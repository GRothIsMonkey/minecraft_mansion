"""Facade detail: bay modules (cloned), windows, timber framing, towers, portico."""
from mansion_base import *   # noqa: F401,F403
from mansion_base import MB, Face, BOTH, ID, MI, T
from engine import stairs, trapdoor, torch, wallmount, door_lower, door_upper, N, S, E, W, OPP, DIRV

SBS = 'stone_brick_stairs'


def beam_for(face):
    return TIMBER_Z if face.axis == 'x' else TIMBER_X


def along(face, sign):
    lo, hi = face.along_dirs
    return hi if sign > 0 else lo


def build_bay(b, f, p, f1=True, f2=True, f3=True, buttress=True, shutters=True):
    """One 5-wide bay module starting at along-position p (timber post at p)."""
    inward = OPP[f.out]
    beam = beam_for(f)
    if buttress:
        f.box(b, p, 0, 1, p, 7, 1, *WALL)
        f.set(b, p, 8, 1, SBS, stairs(inward))
    f.box(b, p, 9, 1, p + 4, 9, 1, SBS, stairs(inward, True))          # corbel table
    if f1:
        f.box(b, p + 2, 4, 0, p + 3, 7, 0, 'glass_pane')
        f.box(b, p + 2, 3, 1, p + 3, 3, 1, SBS, stairs(inward, True))    # sill
        f.box(b, p + 2, 8, 0, p + 3, 8, 0, *CHISEL)                      # lintel
    f.box(b, p, 10, 0, p, 23, 0, *TIMBER_Y)
    f.box(b, p + 1, 10, 0, p + 4, 10, 0, *beam)
    f.box(b, p + 1, 17, 0, p + 4, 17, 0, *beam)
    f.box(b, p + 1, 23, 0, p + 4, 23, 0, *beam)
    for on, y1, y2 in ((f2, 11, 13), (f3, 18, 20)):
        if not on:
            continue
        f.box(b, p + 2, y1, 0, p + 3, y2, 0, 'glass_pane')
        if shutters:
            f.box(b, p + 1, y1, 1, p + 1, y2, 1, 'trapdoor', trapdoor(f.out, True))
            f.box(b, p + 4, y1, 1, p + 4, y2, 1, 'trapdoor', trapdoor(f.out, True))


def post(b, f, a, y1=10, y2=23):
    f.box(b, a, y1, 0, a, y2, 0, *TIMBER_Y)


def beams(b, f, a1, a2):
    for y in (10, 17, 23):
        f.box(b, a1, y, 0, a2, y, 0, *beam_for(f))


def bays(b, f, starts, **kw):
    p0 = starts[0]
    build_bay(b, f, p0, **kw)
    for p in starts[1:]:
        f.clone(b, p0, 0, p0 + 4, 23, 0, 1, p)


def window(b, f, a1, a2, y1, y2, shutters=True, sill=None, glass='glass_pane'):
    f.box(b, a1, y1, 0, a2, y2, 0, glass)
    if shutters:
        f.box(b, a1 - 1, y1, 1, a1 - 1, y2, 1, 'trapdoor', trapdoor(f.out, True))
        f.box(b, a2 + 1, y1, 1, a2 + 1, y2, 1, 'trapdoor', trapdoor(f.out, True))
    if sill:
        f.box(b, a1, y1 - 1, 1, a2, y1 - 1, 1, sill, stairs(OPP[f.out], True))


def arched(b, f, a1, a2, y1, y2, glass='glass_pane', trim=SBS):
    """Window with stepped arch corners (a2-a1 >= 2)."""
    f.box(b, a1, y1, 0, a2, y2, 0, glass)
    f.set(b, a1, y2, 0, trim, stairs(along(f, -1), True))
    f.set(b, a2, y2, 0, trim, stairs(along(f, 1), True))
    f.box(b, a1 + 1, y2 + 1, 0, a2 - 1, y2 + 1, 0, *CHISEL)


