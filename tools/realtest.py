"""Pack the current build, run every paste on a real server, diff world vs model."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build                 # noqa: E402
import packer                # noqa: E402
import runtest               # noqa: E402
from mansion_base import X0, Z0   # noqa: E402


def message(k, total, final):
    if final:
        return ('{"text":"","extra":[{"text":"[Mansion] ","color":"gold","bold":true},'
                '{"text":"Stage %d/%d complete - the mansion is finished! Enjoy exploring.","color":"green"}]}'
                % (k, total))
    return ('{"text":"","extra":[{"text":"[Mansion] ","color":"gold","bold":true},'
            '{"text":"Stage %d/%d complete. ","color":"green"},'
            '{"text":"Now paste Command %d into the same command block and press the button.","color":"yellow"}]}'
            % (k, total, k + 1))


def main(server_dir, stop_after=None):
    b = build.assemble()
    cmds = [c.text for c in b.cmds]
    pastes = packer.pack(cmds, message)
    print('commands %d -> %d pastes, sizes %s' % (len(cmds), len(pastes), [len(p) for p, _ in pastes]))
    if stop_after:
        pastes = pastes[:stop_after]
    t0 = time.time()
    errors, times = runtest.run(server_dir, [p for p, _ in pastes], wait_ticks=100)
    print('server errors:', errors[:10])
    print('elapsed %.1fs' % (time.time() - t0))
    box = (X0 - 12, -8, Z0 - 26, X0 + 74, 52, Z0 + 60)
    bad, ids, metas, w = runtest.diff(server_dir, b, box, max_report=80)
    return b, bad, w


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else None)
