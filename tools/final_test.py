"""Run the exported commands/command_NN.txt files (exactly as shipped) on a real server and diff."""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build        # noqa: E402
import runtest      # noqa: E402
from mansion_base import X0, Z0   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(ROOT, 'commands', 'command_*.txt')))
    pastes = [open(f).read() for f in files]
    errors, times = runtest.run(sys.argv[1], pastes, wait_ticks=100)
    print('server warnings/errors:', errors)
    b = build.assemble()
    runtest.diff(sys.argv[1], b, (X0 - 12, -12, Z0 - 26, X0 + 74, 52, Z0 + 60), max_report=40)
