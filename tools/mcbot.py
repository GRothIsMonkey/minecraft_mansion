"""A minimal headless Minecraft 1.8 (protocol 47) player for tests, offline mode.

It joins like a real client, stays where the server puts it (answers every
teleport, keep-alive and sends a position every tick), so the server loads
chunks around it exactly as it would for a real player, and it can
right-click blocks (levers, doors, chests...) like a player does.
"""
import socket
import struct
import threading
import time
import zlib


def _varint(n):
    n &= 0xFFFFFFFF
    out = b''
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out += bytes([b | 0x80])
        else:
            return out + bytes([b])


def _read_varint(buf, i=0):
    n = shift = 0
    while True:
        b = buf[i]
        i += 1
        n |= (b & 0x7F) << shift
        if not b & 0x80:
            break
        shift += 7
    if n & 0x80000000:
        n -= 1 << 32
    return n, i


def _string(s):
    b = s.encode('utf-8')
    return _varint(len(b)) + b


def _position(x, y, z):
    x, y, z = int(x), int(y), int(z)
    v = ((x & 0x3FFFFFF) << 38) | ((y & 0xFFF) << 26) | (z & 0x3FFFFFF)
    return struct.pack('>Q', v & 0xFFFFFFFFFFFFFFFF)


class Bot:
    def __init__(self, name='MansionTester', host='127.0.0.1', port=25599):
        self.name, self.host, self.port = name, host, port
        self.threshold = -1
        self.pos = None                # (x, y, z, yaw, pitch)
        self.teleports = 0
        self.lock = threading.Lock()
        self.send_lock = threading.Lock()
        self.events = []               # (time, kind, data)
        self.alive = False
        self.disconnect_reason = None

    # -------------------------------------------------------------- io ------
    def _recv_exact(self, n):
        out = b''
        while len(out) < n:
            c = self.sock.recv(n - len(out))
            if not c:
                raise ConnectionError('closed')
            out += c
        return out

    def _recv_packet(self):
        n = shift = 0
        while True:
            b = self._recv_exact(1)[0]
            n |= (b & 0x7F) << shift
            if not b & 0x80:
                break
            shift += 7
        data = self._recv_exact(n)
        if self.threshold >= 0:
            dlen, i = _read_varint(data)
            data = zlib.decompress(data[i:]) if dlen else data[i:]
        pid, i = _read_varint(data)
        return pid, data[i:]

    def _send(self, pid, payload=b''):
        body = _varint(pid) + payload
        if self.threshold >= 0:
            if len(body) >= self.threshold:
                comp = zlib.compress(body)
                body = _varint(len(body)) + comp
            else:
                body = _varint(0) + body
        with self.send_lock:
            self.sock.sendall(_varint(len(body)) + body)

    # ----------------------------------------------------------- session ----
    def connect(self, timeout=60):
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        self._send(0x00, _varint(47) + _string(self.host) + struct.pack('>H', self.port) + _varint(2))
        self._send(0x00, _string(self.name))
        while True:
            pid, data = self._recv_packet()
            if pid == 0x03:
                self.threshold, _ = _read_varint(data)
            elif pid == 0x02:
                break
            elif pid == 0x00:
                raise ConnectionError('login refused: %r' % data)
        while True:                       # play state starts with Join Game
            pid, data = self._recv_packet()
            if pid == 0x01:
                break
            if pid == 0x40:
                raise ConnectionError('kicked: %r' % data)
        self.sock.settimeout(None)
        self.alive = True
        # client settings (like a vanilla client) then the reader / ticker threads
        self._send(0x15, _string('en_US') + bytes([10, 0, 1, 0x7F]))
        threading.Thread(target=self._reader, daemon=True).start()
        threading.Thread(target=self._ticker, daemon=True).start()
        t0 = time.time()
        while self.pos is None and time.time() - t0 < timeout:
            time.sleep(0.05)
        return self

    def _event(self, kind, data):
        with self.lock:
            self.events.append((time.time(), kind, data))

    def _reader(self):
        try:
            while self.alive:
                pid, d = self._recv_packet()
                if pid == 0x00:                                   # keep alive
                    kid, _ = _read_varint(d)
                    self._send(0x00, _varint(kid))
                elif pid == 0x08:                                 # player position and look
                    x, y, z, yaw, pitch, flags = struct.unpack('>dddffb', d[:33])
                    if self.pos is not None:
                        ox, oy, oz, oyaw, opitch = self.pos
                        x = x + ox if flags & 1 else x
                        y = y + oy if flags & 2 else y
                        z = z + oz if flags & 4 else z
                        yaw = yaw + oyaw if flags & 8 else yaw
                        pitch = pitch + opitch if flags & 16 else pitch
                    self.pos = (x, y, z, yaw, pitch)
                    self._send(0x06, struct.pack('>dddff?', x, y, z, yaw, pitch, False))
                    with self.lock:
                        self.teleports += 1
                    self._event('tp', (x, y, z))
                elif pid == 0x2D:                                 # open window
                    wid = d[0]
                    n, i = _read_varint(d, 1)
                    kind = d[i:i + n].decode('utf-8', 'replace')
                    self._event('window', (wid, kind))
                elif pid == 0x23:                                 # block change
                    (v,) = struct.unpack('>Q', d[:8])
                    x, y, z = v >> 38, (v >> 26) & 0xFFF, v & 0x3FFFFFF
                    if x >= 1 << 25:
                        x -= 1 << 26
                    if z >= 1 << 25:
                        z -= 1 << 26
                    st, _ = _read_varint(d, 8)
                    self._event('block', ((x, y, z), st >> 4, st & 15))
                elif pid == 0x02:                                 # chat
                    n, i = _read_varint(d)
                    self._event('chat', d[i:i + n].decode('utf-8', 'replace'))
                elif pid == 0x06:                                 # health
                    hp = struct.unpack('>f', d[:4])[0]
                    if hp <= 0:
                        self._send(0x16, _varint(0))              # respawn
                        self._event('died', hp)
                elif pid == 0x40:
                    self.disconnect_reason = d.decode('utf-8', 'replace')
                    self.alive = False
        except (ConnectionError, OSError) as e:
            if self.alive:
                self.disconnect_reason = repr(e)
            self.alive = False

    def _ticker(self):
        while self.alive:
            if self.pos is not None:
                x, y, z, _, _ = self.pos
                try:
                    self._send(0x04, struct.pack('>ddd?', x, y, z, False))
                except OSError:
                    self.alive = False
            time.sleep(0.05)

    def close(self):
        self.alive = False
        try:
            self.sock.close()
        except OSError:
            pass

    # ----------------------------------------------------------- actions ----
    def mark(self):
        with self.lock:
            return len(self.events)

    def wait_event(self, kind, since, timeout=5.0, pred=None):
        t0 = time.time()
        while time.time() - t0 < timeout:
            with self.lock:
                for (_, k, d) in self.events[since:]:
                    if k == kind and (pred is None or pred(d)):
                        return d
            time.sleep(0.02)
        return None

    def use_block(self, x, y, z, face=1, sneak=False):
        """Right-click block (x,y,z) with an empty hand, like a player."""
        self._send(0x08, _position(x, y, z) + bytes([face]) + struct.pack('>h', -1) + bytes([8, 8, 8]))
        self._send(0x0A)          # arm swing, like the vanilla client

    def close_window(self, wid):
        self._send(0x0D, bytes([wid]))