def chimney_stack(b, f, a1, a2, top, depth=(1, 2), base_y=0):
    """Exterior chimney breast against face f spanning along a1..a2."""
    d1, d2 = depth
    f.box(b, a1 - 1, base_y, d1, a2 + 1, 5, d2, *WALL)
    f.box(b, a1 - 1, 6, d1, a1 - 1, 6, d2, SBS, stairs(along(f, 1)))
    f.box(b, a2 + 1, 6, d1, a2 + 1, 6, d2, SBS, stairs(along(f, -1)))
    f.box(b, a1, 6, d1, a2, top, d2, 'brick_block')
    f.box(b, a1 - 1, top + 1, d1, a2 + 1, top + 1, d2 + 1, 'stone_slab', 5)
    f.box(b, a1 - 1, top + 1, d1 - 1, a2 + 1, top + 1, d1 - 1, 'stone_slab', 5)
    f.set(b, a1, top + 2, d1, 'cobblestone_wall')
    f.set(b, a2, top + 2, d1, 'cobblestone_wall')


# --------------------------------------------------------------------------
def wing_sides(b):
    b.section = 'facade: wing sides'
    for t in BOTH:
        f = Face('x', t.x(0), t.d(W))
        bays(b, f, [10, 15, 20, 25, 30, 35])
        post(b, f, 40)
        post(b, f, 8)
        f.box(b, 8, 9, 1, 9, 9, 1, SBS, stairs(OPP[f.out], True))
        beams(b, f, 9, 9)
        f.box(b, 40, 0, 1, 40, 7, 1, *WALL)
        f.set(b, 40, 8, 1, SBS, stairs(OPP[f.out]))
        if not t.m:
            # library: two-storey windows, no shutters, stone transoms
            for p in (15, 20, 25, 30):
                f.box(b, p + 2, 4, 0, p + 3, 14, 0, 'glass_pane')
                f.box(b, p + 1, 11, 1, p + 4, 13, 1, 'air')
                f.box(b, p + 2, 9, 0, p + 3, 9, 0, *CHISEL)
            # the blank, bricked-up window of the hidden study
            f.box(b, 37, 4, 0, 38, 7, 0, *CRACK)
            f.box(b, 37, 3, 1, 38, 3, 1, 'air')
        # exterior chimney (library fireplace / dining-room fireplace)
        f.box(b, 24, 11, 1, 26, 13, 1, 'air')
        chimney_stack(b, f, 24, 26, 31)


def wing_fronts(b):
    b.section = 'facade: wing fronts'
    for t in BOTH:
        f = Face('z', 0, N)
        a = t.x
        lo, hi = t.xs(8, 17)
        # timber: corner posts + centre double post, beams
        for p in (8, 12, 13, 17):
            post(b, f, a(p))
        beams(b, f, lo, hi)
        f.box(b, lo, 9, 1, hi, 9, 1, SBS, stairs(S, True))
        # F1 projecting bay window (oriel) mx 10..15
        x1, x2 = t.xs(10, 15)
        b.F(x1, 0, -1, x2, 8, -1, *WALL)
        b.F(x1 + 1, 4, -1, x2 - 1, 7, -1, 'glass_pane')
        b.F(x1 + 1, 3, 0, x2 - 1, 8, 0, 'air')          # open into the room (window seat)
        b.F(x1, 9, -2, x2, 9, -2, SBS, stairs(S))
        b.F(x1, 9, -1, x2, 9, -1, *WALL)
        b.F(x1 + 1, 10, -1, x2 - 1, 10, -1, SBS, stairs(S))
        b.F(x1, 10, -1, x1, 10, -1, SBS, stairs(t.d(E)))
        b.F(x2, 10, -1, x2, 10, -1, SBS, stairs(t.d(W)))
        # upper windows
        for y1, y2 in ((11, 13), (18, 20)):
            for w1, w2 in ((10, 11), (14, 15)):
                c1, c2 = t.xs(w1, w2)
                window(b, f, c1, c2, y1, y2)
        # sub-gable: window in the triangle
        c1, c2 = t.xs(12, 13)
        b.F(c1, 25, 0, c2, 26, 0, 'glass_pane')
        b.F(c1, 24, -1, c2, 24, -1, SBS, stairs(S, True))


