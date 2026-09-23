"""Grounds: forecourt with a fountain, gates, hedges, trees, lamps, rear patio + parterre,
gazebo and kitchen garden.  Everything sits on the lawn (grass at y=-1) inside SITE."""
from mansion_base import *   # noqa: F401,F403
from engine import stairs, N, S, E, W

HEDGE = ('leaves', 4)          # oak leaves, no-decay bit set (never decay without logs)
PINE = ('leaves', 5)
G = -1                         # lawn level


def lamp(b, x, z, h=2):
    b.F(x, 0, z, x, h - 1, z, 'dark_oak_fence')
    b.S(x, h, z, *GLOW)


def tree(b, x, z, h=5, log=0, leaves=HEDGE):
    b.F(x - 2, h - 2, z - 2, x + 2, h - 1, z + 2, *leaves)
    b.F(x - 1, h, z - 1, x + 1, h + 1, z + 1, *leaves)
    b.F(x, 0, z, x, h, z, 'log', log)


def pine(b, x, z, h=7):
    b.F(x - 2, 2, z - 2, x + 2, 3, z + 2, *PINE)
    b.F(x - 1, 4, z - 1, x + 1, 5, z + 1, *PINE)
    b.F(x, 6, z, x, h + 1, z, *PINE)
    b.F(x, 0, z, x, h - 1, z, 'log', 1)


def hedge_ring(b, x1, z1, x2, z2, flowers=None):
    b.F(x1, 0, z1, x2, 0, z2, *HEDGE)
    b.F(x1 + 1, 0, z1 + 1, x2 - 1, 0, z2 - 1, *(flowers or ('air', 0)))


def forecourt(b):
    b.section = 'grounds: forecourt + fountain'
    # gravel carriage ring round the fountain, drive to the gate, apron at the steps
    b.F(23, G, -21, 38, G, -10, 'gravel')
    b.F(25, G, -19, 36, G, -12, 'grass')
    b.F(28, G, -24, 33, G, -22, 'gravel')
    b.F(20, G, -10, 41, G, -9, 'gravel')
    # the fountain: sunken basin, stone rim, quartz column with a four-sided cascade
    b.F(26, G - 1, -18, 35, G - 1, -13, *WALL)
    b.F(26, 0, -18, 35, 0, -13, *WALL)
    b.F(27, 0, -17, 34, 0, -14, 'air')
    for (gx, gz) in ((28, -16), (33, -15), (28, -14), (33, -17)):
        b.S(gx, G - 1, gz, 'sea_lantern')
    b.F(27, G, -17, 34, 0, -14, 'water')
    b.F(30, G, -16, 31, 2, -15, *QPILLAR)
    b.F(29, 1, -16, 29, 1, -15, 'quartz_stairs', stairs(E, True))
    b.F(32, 1, -16, 32, 1, -15, 'quartz_stairs', stairs(W, True))
    b.F(30, 1, -17, 31, 1, -17, 'quartz_stairs', stairs(S, True))
    b.F(30, 1, -14, 31, 1, -14, 'quartz_stairs', stairs(N, True))
    b.F(30, 3, -16, 31, 3, -15, 'quartz_block', 1)          # chiseled cap + lantern finial
    b.F(30, 4, -16, 31, 4, -15, 'stone_slab', 7)
    for (x, z) in ((26, -18), (35, -18), (26, -13), (35, -13)):
        b.S(x, 1, z, 'stone_slab', 5)
    # lamps round the ring and along the drive
    for (x, z) in ((22, -21), (39, -21), (22, -10), (39, -10), (27, -23), (34, -23)):
        lamp(b, x, z, 3 if abs(z) > 20 and x in (27, 34) else 2)


