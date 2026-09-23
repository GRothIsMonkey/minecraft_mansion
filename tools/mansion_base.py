"""Shared base for the mansion design: coordinate offsets, symmetry helpers, palette."""
from engine import Build, stairs, trapdoor, torch, wallmount, door_lower, door_upper, bed, horiz
from engine import N, S, E, W, UP, DOWN, MIRX, OPP, CW, CCW, DIRV

# Mansion coordinates (mx, y, mz) -> local = (mx + X0, y, mz + Z0)
# The player's command block is local (0,0,0) = mansion (-12, 0, -26).
X0, Z0 = 12, 26
AXIS = 61          # the design is mirror-symmetric about mx = 30.5  (mx <-> 61 - mx)

# Vertical levels (y relative to the command block; ground surface y=-1)
BF, B_TOP, B_CEIL = -5, 0, 1           # basement floor block, top air, ceiling layer
F1, F1_TOP, F1_CEIL = 2, 8, 9           # F1 floor block y=2, air 3..8, ceiling layer 9
F2, F2_TOP, F2_CEIL = 10, 15, 16
F3, F3_TOP, F3_CEIL = 17, 22, 23
EAVE = 24

# palette -------------------------------------------------------------------
WALL = ('stonebrick', 0)
CHISEL = ('stonebrick', 3)
MOSSY = ('stonebrick', 1)
CRACK = ('stonebrick', 2)
PLASTER = ('stained_hardened_clay', 0)
TIMBER_Y = ('log2', 1)
TIMBER_X = ('log2', 5)
TIMBER_Z = ('log2', 9)
ROOF = 'dark_oak_stairs'
ROOF_SLAB = ('wooden_slab', 5)
ROOF_SLAB_TOP = ('wooden_slab', 13)
ROOF_FILL = ('planks', 5)
DO_PLANK = ('planks', 5)
OAK_PLANK = ('planks', 0)
SPRUCE_PLANK = ('planks', 1)
BIRCH_PLANK = ('planks', 2)
QUARTZ = ('quartz_block', 0)
QPILLAR = ('quartz_block', 2)
GLOW = ('glowstone', 0)


class T:
    """Transform for symmetric features: identity or mirror about mx=30.5."""

    def __init__(self, mirror=False):
        self.m = mirror

    def x(self, mx):
        return AXIS - mx if self.m else mx

    def xs(self, a, b):
        a2, b2 = self.x(a), self.x(b)
        return (min(a2, b2), max(a2, b2))

    def d(self, direction):
        return MIRX[direction] if self.m else direction

    def hinge_right(self, right):
        # mirroring swaps left/right hinges
        return (not right) if self.m else right


ID = T(False)
MI = T(True)
BOTH = (ID, MI)