def wing_rears(b):
    b.section = 'facade: wing rears'
    for t in BOTH:
        f = Face('z', 40, S)
        lo, hi = t.xs(0, 17)
        for p in (0, 6, 11, 17):
            post(b, f, t.x(p))
        beams(b, f, lo, hi)
        f.box(b, lo, 9, 1, hi, 9, 1, SBS, stairs(N, True))
        for p in (0, 6, 11, 17):
            f.box(b, t.x(p), 0, 1, t.x(p), 7, 1, *WALL)
            f.set(b, t.x(p), 8, 1, SBS, stairs(N))
        for y1, y2 in ((11, 13), (18, 20)):
            for w1, w2 in ((3, 4), (8, 9), (13, 14)):
                c1, c2 = t.xs(w1, w2)
                window(b, f, c1, c2, y1, y2)
        # gable (attic) window
        c1, c2 = t.xs(8, 9)
        b.F(c1, 26, 40, c2, 28, 40, 'glass_pane')
        b.F(c1, 25, 41, c2, 25, 41, SBS, stairs(N, True))
        if t.m:
            # kitchen: ground floor windows + garden door
            for w1, w2 in ((3, 4), (13, 14)):
                c1, c2 = t.xs(w1, w2)
                f.box(b, c1, 4, 0, c2, 7, 0, 'glass_pane')
                f.box(b, c1, 3, 1, c2, 3, 1, SBS, stairs(N, True))
                f.box(b, c1, 8, 0, c2, 8, 0, *CHISEL)
        else:
            # the hidden study: bricked-up windows (a hint for sharp-eyed players)
            for w1, w2 in ((3, 4), (13, 14)):
                c1, c2 = t.xs(w1, w2)
                f.box(b, c1, 4, 0, c2, 7, 0, *CRACK)
                f.box(b, c1, 3, 1, c2, 3, 1, SBS, stairs(N, True))


def central_faces(b):
    b.section = 'facade: central block'
    for t in BOTH:
        # front recess (mz=3) and rear (mz=36) beside pavilion / rear room
        for fz, out in ((3, N), (36, S)):
            f = Face('z', fz, out)
            lo, hi = t.xs(18, 22)
            for p in (18, 21, 22):
                post(b, f, t.x(p))
            beams(b, f, lo, hi)
            f.box(b, lo, 9, 1, hi, 9, 1, SBS, stairs(OPP[out], True))
            c1, c2 = t.xs(19, 20)
            f.box(b, c1, 4, 0, c2, 7, 0, 'glass_pane')
            f.box(b, c1, 3, 1, c2, 3, 1, SBS, stairs(OPP[out], True))
            f.box(b, c1, 8, 0, c2, 8, 0, *CHISEL)
            for y1, y2 in ((11, 13), (18, 20)):
                f.box(b, c1, y1, 0, c2, y2, 0, 'glass_pane')
        # inner faces of the wings: front recess side walls (mx=17, mz 0..2)
        f = Face('x', t.x(17), t.d(E))
        f.box(b, 1, 11, 0, 1, 13, 0, 'glass_pane')
        f.box(b, 1, 18, 0, 1, 20, 0, 'glass_pane')
        post(b, f, 0)
        beams(b, f, 0, 2)
        # rear parts (mx=17, mz 37..40)
        f.box(b, 38, 11, 0, 38, 13, 0, 'glass_pane')
        f.box(b, 38, 18, 0, 38, 20, 0, 'glass_pane')
        beams(b, f, 37, 39)
    # above the rear garden room: master bedroom + trophy room windows
    f = Face('z', 36, S)
    beams(b, f, 23, 38)
    for p in (23, 29, 32, 38):
        post(b, f, p, 17, 23)
    for p in (23, 38):
        post(b, f, p, 10, 23)
    for w1, w2 in ((26, 27), (34, 35)):
        window(b, f, w1, w2, 11, 13)
        window(b, f, w1, w2, 18, 20)
    window(b, f, 30, 31, 18, 20, shutters=False)


