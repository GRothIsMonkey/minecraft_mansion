"""Real-server test of the AshgroveManor plugin on Spigot 1.8.8.

    python3 plugin_test.py <spigot-dir> [flat|terrain] [--no-functional] [--crash]

<spigot-dir> holds server.jar = a Spigot 1.8.8 jar built by BuildTools (--rev 1.8.8).
Set MC_JAVA to choose the Java that runs it (for example a Java 8 JDK).

  1. Fresh world (flat, grass at Y 72; or generated hilly terrain), world spawn far away,
     and NO player online: the plugin must keep its own chunks loaded.
  2. Copies AshgroveManor-*.jar into plugins/, starts the server, types into the console
     exactly what CONSOLE/PLUGIN_INSTALL.md says: 'mansion build', then 'mansion confirm'.
     With --crash the server is killed (kill -9) at about 40 %, restarted, and the build is
     finished with 'mansion resume'.
  3. Waits for "Mansion construction complete." and the plugin's own block-by-block check.
  4. Stops the server and runs the same world checks as the console-edition test against the
     FINAL Claude + Astra model: every block, paintings / item frame / armor stands, no
     installer leftovers, and the design validators on the blocks read back from the world.
  5. Optionally restarts with a headless player that clicks every mechanism.
"""
import glob
import json
import os
import re
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import astra_design as D               # noqa: E402
import console_test as CT              # noqa: E402
import rotation as R                   # noqa: E402
from mcserver import Server            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def props(kind):
    # MC_EXTRA_PROPS, e.g. 'enable-command-block=false', is appended last (later keys win)
    return CT.props(kind) + os.environ.get('MC_EXTRA_PROPS', '').replace(';', '\n') + '\n'


def install_plugin(server_dir):
    plugins = os.path.join(server_dir, 'plugins')
    os.makedirs(plugins, exist_ok=True)
    for f in glob.glob(os.path.join(plugins, 'AshgroveManor*.jar')):
        os.remove(f)
    shutil.rmtree(os.path.join(plugins, 'AshgroveManor'), ignore_errors=True)
    jar = sorted(glob.glob(os.path.join(ROOT, 'AshgroveManor-*.jar')))[-1]
    shutil.copy(jar, plugins)
    return os.path.basename(jar)


def build(server_dir, kind, crash=False):
    tpl = CT.template(server_dir, kind)
    for d in ('world', 'world_nether', 'world_the_end'):
        shutil.rmtree(os.path.join(server_dir, d), ignore_errors=True)
    shutil.copytree(tpl, os.path.join(server_dir, 'world'))
    jar = install_plugin(server_dir)
    out = {'jar': jar}
    s = Server(server_dir, fresh=False, props_extra=props(kind))
    s.start()
    try:
        ver = [l for l in s.lines if 'This server is running' in l or 'server version' in l]
        out['server'] = ver[-1].split(']: ', 1)[-1] if ver else '?'
        loaded = [l for l in s.lines if 'Ashgrove Manor ready' in l]
        CT.res('plugin loads on the server', bool(loaded), loaded[0].split(']: ', 1)[-1] if loaded else '')
        m = s.mark()
        s.cmd('mansion build')
        s.wait_for(r"Type 'mansion confirm'", 30, m)
        t0 = time.time()
        m = s.mark()
        s.cmd('mansion confirm')
        s.wait_for('Building started', 30, m)
        if crash:
            s.wait_for(r'Building\.\.\. .*\((4\d|5\d)%\)', 900, m)
            s.p.kill()                                   # like a host crash: no clean shutdown
            s.p.wait()
            out['crashed_at'] = [l for l in s.lines if 'Building...' in l][-1].split(']: ', 1)[-1]
            s = Server(server_dir, fresh=False, props_extra=props(kind))
            s.start()
            warn = [l for l in s.lines if 'was interrupted' in l]
            CT.res('after the crash the plugin reports the interrupted build', bool(warn),
                   warn[0].split(']: ', 1)[-1] if warn else '')
            m = s.mark()
            t0 = time.time()
            s.cmd('mansion resume')
        s.wait_for('Mansion construction complete', 1800, m)
        out['build_secs'] = round(time.time() - t0, 1)
        line = s.wait_for(r'(OK|DIFFERENCES FOUND): .* built blocks match', 600, m)
        out['plugin_check'] = line.split(']: ', 1)[-1]
        lines = s.since(m)
        out['plugin_log'] = [l.split(']: ', 1)[-1] for l in lines if 'Ashgrove' in l or 'game-made' in l
                             or l.strip().startswith('[') is False]
        out['lag'] = [l.split(']: ', 1)[-1] for l in lines if "Can't keep up" in l]
        out['console_lines_during_build'] = len([l for l in lines if 'sync' not in l])
        CT.res("the plugin's own check reports the design exactly",
               'OK: 348,046 of 348,046 built blocks match the design; paintings 16/16, item frame 1/1, armor stands'
               ' 8/8' in line, out['plugin_check'])
        s.wait_ticks(200)       # let hanging entities re-check and natural cave gravel finish falling
        errs = [l for l in s.lines if re.search(r'Exception|ERROR|SEVERE|Command failed|refused', l)]
        CT.res('no errors or exceptions in the server log', not errs, '; '.join(errs[:3]))
        m = s.mark()
        s.cmd('gamerule commandBlockOutput')
        s.cmd('gamerule logAdminCommands')
        s.cmd('mansion status')
        s.sync()
        gr = [l.split(']: ', 1)[-1] for l in s.since(m)]
        CT.res('gamerules back to their previous values', 'commandBlockOutput = true' in gr
               and 'logAdminCommands = true' in gr, str(gr))
    finally:
        s.stop()
    return out


def main():
    server_dir = sys.argv[1]
    kind = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 'flat'
    crash = '--crash' in sys.argv
    base, b = D.assemble()
    F = R.rotated_frame(b)
    print('== plugin build on %s (%s world%s), no player online' % (server_dir, kind, ', crash + resume'
                                                                     if crash else ''), flush=True)
    info = build(server_dir, kind, crash)
    print('  %s' % json.dumps({k: v for k, v in info.items() if k != 'plugin_log'}), flush=True)
    CT.verify_world(server_dir, b, F, kind)
    if '--no-functional' not in sys.argv:
        CT.functional(server_dir, kind, F)
    fails = [r for r in CT.RESULTS if not r[1]]
    print('\nRESULT: %d passed, %d failed' % (len(CT.RESULTS) - len(fails), len(fails)))
    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
    name = 'plugin_test_%s_%s%s.json' % (os.path.basename(server_dir.rstrip('/')), kind, '_crash' if crash else '')
    info['extra_props'] = os.environ.get('MC_EXTRA_PROPS', '')
    info['java'] = os.environ.get('MC_JAVA', 'java')
    with open(os.path.join(ROOT, 'out', name), 'w') as fh:
        json.dump({'info': info, 'results': CT.RESULTS}, fh, indent=1)
    return not fails


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