class MB(Build):
    """Build that takes mansion coordinates."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.fires = []            # fire positions, lit at the very end
        self.water = []            # water boxes, poured at the very end
        self.late_paintings = []   # paintings hung after all blocks exist
        self.late_frames = []      # item frames (x, y, z, facing, item)
        self._door_tpl = {}        # (blk, lower, upper) -> a placed leaf we can /clone from

    def F(self, x1, y1, z1, x2, y2, z2, blk, meta=0, **kw):
        if isinstance(blk, tuple):
            blk, meta = blk
        self.fill(x1 + X0, y1, z1 + Z0, x2 + X0, y2, z2 + Z0, blk, meta, **kw)

    def S(self, x, y, z, blk, meta=0, nbt=None):
        if isinstance(blk, tuple):
            blk, meta = blk
        self.setblock(x + X0, y, z + Z0, blk, meta, nbt)

    def C(self, x1, y1, z1, x2, y2, z2, dx, dy, dz, mask='replace'):
        self.clone(x1 + X0, y1, z1 + Z0, x2 + X0, y2, z2 + Z0, dx + X0, dy, dz + Z0, mask)

    def P(self, hx, hy, hz, facing, motive, w=1, h=1):
        self.painting(hx + X0, hy, hz + Z0, facing, motive, w, h)

    def FRAME(self, hx, hy, hz, facing, item):
        """Item frame hanging in block (hx,hy,hz) on the wall behind it (1.8: hanging = floor(pos))."""
        fidx = {S: 0, W: 1, N: 2, E: 3}[facing]
        self.summon('ItemFrame', hx + X0 + 0.5, hy + 0.0625, hz + Z0 + 0.5,
                    '{Facing:%d,Item:{id:%s,Count:1b}}' % (fidx, item))
        self.entities[-1] = ('ItemFrame', (hx + X0, hy, hz + Z0), (item, facing))

    def SUM(self, entity, fx, fy, fz, nbt=None):
        self.summon(entity, fx + X0, fy, fz + Z0, nbt)

    def X(self, x, y, z, blk, meta=0):
        """Expected game-side result (no command emitted)."""
        self.expect(x + X0, y, z + Z0, blk, meta)

    def G(self, x, y, z):
        return self.get(x + X0, y, z + Z0)

    # -- symmetric helpers (t = transform) --------------------------------
    def tF(self, t, x1, y1, z1, x2, y2, z2, blk, meta=0, **kw):
        a, b = t.xs(x1, x2)
        self.F(a, y1, z1, b, y2, z2, blk, meta, **kw)

    def tS(self, t, x, y, z, blk, meta=0, nbt=None):
        self.S(t.x(x), y, z, blk, meta, nbt)

    # -- common furniture/fixtures ----------------------------------------
    def door(self, x, y, z, facing, blk='dark_oak_door', hinge_right=False, t=ID):
        """Single door; lower half at (x,y,z)."""
        f = t.d(facing)
        self.leaf(t.x(x), y, z, blk, door_lower(f), door_upper(t.hinge_right(hinge_right)))

    def leaf(self, x, y, z, blk, lower, upper):
        """One door leaf.  Both halves go in back-to-back (a lone lower half is deleted by the
        next neighbour update); repeats of an identical leaf are one /clone of an earlier one."""
        from blockids import BLOCK_IDS
        key = (blk, lower, upper)
        bid = BLOCK_IDS[blk]
        tpl = self._door_tpl.get(key)
        if tpl and self.G(*tpl) == (bid, lower) and self.G(tpl[0], tpl[1] + 1, tpl[2]) == (bid, upper) \
                and tpl != (x, y, z):
            tx, ty, tz = tpl
            self.C(tx, ty, tz, tx, ty + 1, tz, x, y, z)
            return
        self.S(x, y, z, blk, lower)
        self.S(x, y + 1, z, blk, upper)
        self._door_tpl[key] = (x, y, z)

    def double_door(self, xa, y, za, xb, zb, facing, blk='dark_oak_door', t=ID):
        """Double door on two adjacent cells; hinges mirrored so both leaves swing apart.

        `facing` = the direction a person looks when walking through from the
        side the door was 'placed' from.  The leaf on that person's left gets the
        left hinge, the other the right hinge (matches vanilla ItemDoor logic).
        """
        f = t.d(facing)
        ax, bx = t.x(xa), t.x(xb)
        lv = DIRV[CCW[f]]
        if ax * lv[0] + za * lv[2] > bx * lv[0] + zb * lv[2]:
            (lx, lz), (rx, rz) = (ax, za), (bx, zb)
        else:
            (lx, lz), (rx, rz) = (bx, zb), (ax, za)
        # each leaf's two halves must be placed back-to-back: in 1.8 a lower half
        # without its upper half is deleted as soon as a neighbour updates it
        self.leaf(lx, y, lz, blk, door_lower(f), door_upper(False))
        self.leaf(rx, y, rz, blk, door_lower(f), door_upper(True))


class Face:
    """A vertical exterior wall plane.

    axis='x': wall at x=wall, runs along z.  axis='z': wall at z=wall, runs along x.
    out: outward direction (N/S/E/W).  depth 0 = wall plane, 1 = outside, -1 = inside.
    """

    def __init__(self, axis, wall, out):
        self.axis, self.wall, self.out = axis, wall, out
        self.sign = DIRV[out][0] if axis == 'x' else DIRV[out][2]

    def xz(self, a, depth=0):
        w = self.wall + depth * self.sign
        return (w, a) if self.axis == 'x' else (a, w)

    def box(self, b, a1, y1, d1, a2, y2, d2, blk, meta=0, **kw):
        x1, z1 = self.xz(a1, d1)
        x2, z2 = self.xz(a2, d2)
        b.F(x1, y1, z1, x2, y2, z2, blk, meta, **kw)

    def set(self, b, a, y, d, blk, meta=0, nbt=None):
        x, z = self.xz(a, d)
        b.S(x, y, z, blk, meta, nbt)

    def clone(self, b, a1, y1, a2, y2, d1, d2, a_dst, y_dst=None, mask='masked'):
        x1, z1 = self.xz(a1, d1)
        x2, z2 = self.xz(a2, d2)
        xd, zd = self.xz(a_dst, min(d1, d2) if self.sign > 0 else max(d1, d2))
        # destination min corner
        lo_x = min(x1, x2)
        lo_z = min(z1, z2)
        if self.axis == 'x':
            dx, dz = lo_x, a_dst
        else:
            dx, dz = a_dst, lo_z
        b.C(min(x1, x2), y1, min(z1, z2), max(x1, x2), y2, max(z1, z2), dx,
            y1 if y_dst is None else y_dst, dz, mask)

    @property
    def along_dirs(self):
        """(minus, plus) directions along the wall."""
        return (N, S) if self.axis == 'x' else (W, E)