def pavilion(b):
    b.section = 'facade: pavilion + entrance'
    f = Face('z', 0, N)
    # quoins
    for x in (23, 38):
        for y in range(2, 24, 2):
            b.S(x, y, 0, *CHISEL)
    # --- grand entrance ---
    b.F(28, 3, 0, 33, 8, 0, *QUARTZ)
    b.F(28, 3, 0, 28, 8, 0, *QPILLAR)
    b.F(33, 3, 0, 33, 8, 0, *QPILLAR)
    b.F(29, 3, 0, 32, 7, 0, 'glass_pane')           # sidelights + transom
    b.S(29, 7, 0, 'quartz_stairs', stairs(W, True))  # arch corners
    b.S(32, 7, 0, 'quartz_stairs', stairs(E, True))
    b.F(30, 3, 0, 31, 4, 0, 'air')                   # door opening (door placed later)
    b.F(29, 5, 0, 29, 5, 0, *QUARTZ)
    b.F(32, 5, 0, 32, 5, 0, *QUARTZ)
    b.F(28, 8, -1, 33, 8, -1, 'quartz_stairs', stairs(S, True))
    b.S(30, 8, -1, 'quartz_block', 1)
    b.S(31, 8, -1, 'quartz_block', 1)
    # ground-floor windows of the vestibule
    for w1, w2 in ((25, 26), (35, 36)):
        f.box(b, w1, 4, 0, w2, 7, 0, 'glass_pane')
        f.box(b, w1 - 1, 3, 1, w2 + 1, 3, 1, 'quartz_stairs', stairs(S, True))
        f.box(b, w1 - 1, 8, 1, w2 + 1, 8, 1, 'quartz_stairs', stairs(S, True))
        f.box(b, w1 - 1, 4, 0, w1 - 1, 7, 0, *QPILLAR)
        f.box(b, w2 + 1, 4, 0, w2 + 1, 7, 0, *QPILLAR)
    # --- second floor: balcony doors + windows ---
    b.F(29, 11, 0, 32, 15, 0, *QUARTZ)
    b.F(30, 13, 0, 31, 14, 0, 'glass_pane')
    b.F(30, 11, 0, 31, 12, 0, 'air')
    b.F(29, 11, 0, 29, 14, 0, *QPILLAR)
    b.F(32, 11, 0, 32, 14, 0, *QPILLAR)
    for w1, w2 in ((25, 26), (35, 36)):
        f.box(b, w1, 11, 0, w2, 13, 0, 'glass_pane')
        f.box(b, w1 - 1, 14, 1, w2 + 1, 14, 1, SBS, stairs(S, True))
    # string courses
    b.F(23, 9, -1, 38, 9, -1, SBS, stairs(S, True))
    b.F(23, 16, -1, 38, 16, -1, SBS, stairs(S, True))
    # third floor
    for w1, w2 in ((25, 26), (35, 36)):
        f.box(b, w1, 18, 0, w2, 20, 0, 'glass_pane')
    arched(b, f, 29, 32, 18, 21)
    b.F(29, 17, -1, 32, 17, -1, SBS, stairs(S, True))
    # gable: rose window
    b.F(29, 26, 0, 32, 29, 0, 'stained_glass_pane', 14)
    b.F(30, 26, 0, 31, 29, 0, 'stained_glass_pane', 4)
    b.F(30, 27, 0, 31, 28, 0, 'stained_glass_pane', 1)
    b.S(29, 26, 0, SBS, stairs(W, False))
    b.S(32, 26, 0, SBS, stairs(E, False))
    b.S(29, 29, 0, SBS, stairs(W, True))
    b.S(32, 29, 0, SBS, stairs(E, True))
    b.F(28, 25, -1, 33, 25, -1, SBS, stairs(S, True))
    # pavilion side walls: narrow windows
    for t in BOTH:
        g = Face('x', t.x(23), t.d(W))
        g.box(b, 1, 4, 0, 2, 7, 0, 'glass_pane')
        g.box(b, 1, 11, 0, 2, 13, 0, 'glass_pane')
        g.box(b, 1, 18, 0, 2, 20, 0, 'glass_pane')


