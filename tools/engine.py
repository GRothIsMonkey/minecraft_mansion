"""Command-generation engine for a Minecraft 1.8.x command-block build.

Coordinates are LOCAL block coordinates relative to the player's command
block, which sits at (0, 0, 0).  Every generated command is executed by a
command-block minecart that sits on an activator rail at (0, 3, 0), so all
commands are written with `~dx ~dy ~dz` offsets from that rail.

Besides producing command text, every builder call is applied to a voxel
model (numpy arrays of block id / metadata) so the finished mansion can be
inspected, rendered and compared block-for-block with a real 1.8 server.
"""
import math
import re

import numpy as np

from blockids import BLOCK_IDS, ID_NAMES

ORIGIN = (0, 3, 0)          # where the command minecarts execute from
FILL_LIMIT = 32768          # /fill and /clone volume limit in 1.8

# Simulation box (local coords, inclusive)
SX0, SX1 = -8, 104
SY0, SY1 = -24, 72
SZ0, SZ1 = -8, 104

N, S, E, W, UP, DOWN = 'N', 'S', 'E', 'W', 'UP', 'DOWN'
DIRV = {N: (0, 0, -1), S: (0, 0, 1), E: (1, 0, 0), W: (-1, 0, 0), UP: (0, 1, 0), DOWN: (0, -1, 0)}
OPP = {N: S, S: N, E: W, W: E, UP: DOWN, DOWN: UP}
CW = {N: E, E: S, S: W, W: N}
CCW = {N: W, W: S, S: E, E: N}
MIRX = {N: N, S: S, E: W, W: E, UP: UP, DOWN: DOWN}


# ------------------------------------------------------------ metadata ------
def stairs(high_side, upside_down=False):
    """Stair metadata; `high_side` is the side of the tall back (walk that way to go up)."""
    return {E: 0, W: 1, S: 2, N: 3}[high_side] + (4 if upside_down else 0)


def door_lower(facing, open_=False):
    """`facing` = direction a player looks when walking through from the placing side."""
    return {E: 0, S: 1, W: 2, N: 3}[facing] + (4 if open_ else 0)


def door_upper(hinge_right=False):
    return 8 + (1 if hinge_right else 0)


def trapdoor(facing, open_=False, top=False):
    """Trapdoor meta. Support block is on the OPPOSITE side of `facing` (1.8 needs it)."""
    return {N: 0, S: 1, W: 2, E: 3}[facing] + (4 if open_ else 0) + (8 if top else 0)


def torch(facing):
    """Torch pointing `facing` (attached to the block on the opposite side) or UP."""
    return {E: 1, W: 2, S: 3, N: 4, UP: 5}[facing]


def wallmount(facing):
    """ladder / wall_sign / wall_banner / chest / furnace / wall skull / dispenser."""
    return {N: 2, S: 3, W: 4, E: 5}[facing]


def bed(head_dir, head=False):
    return {S: 0, W: 1, N: 2, E: 3}[head_dir] + (8 if head else 0)


def lever(facing, on=False):
    """Wall lever pointing `facing`, or 'floor'/'ceiling'."""
    m = {E: 1, W: 2, S: 3, N: 4, 'floor': 5, 'ceiling': 7}[facing]
    return m + (8 if on else 0)


def button(facing):
    return {DOWN: 0, E: 1, W: 2, S: 3, N: 4, UP: 5}[facing]


def piston(facing, extended=False):
    return {DOWN: 0, UP: 1, N: 2, S: 3, W: 4, E: 5}[facing] + (8 if extended else 0)


def repeater(output_dir, delay=1):
    return {N: 0, E: 1, S: 2, W: 3}[output_dir] + 4 * (delay - 1)


def horiz(facing):
    """fence_gate / pumpkin / lit_pumpkin / end_portal_frame / anvil-ish."""
    return {S: 0, W: 1, N: 2, E: 3}[facing]


def log_axis(axis, wood=0):
    return wood + {'Y': 0, 'X': 4, 'Z': 8, 'ALL': 12}[axis]


# ------------------------------------------------------------ helpers -------
def _rel(v):
    return '~' if v == 0 else '~%d' % v


