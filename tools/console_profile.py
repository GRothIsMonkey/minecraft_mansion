"""Measure how long every build command takes on a real 1.8 server (for stage packing).

    MC_PORT=25600 python3 console_profile.py <server-dir>

Runs the whole console-edition build one command at a time from the console (a test
player at the stand point keeps the chunks loaded) and records the wall time of every
command that takes 50 ms or more in console_costs.json, keyed by a hash of its text.
console_build.pack() uses these costs to spread the expensive commands (mostly the big
hollow shells, whose lighting updates are slow) over several stages, so that no stage
freezes the server for long.
"""
import hashlib
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import console_build as CB     # noqa: E402
import console_test as CT      # noqa: E402
from mcserver import Server    # noqa: E402
from mcbot import Bot          # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'console_costs.json')


def key(text):
    return hashlib.sha1(text.encode()).hexdigest()[:16]


def main(server_dir):
    b = CB.assemble()
    tpl = CT.template(server_dir, 'flat')
    shutil.rmtree(os.path.join(server_dir, 'world'), ignore_errors=True)
    shutil.copytree(tpl, os.path.join(server_dir, 'world'))
    s = Server(server_dir, fresh=False, props_extra=CT.props('flat'))
    s.start()
    costs = {}
    try:
        bot = Bot('Profiler', port=CT.PORT).connect()
        sx, sy, sz = CB.STAND
        s.cmd('tp Profiler %.1f %d %.1f' % (sx + 0.5, sy, sz + 0.5))
        time.sleep(6)
        s.cmd('gamerule logAdminCommands false')
        s.sync()
        base = []
        for _ in range(20):                       # round-trip overhead of one console sync
            t0 = time.time()
            s.sync()
            base.append(time.time() - t0)
        over = sorted(base)[len(base) // 2]
        for i, c in enumerate(b.cmds):
            t0 = time.time()
            s.cmd(c.text)
            s.sync()
            dt = time.time() - t0 - over
            if dt >= 0.05:
                costs[key(c.text)] = round(dt, 3)
        bot.close()
    finally:
        s.stop()
    with open(OUT, 'w') as fh:
        json.dump({'note': 'seconds per command on the test machine (vanilla 1.8.9), >= 50 ms only',
                   'costs': costs}, fh, indent=0, sort_keys=True)
    top = sorted(costs.values(), reverse=True)
    print('%d costly commands, total %.1fs, top %s' % (len(costs), sum(top), top[:10]))


if __name__ == '__main__':
    main(sys.argv[1])