def portico(b):
    """Columned porch with the main F2 balcony on top and wide front steps."""
    b.section = 'portico + front steps'
    # platform
    b.F(22, 0, -6, 39, 1, -1, *WALL)
    b.F(24, 2, -5, 37, 2, -1, *QUARTZ)
    b.F(24, 2, -5, 37, 2, -5, 'stone_slab', 13)  # (overwritten below by edge)
    b.F(24, 2, -5, 37, 2, -1, 'double_stone_slab', 8)
    b.F(26, 2, -4, 35, 2, -2, *QUARTZ)
    # wide steps (3 rises)
    b.F(20, 0, -8, 41, 0, -8, SBS, stairs(S))
    b.F(20, 0, -7, 41, 0, -6, *WALL)
    b.F(20, 1, -7, 41, 1, -7, SBS, stairs(S))
    b.F(20, 1, -6, 41, 1, -6, *WALL)
    b.F(22, 2, -6, 39, 2, -6, SBS, stairs(S))
    # cheek walls with urns
    for t in BOTH:
        x = t.x(20)
        b.F(x, 0, -8, x, 2, -1, *WALL)
        b.F(x, 1, -1, t.x(23), 2, -1, *WALL)
        b.F(t.x(21), 0, -6, t.x(21), 2, -2, *WALL)
        b.S(x, 3, -8, 'stone_slab', 5)
        b.S(x, 3, -5, 'flower_pot', 0, '{Item:red_flower,Data:0}')
        b.S(t.x(22), 3, -6, 'stone_slab', 5)
    # columns
    for x in (24, 28, 33, 37):
        b.F(x, 3, -5, x, 7, -5, *QPILLAR)
        b.S(x, 8, -5, 'quartz_block', 1)
        b.S(x, 3, -1, *QPILLAR)
    # entablature + balcony floor
    b.F(24, 9, -6, 37, 9, -1, *WALL)
    b.F(23, 9, -6, 38, 9, -6, SBS, stairs(S, True))
    b.F(23, 9, -5, 23, 9, -1, SBS, stairs(W, True))
    b.F(38, 9, -5, 38, 9, -1, SBS, stairs(E, True))
    b.F(25, 9, -4, 36, 9, -2, *SPRUCE_PLANK)       # porch ceiling
    b.S(30, 9, -3, *GLOW)
    b.S(31, 9, -3, *GLOW)
    b.F(24, 10, -5, 37, 10, -1, 'double_stone_slab', 8)
    # balustrade
    b.F(24, 11, -5, 37, 11, -5, 'nether_brick_fence')
    b.F(24, 11, -5, 24, 11, -1, 'nether_brick_fence')
    b.F(37, 11, -5, 37, 11, -1, 'nether_brick_fence')
    for x in (24, 28, 33, 37):
        b.S(x, 11, -5, *QPILLAR)
        b.S(x, 12, -5, 'stone_slab', 7)


def rear_room(b):
    """Garden room / conservatory with the rear balcony on its flat roof."""
    b.section = 'facade: conservatory + rear balcony'
    f = Face('z', 43, S)
    for p in (23, 26, 29, 32, 35, 38):
        f.box(b, p, 2, 0, p, 9, 0, *QPILLAR if p in (29, 32) else WALL)
    for a1, a2 in ((24, 25), (27, 28), (33, 34), (36, 37)):
        f.box(b, a1, 3, 0, a2, 8, 0, 'glass_pane')
    f.box(b, 30, 5, 0, 31, 8, 0, 'glass_pane')
    f.box(b, 30, 3, 0, 31, 4, 0, 'air')
    for t in BOTH:
        g = Face('x', t.x(23), t.d(W))
        for p in (36, 39, 43):
            g.box(b, p, 2, 0, p, 9, 0, *WALL)
        g.box(b, 37, 3, 0, 38, 8, 0, 'glass_pane')
        g.box(b, 40, 3, 0, 42, 8, 0, 'glass_pane')
    # roof: balcony floor + balustrade
    b.F(23, 9, 44, 38, 9, 44, SBS, stairs(N, True))
    b.F(22, 9, 36, 22, 9, 44, SBS, stairs(E, True))
    b.F(39, 9, 36, 39, 9, 44, SBS, stairs(W, True))
    b.F(23, 10, 37, 38, 10, 43, 'double_stone_slab', 8)
    b.F(23, 11, 43, 38, 11, 43, 'nether_brick_fence')
    b.F(23, 11, 37, 23, 11, 43, 'nether_brick_fence')
    b.F(38, 11, 37, 38, 11, 43, 'nether_brick_fence')
    for x in (23, 38):
        for z in (37, 43):
            b.S(x, 11, z, *QPILLAR)
            b.S(x, 12, z, 'stone_slab', 7)
    b.S(30, 11, 43, *QPILLAR)
    b.S(31, 11, 43, *QPILLAR)
    b.S(30, 12, 43, 'flower_pot', 0, '{Item:red_flower,Data:4}')
    b.S(31, 12, 43, 'flower_pot', 0, '{Item:red_flower,Data:6}')


def tower_window(b, f, a1, a2, y1, y2):
    arched(b, f, a1, a2, y1, y2)
    f.box(b, a1, y1 - 1, 1, a2, y1 - 1, 1, SBS, stairs(OPP[f.out], True))


