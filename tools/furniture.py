"""Reusable furniture and fixtures (all take mansion coordinates)."""
from mansion_base import *   # noqa: F401,F403
from engine import stairs, trapdoor, torch, wallmount, bed as bedmeta, lever, button, horiz
from engine import N, S, E, W, UP, DOWN, OPP, CW, CCW, DIRV


def chair(b, x, y, z, facing, wood='spruce_stairs'):
    """Seat looking `facing` (backrest behind)."""
    b.S(x, y, z, wood, stairs(OPP[facing]))


def armchair(b, x, y, z, facing, wood='dark_oak_stairs'):
    """Stair seat with open-trapdoor armrests on both sides (1.8: stairs are valid supports)."""
    b.S(x, y, z, wood, stairs(OPP[facing]))
    left, right = CCW[facing], CW[facing]
    for side in (left, right):
        dx, _, dz = DIRV[side]
        b.S(x + dx, y, z + dz, 'trapdoor', trapdoor(side, True))


def sofa(b, x1, z1, x2, z2, y, facing, wood='dark_oak_stairs', arms=True):
    """Row of stair seats from (x1,z1) to (x2,z2) with trapdoor armrests at the ends."""
    b.F(x1, y, z1, x2, y, z2, wood, stairs(OPP[facing]))
    if arms:
        dx, _, dz = DIRV[CCW[facing]]
        # arms beyond both ends along the row
        if x1 == x2:
            lo, hi = min(z1, z2), max(z1, z2)
            b.S(x1, y, lo - 1, 'trapdoor', trapdoor(N, True))
            b.S(x1, y, hi + 1, 'trapdoor', trapdoor(S, True))
        else:
            lo, hi = min(x1, x2), max(x1, x2)
            b.S(lo - 1, y, z1, 'trapdoor', trapdoor(W, True))
            b.S(hi + 1, y, z1, 'trapdoor', trapdoor(E, True))


def slab_table(b, x1, y, z1, x2, z2, wood=5, cloth=None):
    """Table top of upper slabs (surface flush with y+1); optional carpet cloth."""
    b.F(x1, y, z1, x2, y, z2, 'wooden_slab', 8 + wood)
    if cloth is not None:
        b.F(x1, y + 1, z1, x2, y + 1, z2, 'carpet', cloth)


def post_table(b, x, y, z, wood='dark_oak_fence', top='wooden_pressure_plate'):
    b.S(x, y, z, wood)
    b.S(x, y + 1, z, top)


def pot(b, x, y, z, item='red_flower', data=0):
    b.S(x, y, z, 'flower_pot', 0, '{Item:%s,Data:%d}' % (item, data))


def rug(b, x1, z1, x2, z2, y, color, border=None):
    if border is not None:
        b.F(x1, y, z1, x2, y, z2, 'carpet', border)
        if x2 - x1 >= 2 and z2 - z1 >= 2:
            b.F(x1 + 1, y, z1 + 1, x2 - 1, y, z2 - 1, 'carpet', color)
    else:
        b.F(x1, y, z1, x2, y, z2, 'carpet', color)


def bed(b, x, y, z, head_dir, posts=False, canopy=None):
    """Bed with its FOOT at (x,y,z) and head one block toward head_dir."""
    dx, _, dz = DIRV[head_dir]
    b.S(x + dx, y, z + dz, 'bed', bedmeta(head_dir, True))
    b.S(x, y, z, 'bed', bedmeta(head_dir, False))


def double_bed(b, x, y, z, head_dir, side, canopy=None, posts='dark_oak_fence'):
    """Two beds side by side (foot at (x,z) and its neighbour toward `side`)."""
    sx, _, sz = DIRV[side]
    bed(b, x, y, z, head_dir)
    bed(b, x + sx, y, z + sz, head_dir)
    if canopy is not None:
        hx, _, hz = DIRV[head_dir]
        # four posts: two at the head beyond the pillow corners, two at the foot corners
        cx = [x - sx, x + 2 * sx]
        cz = [z - sz, z + 2 * sz]
        corners = []
        for k in range(2):
            px = cx[k] if sx else x
            pz = cz[k] if sz else z
            corners.append((px, pz))
            corners.append((px + hx, pz + hz))
        for (px, pz) in corners:
            b.F(px, y, pz, px, y + 2, pz, posts)
        xs = [p[0] for p in corners]
        zs = [p[1] for p in corners]
        b.F(min(xs), y + 3, min(zs), max(xs), y + 3, max(zs), 'wooden_slab', canopy)


def wardrobe(b, x, y, z, facing, wood=DO_PLANK):
    """2-high cabinet with open-trapdoor doors on its front face."""
    b.F(x, y, z, x, y + 1, z, *wood)
    dx, _, dz = DIRV[facing]
    b.F(x + dx, y, z + dz, x + dx, y + 1, z + dz, 'trapdoor', trapdoor(facing, True))