def boundary(b):
    b.section = 'grounds: front wall, gate, hedges'
    zf = -24
    # low wall with iron railings, capped piers, grand gate piers flanking the drive
    for (x1, x2) in ((-10, 26), (35, 72)):
        b.F(x1, 0, zf, x2, 0, zf, *WALL)
        b.F(x1, 1, zf, x2, 1, zf, 'iron_bars')
    for x in (-10, -2, 6, 14, 22, 39, 47, 55, 63, 71):
        b.F(x, 1, zf, x, 1, zf, *CHISEL)
        b.S(x, 2, zf, 'stone_slab', 5)
    for x in (26, 35):
        b.F(x, 0, zf, x, 2, zf, *QPILLAR)
        b.S(x, 3, zf, 'quartz_block', 1)
        b.S(x, 4, zf, *GLOW)
        b.S(x, 5, zf, 'stone_slab', 7)
    # hedge lining inside the wall, and hedge parterres on the front lawns
    b.F(-10, 0, zf + 1, 25, 0, zf + 1, *HEDGE)
    b.F(36, 0, zf + 1, 72, 0, zf + 1, *HEDGE)
    for (x1, x2) in ((2, 16), (45, 59)):
        hedge_ring(b, x1, -19, x2, -12, ('red_flower', 0))
        b.F(x1 + 2, 0, -17, x2 - 2, 0, -14, 'red_flower', 8)
        b.F(x1 + 4, 0, -16, x2 - 4, 0, -15, 'yellow_flower')
        b.F((x1 + x2) // 2, 0, -16, (x1 + x2) // 2, 1, -15, *HEDGE)       # topiary
    for x in (4, 14, 47, 57):
        b.S(x, 0, -21, 'double_plant', 4)
        b.S(x, 1, -21, 'double_plant', 10)     # upper half (the game stores 8|facing)


def trees(b):
    b.section = 'grounds: trees'
    for (x, z) in ((-6, -18), (67, -18), (-6, 8), (67, 8)):
        tree(b, x, z, 5)
    for (x, z) in ((-6, 22), (67, 45), (-6, 45), (15, 50), (46, 50)):
        pine(b, x, z)
    tree(b, -6, 34, 6, 2, ('leaves', 6))                 # a birch


def rear(b):
    b.section = 'grounds: rear patio, parterre, gazebo'
    # plinth under the conservatory + garden steps down from its glass doorway
    b.F(23, 0, 41, 38, 1, 43, *WALL)
    b.F(28, 0, 44, 33, 1, 44, *WALL)
    b.F(28, 2, 44, 33, 2, 44, 'double_stone_slab', 0)
    b.F(28, 0, 45, 33, 0, 45, *WALL)
    b.F(28, 1, 45, 33, 1, 45, 'stone_brick_stairs', stairs(N))
    b.F(28, 0, 46, 33, 0, 46, 'stone_brick_stairs', stairs(N))
    # stone patio behind the conservatory, with benches and planters
    b.F(18, G, 45, 43, G, 49, 'stone', 6)
    b.F(18, G, 45, 18, G, 49, *WALL)
    b.F(43, G, 45, 43, G, 49, *WALL)
    for x in (21, 39):
        b.F(x, 0, 49, x + 2, 0, 49, 'dark_oak_stairs', stairs(S))
    for x in (19, 42):
        b.S(x, 0, 46, *HEDGE)
        b.S(x, 0, 48, *HEDGE)
        lamp(b, x, 47, 2)
    # parterre garden south of the patio: two hedge beds, a sundial
    b.F(28, G, 50, 33, G, 57, 'gravel')
    hedge_ring(b, 20, 50, 27, 57, ('red_flower', 4))
    hedge_ring(b, 34, 50, 41, 57, ('red_flower', 7))
    b.F(22, 0, 52, 25, 0, 55, 'red_flower', 3)
    b.F(36, 0, 52, 39, 0, 55, 'red_flower', 1)
    b.S(30, 0, 54, *CHISEL)
    b.S(30, 1, 54, 'stone_slab', 0)
    b.S(31, 0, 54, 'cobblestone_wall')
    b.S(31, 1, 54, 'torch', 5)
    # gazebo in the east garden
    gx1, gz1, gx2, gz2 = 52, 47, 58, 53
    b.F(gx1, G, gz1, gx2, G, gz2, 'double_stone_slab', 0)
    for (x, z) in ((gx1, gz1), (gx2, gz1), (gx1, gz2), (gx2, gz2)):
        b.F(x, 0, z, x, 2, z, 'birch_fence')
    b.F(gx1 - 1, 3, gz1 - 1, gx2 + 1, 3, gz2 + 1, 'wooden_slab', 2)
    b.F(gx1, 4, gz1, gx2, 4, gz2, 'wooden_slab', 2)
    b.F(gx1 + 2, 5, gz1 + 2, gx2 - 2, 5, gz2 - 2, 'wooden_slab', 2)
    b.S(55, 4, 50, *GLOW)
    b.S(55, 0, 50, 'birch_fence')
    b.S(55, 1, 50, 'wooden_pressure_plate')
    b.F(53, 0, 50, 53, 0, 50, 'birch_stairs', stairs(W))
    b.F(57, 0, 50, 57, 0, 50, 'birch_stairs', stairs(E))
    b.F(55, 0, 48, 55, 0, 48, 'birch_stairs', stairs(N))


def kitchen_garden(b):
    b.section = 'grounds: kitchen garden'
    x1, x2, z1, z2 = 65, 71, 30, 40
    b.F(x1 - 1, 0, z1 - 1, x2 + 1, 0, z2 + 1, 'fence')
    b.F(x1, 0, z1, x2, 0, z2, 'air')
    b.S(x1 - 1, 0, 35, 'fence_gate', 3)
    b.F(x1, G, z1, x2, G, z2, 'farmland', 7)
    b.F(68, G, z1, 68, G, z2, 'water')
    b.F(x1, 0, z1, 67, 0, 34, 'wheat', 7)
    b.F(69, 0, z1, x2, 0, 34, 'carrots', 7)
    b.F(x1, 0, 36, 67, 0, z2, 'potatoes', 7)
    b.F(69, 0, 36, x2, 0, z2, 'wheat', 7)
    b.S(x1 - 1, 1, z1 - 1, 'lit_pumpkin', 2)
    b.S(x2 + 1, 1, z2 + 1, 'lit_pumpkin', 0)


def all_(b):
    forecourt(b)
    boundary(b)
    trees(b)
    rear(b)
    kitchen_garden(b)