def towers(b):
    b.section = 'towers'
    for t in BOTH:
        top = 36 if not t.m else 30
        xw = t.x(-1)
        lo, hi = t.xs(-1, 7)
        side = Face('x', xw, t.d(W))
        # side face: string courses + window stack (build F1, clone up)
        side.box(b, -1, 9, 1, 7, 9, 1, SBS, stairs(OPP[side.out], True))
        tower_window(b, side, 2, 4, 4, 7)
        for dy in (7, 14, 21):
            side.clone(b, 2, 3, 4, 8, 0, 1, 2, 3 + dy)
        side.clone(b, -1, 9, 7, 9, 1, 1, -1, 16)
        side.clone(b, -1, 9, 7, 9, 1, 1, -1, 23)
        # quoins
        for y in range(2, top, 2):
            b.S(xw, y, -1, *CHISEL)
        # corbelled crown
        b.F(lo - 1, top, -2, hi + 1, top, -2, SBS, stairs(S, True))
        b.F(lo - 1, top, 8, hi + 1, top, 8, SBS, stairs(N, True))
        b.F(lo - 1, top, -1, lo - 1, top, 7, SBS, stairs(E, True))
        b.F(hi + 1, top, -1, hi + 1, top, 7, SBS, stairs(W, True))
    # north faces: build on the NW tower, clone to the NE tower (symmetric faces)
    f = Face('z', -1, N)
    f.box(b, -1, 9, 1, 7, 9, 1, SBS, stairs(S, True))
    tower_window(b, f, 2, 4, 4, 7)
    for dy in (7, 14, 21):
        f.clone(b, 2, 3, 4, 8, 0, 1, 2, 3 + dy)
    f.clone(b, -1, 9, 7, 9, 1, 1, -1, 16)
    f.clone(b, -1, 9, 7, 9, 1, 1, -1, 23)
    b.C(-1, 2, -2, 7, 29, -1, 54, 2, -2, mask='masked')
    # NW observatory: windows on all four sides (y 31..34)
    for f2 in (Face('z', -1, N), Face('z', 7, S), Face('x', -1, W), Face('x', 7, E)):
        f2.box(b, 1, 31, 0, 5, 34, 0, 'glass_pane')
        f2.box(b, 3, 31, 0, 3, 34, 0, *QPILLAR)
        f2.box(b, -1, 30, 1, 7, 30, 1, SBS, stairs(OPP[f2.out], True))
    # NE tower top room: windows east + south above the roofs
    f3 = Face('z', 7, S)
    f3.box(b, 56, 26, 0, 60, 28, 0, 'glass_pane')
    f3.box(b, 58, 26, 0, 58, 28, 0, *QPILLAR)


def dormers(b):
    """Two gabled dormers on each wing's outer roof slope (attic windows)."""
    b.section = 'dormers'
    for t in BOTH:
        o = t.d(W)
        x = t.x
        lo, hi = t.xs(0, 4)
        # dormer at mz 16..19 : plaster box, carve, window, posts, mini gable roof (ridge along x)
        b.F(lo, 24, 16, hi, 27, 19, *PLASTER)
        c1, c2 = t.xs(1, 4)
        b.F(c1, 25, 17, c2, 26, 18, 'air')
        b.F(x(0), 25, 17, x(0), 26, 18, 'glass_pane')
        b.F(x(0), 24, 16, x(0), 27, 16, *TIMBER_Y)
        b.F(x(0), 24, 19, x(0), 27, 19, *TIMBER_Y)
        b.F(x(0), 27, 17, x(0), 27, 18, *TIMBER_Z)
        r1, r2 = t.xs(-1, 5)
        b.F(r1, 28, 15, r2, 28, 15, ROOF, stairs(S))
        b.F(r1, 28, 20, r2, 28, 20, ROOF, stairs(N))
        b.F(r1, 29, 16, r2, 29, 16, ROOF, stairs(S))
        b.F(r1, 29, 19, r2, 29, 19, ROOF, stairs(N))
        b.F(r1, 30, 17, r2, 30, 18, 'stone_slab', 5)
        g1, g2 = t.xs(0, 4)
        b.F(g1, 28, 16, g2, 28, 19, *PLASTER, mode='keep')
        b.F(g1, 29, 17, g2, 29, 18, *PLASTER, mode='keep')
        # clone to the second dormer position (mz 31..34)
        k1, k2 = t.xs(-1, 5)
        b.C(k1, 24, 15, k2, 30, 20, k1, 24, 30)


