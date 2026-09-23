"""Real vanilla 1.8 test/profile: frozen base install, then the Astra patch.

python3 astra_test.py SERVER flat --profile
python3 astra_test.py SERVER flat
python3 astra_test.py SERVER terrain --no-functional

Uses the existing world-diff, navigation, lighting and protocol-47 functional
test harness unchanged. Only temporary worlds inside SERVER are replaced.
"""
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import astra_build as A
import astra_design as D
import console_build as CB
import console_test as CT
import rotation as R
from mcserver import Server
from mcbot import Bot


def run(server_dir,kind,profile=False,functional=True):
    base,b = D.assemble()
    CT.RESULTS.clear()
    base_stages = CT.install(server_dir,kind)
    CT.res('all 24 frozen base stages completed',len(base_stages)-1 == 24)
    if any(not r[1] for r in CT.RESULTS):
        raise RuntimeError('Base installation failed; refusing to profile or test the patch')
    def inventories():
        world,_,box=CT.world_frame(server_dir)
        return {(t['x'],t['y'],t['z']):t['Items'] for t in world.tile_entities(*box) if 'Items' in t}
    before_inventory=inventories() if not profile else None
    costs,stages = {},[]
    s = Server(server_dir,fresh=False,props_extra=CT.props(kind))
    s.start()
    bot = None
    try:
        bot = Bot(CT.BOT,port=CT.PORT).connect()
        x,y,z = CB.STAND
        s.cmd('tp %s %.1f %d %.1f' % (CT.BOT,x+.5,y,z+.5))
        s.wait_ticks(160)
        if profile:
            overhead=[]
            for _ in range(20):
                t=time.monotonic(); s.sync(); overhead.append(time.monotonic()-t)
            overhead=sorted(overhead)[len(overhead)//2]
            s.cmd('gamerule logAdminCommands false')
            for i,c in enumerate(b.cmds[b.astra_start:]):
                t=time.monotonic(); s.cmd(c.text); s.sync()
                costs[A.key(c.text)]=round(max(0.005,time.monotonic()-t-overhead),4)
                if i%100==0:
                    print('profiled %d commands' % i,flush=True)
            s.cmd('gamerule logAdminCommands true')
            A.COSTS.write_text(json.dumps({'note':'Every Astra command measured on vanilla 1.8.9 after base install; seconds minus median sync overhead, minimum 0.005s.',
                'command_count':len(b.cmds)-b.astra_start,'costs':costs},indent=1,sort_keys=True)+'\n')
        else:
            manifest=json.loads((A.ROOT/'commands_astra/manifest.json').read_text())
            files=[]
            for row in manifest['stages']:
                data=(A.ROOT/'commands_astra'/row['file']).read_bytes()
                assert hashlib.sha256(data).hexdigest()==row['sha256']
                files.append((row,data.decode().strip()))
            for row,text in files:
                m=s.mark(); t=time.monotonic(); s.cmd(text)
                msg=s.wait_for(re.escape(row['expect']),180,m)
                s.wait_ticks(20)
                errors=[ln for ln in s.since(m) if re.search(r'Exception|ERROR|Cannot|out of the world|failed',ln)]
                stages.append({'file':row['file'],'secs':round(time.monotonic()-t,3),'chars':len(text),'errors':errors,'message':msg})
                print(row['file'],stages[-1]['secs'],'seconds',flush=True)
            CT.res('all shipped Astra stages completed without console errors',len(stages)==len(files) and not any(st['errors'] for st in stages))
            # Repeat a patch stage and execute the documented scoped cleanup.
            s.cmd(CB.setup_command()); s.sync()
            row,text=files[1]
            m=s.mark(); s.cmd(text); s.wait_for(re.escape(row['expect']),180,m)
            s.wait_ticks(20)
            for c in A.cleanup_commands():
                s.cmd(c)
            s.sync()
            CT.res('recovery drill repeated an Astra stage and ran scoped cleanup',True)
        s.wait_ticks(200)
        if not profile:
            m=s.mark()
            s.cmd('gamerule commandBlockOutput'); s.cmd('gamerule logAdminCommands'); s.sync()
            settings=[ln.split(']: ',1)[-1] for ln in s.since(m)
                      if 'commandBlockOutput' in ln or 'logAdminCommands' in ln]
            CT.res('Astra completion and recovery restore documented gamerules',
                   settings==['commandBlockOutput = true','logAdminCommands = true'],str(settings))
        CT.res('test player remained connected throughout the patch',bot.alive,str(bot.disconnect_reason))
        errors=[ln for ln in s.lines if re.search(r'Exception|ERROR|Watchdog|crash',ln)]
        CT.res('no server exceptions or watchdog during Astra pass',not errors,str(errors[:3]))
    finally:
        if bot: bot.close()
        s.stop()
    if profile:
        print('PROFILE: %d commands, %.3fs measured work, max %.3fs' % (len(costs),sum(costs.values()),max(costs.values())),flush=True)
        return True
    F=R.rotated_frame(b)
    CT.res('all saved inventory contents match the pre-patch world',inventories()==before_inventory,
           '%d inventory tile entities' % len(before_inventory))
    CT.verify_world(server_dir,b,F,kind)
    if functional:
        CT.functional(server_dir,kind,F)
    results=CT.RESULTS
    version=re.search(r'server version ([^\s]+)',(Path(server_dir)/'logs/latest.log').read_text()).group(1)
    report={'server_version':version,'server_jar_sha1':hashlib.sha1((Path(server_dir)/'server.jar').read_bytes()).hexdigest(),
            'kind':kind,'base_commit':'082e475081c6f5137e908f38d4b526e572148454',
            'patch_sha256':hashlib.sha256((A.ROOT/'commands_astra/manifest.json').read_bytes()).hexdigest(),
            'base_stages':base_stages,'astra_stages':stages,'results':results}
    out=A.ROOT/'docs/astra_tests'; out.mkdir(exist_ok=True)
    (out/(Path(server_dir).name+'_'+kind+'.json')).write_text(json.dumps(report,indent=1)+'\n')
    fails=[r for r in results if not r[1]]
    print('ASTRA SERVER RESULT: %d passed, %d failed' % (len(results)-len(fails),len(fails)),flush=True)
    return not fails


if __name__=='__main__':
    sys.exit(0 if run(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else 'flat',
                     '--profile' in sys.argv,'--no-functional' not in sys.argv) else 1)
