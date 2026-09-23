"""Drive a real vanilla Minecraft 1.8.x dedicated server for testing.

Usage (see test scripts):
    with Server(jar_dir) as s:
        s.cmd('setblock 0 4 0 stone')
        s.wait_ticks(20)
    world = mcworld.World(os.path.join(jar_dir, 'world'))
"""
import os
import re
import shutil
import subprocess
import threading
import time

PROPS = """enable-command-block=true
level-type=FLAT
generator-settings=
online-mode=false
spawn-protection=0
max-tick-time=-1
view-distance=10
spawn-monsters=false
spawn-animals=false
spawn-npcs=false
generate-structures=false
server-port=25599
enable-rcon=false
difficulty=0
gamemode=1
level-seed=mansion
"""


class Server:
    def __init__(self, jar_dir, fresh=True, xmx='3G', props_extra=''):
        self.dir = jar_dir
        self.fresh = fresh
        self.xmx = xmx
        self.props_extra = props_extra
        self.lines = []
        self.lock = threading.Lock()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *a):
        self.stop()

    def start(self):
        if self.fresh:
            shutil.rmtree(os.path.join(self.dir, 'world'), ignore_errors=True)
            tpl = os.path.join(self.dir, 'world_template')
            if os.path.isdir(tpl):
                shutil.copytree(tpl, os.path.join(self.dir, 'world'))
        with open(os.path.join(self.dir, 'eula.txt'), 'w') as fh:
            fh.write('eula=true\n')
        with open(os.path.join(self.dir, 'server.properties'), 'w') as fh:
            fh.write(PROPS + self.props_extra)
        self.p = subprocess.Popen(
            ['java', '-Xmx' + self.xmx, '-Xss4M', '-jar', 'server.jar', 'nogui'],
            cwd=self.dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, bufsize=1)
        self.t = threading.Thread(target=self._reader, daemon=True)
        self.t.start()
        self.wait_for(r'Done \(', 120)

    def _reader(self):
        for line in self.p.stdout:
            with self.lock:
                self.lines.append(line.rstrip('\n'))

    def mark(self):
        with self.lock:
            return len(self.lines)

    def since(self, m):
        with self.lock:
            return list(self.lines[m:])

    def wait_for(self, pattern, timeout=60, start=0):
        rx = re.compile(pattern)
        t0 = time.time()
        while time.time() - t0 < timeout:
            with self.lock:
                for ln in self.lines[start:]:
                    if rx.search(ln):
                        return ln
            if self.p.poll() is not None:
                raise RuntimeError('server exited:\n' + '\n'.join(self.lines[-40:]))
            time.sleep(0.05)
        raise TimeoutError('timeout waiting for %r\n%s' % (pattern, '\n'.join(self.lines[-40:])))

    def cmd(self, c):
        self.p.stdin.write(c + '\n')
        self.p.stdin.flush()

    def sync(self, timeout=600):
        """Block until the server thread has processed everything queued so far."""
        tag = 'sync%d' % time.time_ns()
        m = self.mark()
        self.cmd('say ' + tag)
        self.wait_for(tag, timeout, start=m)

    def wait_ticks(self, n):
        # Relies on the server keeping up (20 TPS); sync afterwards.
        time.sleep(n / 20.0)
        self.sync()

    def stop(self):
        if self.p.poll() is None:
            self.cmd('save-all')
            self.cmd('stop')
            try:
                self.p.wait(120)
            except subprocess.TimeoutExpired:
                self.p.kill()