def roof_deck(b):
    """Widow's walk railing + glass cupola on the central hipped roof."""
    b.section = 'widow walk + cupola'
    dx1, dz1, dx2, dz2 = b.deck
    y = 35
    b.F(dx1, y + 1, dz1, dx2, y + 1, dz1, 'nether_brick_fence')
    b.F(dx1, y + 1, dz2, dx2, y + 1, dz2, 'nether_brick_fence')
    b.F(dx1, y + 1, dz1, dx1, y + 1, dz2, 'nether_brick_fence')
    b.F(dx2, y + 1, dz1, dx2, y + 1, dz2, 'nether_brick_fence')
    for (xx, zz) in ((dx1, dz1), (dx1, dz2), (dx2, dz1), (dx2, dz2)):
        b.S(xx, y + 1, zz, *QPILLAR)
        b.S(xx, y + 2, zz, 'stone_slab', 7)
    # cupola 4x4 centred on the deck
    cx1, cz1 = 29, 18
    b.F(cx1, y + 1, cz1, cx1 + 3, y + 3, cz1 + 3, 'glass_pane', mode='hollow')
    for (xx, zz) in ((cx1, cz1), (cx1 + 3, cz1), (cx1, cz1 + 3), (cx1 + 3, cz1 + 3)):
        b.F(xx, y + 1, zz, xx, y + 3, zz, *QPILLAR)
    b.F(cx1 + 1, y + 1, cz1 + 1, cx1 + 2, y + 3, cz1 + 2, 'air')  # 'hollow' also glazed the floor/top
    b.F(cx1, y + 1, cz1 + 1, cx1, y + 2, cz1 + 2, 'air')       # doorway (west side)
    b.F(cx1 - 1, y + 4, cz1 - 1, cx1 + 4, y + 4, cz1 + 4, ROOF, stairs(S))
    b.F(cx1 - 1, y + 4, cz1 + 4, cx1 + 4, y + 4, cz1 + 4, ROOF, stairs(N))
    b.F(cx1 - 1, y + 4, cz1, cx1 - 1, y + 4, cz1 + 3, ROOF, stairs(E))
    b.F(cx1 + 4, y + 4, cz1, cx1 + 4, y + 4, cz1 + 3, ROOF, stairs(W))
    b.F(cx1, y + 5, cz1, cx1 + 3, y + 5, cz1, ROOF, stairs(S))
    b.F(cx1, y + 5, cz1 + 3, cx1 + 3, y + 5, cz1 + 3, ROOF, stairs(N))
    b.F(cx1, y + 5, cz1 + 1, cx1, y + 5, cz1 + 2, ROOF, stairs(E))
    b.F(cx1 + 3, y + 5, cz1 + 1, cx1 + 3, y + 5, cz1 + 2, ROOF, stairs(W))
    b.F(cx1 + 1, y + 5, cz1 + 1, cx1 + 2, y + 5, cz1 + 2, *DO_PLANK)
    b.F(cx1 + 1, y + 4, cz1 + 1, cx1 + 2, y + 4, cz1 + 2, *GLOW)
    b.F(cx1 + 1, y + 6, cz1 + 1, cx1 + 2, y + 6, cz1 + 2, 'stone_slab', 7)
    b.S(cx1 + 1, y + 7, cz1 + 1, 'nether_brick_fence')
    b.S(cx1 + 1, y + 8, cz1 + 1, 'gold_block')


def central_chimneys(b):
    """Twin chimney stacks of the salon fireplaces (rise through the hipped roof)."""
    b.section = 'central chimneys'
    for t in BOTH:
        x1, x2 = t.xs(22, 23)
        # flue column from above the salon fireplace up through F2/F3 and out of the roof
        b.F(x1, 8, 27, x2, 33, 28, 'brick_block')
        b.F(x1 - 1, 34, 26, x2 + 1, 34, 29, 'stone_slab', 5)
        b.F(x1, 34, 27, x2, 34, 28, 'brick_block')
        b.S(x1, 35, 27, 'cobblestone_wall')
        b.S(x2, 35, 28, 'cobblestone_wall')
    # kitchen chimney on the east wing's rear face
    f = Face('z', 40, S)
    chimney_stack(b, f, 49, 51, 32)