def fireplace(b, x, y, z, facing, width=3, depth=3, surround=('brick_block', 0),
              hearth=('double_stone_slab', 8), mantel='quartz_stairs', height=5):
    """Fireplace breast.  (x, z) = centre of the FRONT row of the breast (the row
    with the opening), y = floor block level, `facing` = into the room.
    The breast extends `depth` rows back from the front row (include the wall row!).
    Fire sits one row behind the opening, on netherrack; everything within fire
    spread range is brick/stone.  Returns fire positions (light them last).
    """
    fx, _, fz = DIRV[facing]
    lx, _, lz = DIRV[CCW[facing]]
    half = width // 2
    rows = [(x - fx * d, z - fz * d) for d in range(depth)]
    (bx1, bz1), (bx2, bz2) = rows[0], rows[-1]
    w1 = (bx1 - lx * (half + 1), bz1 - lz * (half + 1))
    w2 = (bx2 + lx * (half + 1), bz2 + lz * (half + 1))
    b.F(min(w1[0], w2[0]), y + 1, min(w1[1], w2[1]), max(w1[0], w2[0]), y + height, max(w1[1], w2[1]), *surround)
    # hearth: under the opening row and one row in front, full breast width
    h1 = (x - lx * (half + 1), z - lz * (half + 1))
    h2 = (x + fx + lx * (half + 1), z + fz + lz * (half + 1))
    b.F(min(h1[0], h2[0]), y, min(h1[1], h2[1]), max(h1[0], h2[0]), y, max(h1[1], h2[1]), *hearth)
    # opening
    o1 = (x - lx * half, z - lz * half)
    o2 = (x + lx * half, z + lz * half)
    b.F(min(o1[0], o2[0]), y + 1, min(o1[1], o2[1]), max(o1[0], o2[0]), y + 2, max(o1[1], o2[1]), 'air')
    # firebox
    fbx, fbz = x - fx, z - fz
    b.S(fbx, y, fbz, 'netherrack')
    # mantel shelf
    m1 = (x + fx - lx * (half + 1), z + fz - lz * (half + 1))
    m2 = (x + fx + lx * (half + 1), z + fz + lz * (half + 1))
    b.F(min(m1[0], m2[0]), y + 3, min(m1[1], m2[1]), max(m1[0], m2[0]), y + 3, max(m1[1], m2[1]),
        mantel, stairs(OPP[facing], True))
    return [(fbx, y + 1, fbz)]


def light_fire(b, fires):
    for (x, y, z) in fires:
        b.S(x, y, z, 'fire')


def chandelier(b, cx, cz, y_ceil, drop=3, wide=False, arms=True):
    """Chandelier hanging from ceiling layer y_ceil; body `drop` blocks below it.

    wide=True: 2x2 body with its north-west cell at (cx, cz).
    """
    w = 1 if wide else 0
    yb = y_ceil - drop
    if yb + 1 <= y_ceil - 1:
        b.F(cx, yb + 1, cz, cx + w, y_ceil - 1, cz + w, 'dark_oak_fence')
    b.F(cx, yb, cz, cx + w, yb, cz + w, *GLOW)
    if arms:
        for (ax, az) in ((cx - 1, cz), (cx + w + 1, cz + w), (cx, cz + w + 1), (cx + w, cz - 1)):
            b.S(ax, yb, az, 'dark_oak_fence')
            b.S(ax, yb + 1, az, 'torch', 5)
    b.F(cx, yb - 1, cz, cx + w, yb - 1, cz + w, 'dark_oak_fence')


def lamp_post(b, x, y, z, height=3):
    """Floor lamp: fence column with a glowstone head."""
    b.F(x, y, z, x, y + height - 2, z, 'dark_oak_fence')
    b.S(x, y + height - 1, z, *GLOW)
    b.S(x, y + height, z, 'carpet', 0)


def sconce(b, x, y, z, facing):
    """Wall torch."""
    b.S(x, y, z, 'torch', torch(facing))


def bookcase(b, x1, y1, z1, x2, y2, z2):
    b.F(x1, y1, z1, x2, y2, z2, 'bookshelf')


def counter(b, x1, y, z1, x2, z2, facing, top=('double_stone_slab', 8), doors=True):
    """Kitchen counter run; open trapdoors as cabinet doors on the facing side."""
    b.F(x1, y, z1, x2, y, z2, *top)
    if doors:
        dx, _, dz = DIRV[facing]
        b.F(x1 + dx, y, z1 + dz, x2 + dx, y, z2 + dz, 'trapdoor', trapdoor(facing, True))


def sign(b, x, y, z, facing, *lines):
    nbt = '{' + ','.join('Text%d:"%s"' % (i + 1, t) for i, t in enumerate(lines)) + '}'
    b.S(x, y, z, 'wall_sign', wallmount(facing), nbt)


def banner(b, x, y, z, facing, base, patterns=()):
    pats = ','.join('{Pattern:%s,Color:%d}' % p for p in patterns)
    b.S(x, y, z, 'wall_banner', wallmount(facing), '{Base:%d,Patterns:[%s]}' % (base, pats))


def chest(b, x, y, z, facing, items=None, trapped=False):
    nbt = None
    if items:
        parts = []
        for slot, (iid, cnt) in enumerate(items):
            parts.append('{Slot:%db,id:%s,Count:%db}' % (slot, iid, cnt))
        nbt = '{Items:[%s]}' % ','.join(parts)
    b.S(x, y, z, 'trapped_chest' if trapped else 'chest', wallmount(facing), nbt)


def skull(b, x, y, z, kind, rot=None, wall=None):
    if wall:
        b.S(x, y, z, 'skull', wallmount(wall), '{SkullType:%d}' % kind)
    else:
        b.S(x, y, z, 'skull', 1, '{SkullType:%d,Rot:%d}' % (kind, rot or 0))