def _relf(v):
    if abs(v - round(v)) < 1e-9:
        return _rel(int(round(v)))
    s = ('%.5f' % v).rstrip('0').rstrip('.')
    return '~' + s


def _absf(v):
    """Absolute float coordinate.  Always has a '.', because 1.8 adds 0.5 to a bare integer
    x/z in /summon (block centring)."""
    if abs(v - round(v)) < 1e-9:
        return '%d.0' % int(round(v))
    return ('%.5f' % v).rstrip('0')


def nbt_needs_quotes(s):
    return bool(re.search(r'[,{}\[\]":]', s)) or s != s.strip()


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


class Cmd:
    __slots__ = ('text', 'section', 'kind', 'box', 'block', 'dead')

    def __init__(self, text, section, kind='raw', box=None, block=None):
        self.text = text
        self.section = section
        self.kind = kind      # 'set' (setblock/fill, pure block write) or 'raw' (anything else)
        self.box = box        # written region (x1,y1,z1,x2,y2,z2) for 'set'
        self.block = block
        self.dead = False


# ------------------------------------------------------------ builder -------
class Build:
    # World transform for the server-console edition (see rotation.py).  None = legacy
    # output: relative ~ coordinates from the command-block minecart at ORIGIN.  When set,
    # commands are written with ABSOLUTE world coordinates and rotated metadata, while the
    # voxel model (and every design/validation routine that reads it) stays in local coords.
    xf = None

    def __init__(self, terrain=True):
        shape = (SX1 - SX0 + 1, SY1 - SY0 + 1, SZ1 - SZ0 + 1)
        self.ids = np.zeros(shape, dtype=np.int16)
        self.meta = np.zeros(shape, dtype=np.int8)
        self.te = {}          # (x,y,z) -> nbt text
        self.entities = []    # (type, (x,y,z) float, nbt)
        self.cmds = []
        self.section = 'misc'
        self.touched = np.zeros(shape, dtype=bool)
        self.owner = np.full(shape, -1, dtype=np.int32)   # index of the command that wrote each cell last
        self.used = set()                                 # commands whose output was read (clone/keep/replace)
        self.expects = []                                 # cells changed by the game itself (pistons)
        if terrain:
            # Test terrain: grass at y=-1, dirt -4..-2, stone below.
            self._box_set(SX0, SY0, SZ0, SX1, -5, SZ1, BLOCK_IDS['stone'], 0)
            self._box_set(SX0, -4, SZ0, SX1, -2, SZ1, BLOCK_IDS['dirt'], 0)
            self._box_set(SX0, -1, SZ0, SX1, -1, SZ1, BLOCK_IDS['grass'], 0)
            self.touched[:] = False
            self.owner[:] = -1

    # -- voxel helpers -----------------------------------------------------
    def _idx(self, x, y, z):
        return x - SX0, y - SY0, z - SZ0

    def _slc(self, x1, y1, z1, x2, y2, z2):
        return (slice(x1 - SX0, x2 - SX0 + 1), slice(y1 - SY0, y2 - SY0 + 1),
                slice(z1 - SZ0, z2 - SZ0 + 1))

    def _box_set(self, x1, y1, z1, x2, y2, z2, bid, m):
        s = self._slc(x1, y1, z1, x2, y2, z2)
        self.ids[s] = bid
        self.meta[s] = m
        self.touched[s] = True
        self.owner[s] = len(self.cmds) - 1

    def _mark_used(self, s, mask=None):
        o = self.owner[s] if mask is None else self.owner[s][mask]
        self.used.update(int(v) for v in np.unique(o) if v >= 0)

    def get(self, x, y, z):
        i = self._idx(x, y, z)
        return int(self.ids[i]), int(self.meta[i])

    def name_at(self, x, y, z):
        return ID_NAMES[self.get(x, y, z)[0]]

    def _clear_te(self, x1, y1, z1, x2, y2, z2, mask=None):
        for k in list(self.te):
            if x1 <= k[0] <= x2 and y1 <= k[1] <= y2 and z1 <= k[2] <= z2:
                if mask is None or mask[k[0] - x1, k[1] - y1, k[2] - z1]:
                    del self.te[k]

    # -- command emission --------------------------------------------------
    def emit(self, text, kind='raw', box=None, block=None):
        self.cmds.append(Cmd(text, self.section, kind, box, block))

    @staticmethod
    def rel(x, y, z):
        return '%s %s %s' % (_rel(x - ORIGIN[0]), _rel(y - ORIGIN[1]), _rel(z - ORIGIN[2]))

    def pos(self, x, y, z):
        """Block position text: relative (legacy) or absolute world (console edition)."""
        if self.xf is None:
            return self.rel(x, y, z)
        return '%d %d %d' % self.xf.block(x, y, z)

    def wmeta(self, block, meta):
        return meta if self.xf is None else self.xf.rot_meta(block, meta)

    def wnbt(self, block, meta, nbt):
        return nbt if self.xf is None else self.xf.rot_nbt(block, meta, nbt)

    def prekill(self, entity, wx, wy, wz, dy=0):
        """Console edition: remove an earlier copy first, so a repeated stage never duplicates."""
        self.emit('kill @e[type=%s,x=%d,y=%d,z=%d,dx=0,dy=%d,dz=0]' % (entity, wx, wy, wz, dy))

    # -- builders ----------------------------------------------------------
    def setblock(self, x, y, z, block, meta=0, nbt=None):
        bid = BLOCK_IDS[block]
        wm, wn = self.wmeta(block, meta), self.wnbt(block, meta, nbt)
        t = 'setblock %s %s' % (self.pos(x, y, z), block)
        if wm or wn:
            t += ' %d' % wm
        if wn:
            t += ' replace ' + wn
        self.emit(t, 'set', (x, y, z, x, y, z), block)
        self._clear_te(x, y, z, x, y, z)
        self._box_set(x, y, z, x, y, z, bid, meta)
        if nbt:
            self.te[(x, y, z)] = nbt

    def fill(self, x1, y1, z1, x2, y2, z2, block, meta=0, mode=None, rblock=None, rmeta=None, nbt=None):
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        z1, z2 = min(z1, z2), max(z1, z2)
        vol = (x2 - x1 + 1) * (y2 - y1 + 1) * (z2 - z1 + 1)
        if vol > FILL_LIMIT:
            if mode in ('hollow', 'outline'):
                raise ValueError('cannot split hollow/outline fill')
            # split along the longest axis
            dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
            if dy >= dx and dy >= dz:
                m = (y1 + y2) // 2
                self.fill(x1, y1, z1, x2, m, z2, block, meta, mode, rblock, rmeta, nbt)
                self.fill(x1, m + 1, z1, x2, y2, z2, block, meta, mode, rblock, rmeta, nbt)
            elif dx >= dz:
                m = (x1 + x2) // 2
                self.fill(x1, y1, z1, m, y2, z2, block, meta, mode, rblock, rmeta, nbt)
                self.fill(m + 1, y1, z1, x2, y2, z2, block, meta, mode, rblock, rmeta, nbt)
            else:
                m = (z1 + z2) // 2
                self.fill(x1, y1, z1, x2, y2, m, block, meta, mode, rblock, rmeta, nbt)
                self.fill(x1, y1, m + 1, x2, y2, z2, block, meta, mode, rblock, rmeta, nbt)
            return
        bid = BLOCK_IDS[block]
        wm = self.wmeta(block, meta)
        t = 'fill %s %s %s' % (self.pos(x1, y1, z1), self.pos(x2, y2, z2), block)
        if mode == 'replace' and rblock is not None:
            t += ' %d replace %s' % (wm, rblock)
            if rmeta is not None:
                t += ' %d' % self.wmeta(rblock, rmeta)
        elif mode:
            t += ' %d %s' % (wm, mode)
            if nbt:
                t += ' ' + self.wnbt(block, meta, nbt)
        elif wm:
            t += ' %d' % wm
        pure = mode is None or (mode == 'replace' and rblock is None) or mode == 'hollow'
        self.emit(t, 'set' if pure else 'raw', (x1, y1, z1, x2, y2, z2), block)
        me = len(self.cmds) - 1
        s = self._slc(x1, y1, z1, x2, y2, z2)
        if not pure:
            self._mark_used(s)
        if mode is None or mode == 'destroy' or (mode == 'replace' and rblock is None):
            self._clear_te(x1, y1, z1, x2, y2, z2)
            self.ids[s] = bid
            self.meta[s] = meta
            self.touched[s] = True
            self.owner[s] = me
            if nbt:
                for xx in range(x1, x2 + 1):
                    for yy in range(y1, y2 + 1):
                        for zz in range(z1, z2 + 1):
                            self.te[(xx, yy, zz)] = nbt
        elif mode == 'keep':
            mask = self.ids[s] == 0
            self.ids[s][mask] = bid
            self.meta[s][mask] = meta
            self.touched[s][mask] = True
            self.owner[s][mask] = me
        elif mode == 'replace':
            mask = self.ids[s] == BLOCK_IDS[rblock]
            if rmeta is not None:
                mask &= self.meta[s] == rmeta
            self._clear_te(x1, y1, z1, x2, y2, z2, mask)
            self.ids[s][mask] = bid
            self.meta[s][mask] = meta
            self.touched[s][mask] = True
            self.owner[s][mask] = me
        elif mode in ('hollow', 'outline'):
            shell = np.ones((x2 - x1 + 1, y2 - y1 + 1, z2 - z1 + 1), dtype=bool)
            shell[1:-1, 1:-1, 1:-1] = False
            if mode == 'hollow':
                self._clear_te(x1, y1, z1, x2, y2, z2)
                self.ids[s] = 0
                self.meta[s] = 0
                self.touched[s] = True
                self.owner[s] = me
            else:
                self._clear_te(x1, y1, z1, x2, y2, z2, shell)
            self.ids[s][shell] = bid
            self.meta[s][shell] = meta
            self.touched[s][shell] = True
            self.owner[s][shell] = me
        else:
            raise ValueError(mode)

    def clone(self, x1, y1, z1, x2, y2, z2, dx, dy, dz, mask='replace'):
        """Copy box to destination whose min corner is (dx,dy,dz)."""
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        z1, z2 = min(z1, z2), max(z1, z2)
        vol = (x2 - x1 + 1) * (y2 - y1 + 1) * (z2 - z1 + 1)
        assert vol <= FILL_LIMIT, 'clone too big'
        sx, sy, sz = x2 - x1, y2 - y1, z2 - z1
        # overlap check
        ov = not (dx > x2 or dx + sx < x1 or dy > y2 or dy + sy < y1 or dz > z2 or dz + sz < z1)
        if self.xf is None:
            t = 'clone %s %s %s' % (self.rel(x1, y1, z1), self.rel(x2, y2, z2), self.rel(dx, dy, dz))
        else:
            # /clone's destination is the MIN corner of the target box; after the turn that
            # corner comes from a different corner of the local box.
            d = self.xf.box(dx, dy, dz, dx + sx, dy + sy, dz + sz)
            t = 'clone %s %s %d %d %d' % (self.pos(x1, y1, z1), self.pos(x2, y2, z2), d[0], d[1], d[2])
        if mask != 'replace' or ov:
            t += ' ' + mask
        if ov:
            t += ' force'
        self.emit(t, 'raw', (dx, dy, dz, dx + sx, dy + sy, dz + sz))
        me = len(self.cmds) - 1
        src = self._slc(x1, y1, z1, x2, y2, z2)
        dst = self._slc(dx, dy, dz, dx + sx, dy + sy, dz + sz)
        self._mark_used(src)
        sid = self.ids[src].copy()
        sme = self.meta[src].copy()
        ste = {k: v for k, v in self.te.items()
               if x1 <= k[0] <= x2 and y1 <= k[1] <= y2 and z1 <= k[2] <= z2}
        if mask == 'masked':
            m = sid != 0
            self._clear_te(dx, dy, dz, dx + sx, dy + sy, dz + sz, m)
            self.ids[dst][m] = sid[m]
            self.meta[dst][m] = sme[m]
            self.touched[dst][m] = True
            self.owner[dst][m] = me
        else:
            self._clear_te(dx, dy, dz, dx + sx, dy + sy, dz + sz)
            self.ids[dst] = sid
            self.meta[dst] = sme
            self.touched[dst] = True
            self.owner[dst] = me
        for (kx, ky, kz), v in ste.items():
            self.te[(kx - x1 + dx, ky - y1 + dy, kz - z1 + dz)] = v

    def summon(self, entity, fx, fy, fz, nbt=None, hang=None):
        """Summon at exact float coordinates (local). Minecart sits at +0.5,+0.0625,+0.5.

        `hang` = the hanging block of a painting / item frame (local), used by the console
        edition to clear an earlier copy before summoning."""
        if self.xf is None:
            ox, oy, oz = ORIGIN[0] + 0.5, ORIGIN[1] + 0.0625, ORIGIN[2] + 0.5
            t = 'summon %s %s %s %s' % (entity, _relf(fx - ox), _relf(fy - oy), _relf(fz - oz))
            if nbt:
                t += ' ' + nbt
        else:
            px, py, pz = self.xf.point(fx, fy, fz)
            if hang is not None:
                self.prekill(entity, *self.xf.block(*hang))
            elif entity == 'ArmorStand':
                self.prekill(entity, int(math.floor(px)), int(math.floor(py)), int(math.floor(pz)), dy=1)
            t = 'summon %s %s %s %s' % (entity, _absf(px), _absf(py), _absf(pz))
            nbt = self.xf.rot_entity_nbt(entity, nbt)
            if nbt:
                t += ' ' + nbt
        self.emit(t)
        self.entities.append((entity, (fx, fy, fz), nbt))

    def painting(self, hx, hy, hz, facing, motive, w=1, h=1):
        """Hang a painting whose hanging block is (hx,hy,hz) (the air block in front of the wall).

        1.8 EntityPainting.setLocationAndAngles maps a target T to hanging
        floor(T - c) where c is the painting centre offset; choose T so that
        T - c lands in the middle of the wanted block.
        """
        if self.xf is not None:
            # Console edition: work the formula out in WORLD space (world hanging block,
            # turned facing).  Rotating the local target point instead is off by one block,
            # because the +0.5 block-centre terms do not turn with the painting.
            wx, wy, wz = self.xf.block(hx, hy, hz)
            wf = self.xf.CW[facing]
            tx, ty, tz = self._painting_target(wx, wy, wz, wf, w, h)
            self.prekill('Painting', wx, wy, wz)
            self.emit('summon Painting %s %s %s {Motive:%s,Facing:%d}' % (
                _absf(tx), _absf(ty), _absf(tz), motive, {S: 0, W: 1, N: 2, E: 3}[wf]))
        else:
            tx, ty, tz = self._painting_target(hx, hy, hz, facing, w, h)
            fidx = {S: 0, W: 1, N: 2, E: 3}[facing]
            self.summon('Painting', tx, ty, tz, '{Motive:%s,Facing:%d}' % (motive, fidx))
            self.entities.pop()
        self.entities.append(('Painting', (hx, hy, hz), (motive, facing, w, h)))

    @staticmethod
    def _painting_target(hx, hy, hz, facing, w, h):
        fdx, _, fdz = DIRV[facing]
        ccw = DIRV[CCW[facing]]
        ws = 0.5 if (w * 16) % 32 == 0 else 0.0
        hs = 0.5 if (h * 16) % 32 == 0 else 0.0
        cx = 0.5 - fdx * 0.46875 + ws * ccw[0]
        cy = 0.5 + hs
        cz = 0.5 - fdz * 0.46875 + ws * ccw[2]
        return hx + 0.5 + cx, hy + 0.5 + cy, hz + 0.5 + cz

    def raw(self, text):
        self.emit(text)

    def expect(self, x, y, z, block, meta=0):
        """Update the model only (for block changes the game makes by itself, e.g. pistons)."""
        o = int(self.owner[self._idx(x, y, z)])
        self.used.add(o)
        self.expects.append((x, y, z))
        self._box_set(x, y, z, x, y, z, BLOCK_IDS[block], meta)
        self.owner[self._idx(x, y, z)] = o
