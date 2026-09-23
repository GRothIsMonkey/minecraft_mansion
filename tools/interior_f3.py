"""Floor 3 (floor y=17, air y=18..22, ceiling y=23): the older, stranger floor + towers."""
from mansion_base import *   # noqa: F401,F403
from mansion_base import BOTH, ID, MI
from engine import stairs, trapdoor, torch, wallmount, horiz, N, S, E, W, UP, DOWN, OPP
import furniture as fu

Y = F3 + 1   # 18


def partitions(b):
    b.section = 'F3 walls'
    wall = SPRUCE_PLANK
    b.F(18, Y, 9, 43, 22, 9, *wall)                  # gallery | music room & halls
    for t in BOTH:
        b.tF(t, 22, Y, 10, 22, 22, 35, *wall)
    b.F(23, Y, 20, 38, 22, 20, *wall)                # music | trophy
    b.F(24, Y, 3, 37, 22, 3, 'air')                  # open the pavilion alcove
    b.F(24, F3_CEIL, 3, 37, F3_CEIL, 3, 'wooden_slab', 1)
    # west wing
    b.F(7, Y, 8, 7, 22, 14, *wall)
    b.F(8, Y, 10, 16, 22, 10, *wall)
    b.F(1, Y, 14, 6, 22, 14, *wall)
    b.F(1, Y, 15, 16, 22, 15, *wall)
    b.F(1, Y, 25, 16, 22, 25, *wall)
    # east wing
    b.F(45, Y, 10, 53, 22, 10, *wall)
    b.F(45, Y, 15, 53, 22, 15, *wall)
    b.F(45, Y, 30, 60, 22, 30, *wall)
    # arches from the halls into the gallery
    for t in BOTH:
        b.tF(t, 19, Y, 9, 20, Y + 2, 9, 'air')
        b.tF(t, 7, Y, 3, 7, Y + 2, 4, 'air')        # old bedroom/governess -> tower rooms


def doors(b):
    b.section = 'F3 doors'
    d, dd = b.door, b.double_door
    dd(30, Y, 9, 31, 9, S)
    dd(30, Y, 20, 31, 20, S)
    for t in BOTH:
        d(22, Y, 15, W, t=t)
        d(22, Y, 28, W, t=t)
        dd(17, Y, 12, 17, 13, W, t=t)
        d(14, Y, 10, N, t=t)
    d(7, Y, 12, W, blk='spruce_door')
    dd(12, Y, 15, 13, 15, S, blk='spruce_door')
    d(8, Y, 25, S, blk='spruce_door')
    d(17, Y, 32, W, blk='spruce_door')
    dd(46, Y, 15, 47, 15, S, blk='spruce_door')
    d(47, Y, 30, S, blk='spruce_door')
    d(44, Y, 33, E, blk='spruce_door')


def west_stair(b):
    """Second staircase F2 -> F3 in the west hall (7 steps rising south)."""
    b.section = 'F2-F3 west stair'
    b.F(18, F2_CEIL, 12, 19, F3, 15, 'air')
    for k in range(7):
        z, y = 10 + k, 11 + k
        if k > 0:
            b.F(18, 11, z, 19, y - 1, z, *DO_PLANK)
        b.F(18, y, z, 19, y, z, 'dark_oak_stairs', stairs(S))
    b.F(20, Y, 12, 20, Y, 15, 'dark_oak_fence')
    b.F(18, Y, 11, 19, Y, 11, 'dark_oak_fence')


def central(b):
    b.section = 'F3 gallery, music room, trophy room, halls'
    # portrait gallery (mx 18..43, mz 4..8) + pavilion alcove
    b.F(18, F3, 4, 43, F3, 8, *DO_PLANK)
    b.F(24, F3, 1, 37, F3, 3, *DO_PLANK)
    b.F(19, Y, 6, 42, Y, 6, 'carpet', 14)
    b.F(29, Y, 1, 32, Y, 2, 'carpet', 14)
    b.F(28, Y, 2, 28, Y, 2, 'dark_oak_stairs', stairs(W))
    b.F(33, Y, 2, 33, Y, 2, 'dark_oak_stairs', stairs(E))
    for x in (21, 26, 35, 40):
        b.S(x, Y, 8, *QPILLAR)
        fu.skull(b, x, Y + 1, 8, 0 if x in (21, 40) else 1, rot=8)
    for (x, motive) in ((24, 'Bust'), (29, 'SkullAndRoses'), (33, 'Void'), (38, 'Wither')):
        b.late_paintings.append((x, 19, 8, N, motive, 2, 2))
    for (x, motive) in ((18, 'Graham'), (43, 'Wanderer')):
        b.late_paintings.append((x, 19, 5, E if x == 18 else W, motive, 1, 2))
    for x in (19, 42):
        b.S(x, F3, 6, *GLOW)
    b.S(30, F3, 6, *GLOW)
    b.S(31, F3, 2, *GLOW)
    # halls
    for t in BOTH:
        b.tF(t, 18, F3, 16, 21, F3, 35, *DO_PLANK)
        b.tF(t, 19, Y, 17, 20, Y, 35, 'carpet', 12)
        b.tS(t, 20, F3, 24, *GLOW)
        b.tS(t, 19, F3, 33, *GLOW)
    b.F(40, F3, 10, 43, F3, 15, *DO_PLANK)
    b.F(20, F3, 10, 21, F3, 11, *DO_PLANK)
    # grandfather clock (a working clock in an item frame) in the east hall
    b.F(43, Y, 18, 43, Y + 2, 18, *DO_PLANK)
    b.S(43, Y + 3, 18, 'wooden_slab', 5)
    b.late_frames.append((42, Y + 2, 18, W, 'clock'))
    # --- music room (mx 23..38, mz 10..19) ---
    b.F(23, F3, 10, 38, F3, 19, *SPRUCE_PLANK)
    fu.rug(b, 24, 11, 36, 18, Y, 10, border=15)
    # grand piano
    b.F(25, Y, 12, 27, Y, 13, 'stained_hardened_clay', 15)
    b.S(28, Y, 13, 'stained_hardened_clay', 15)
    b.F(25, Y, 14, 28, Y, 14, 'stone_slab', 15)
    b.F(25, Y + 1, 12, 27, Y + 1, 12, 'carpet', 15)
    b.S(26, Y, 15, 'dark_oak_stairs', stairs(S))
    # pipe organ on the east wall
    for k, z in enumerate(range(12, 18)):
        b.F(38, Y, z, 38, Y + 2 + (k % 3), z, *QPILLAR)
    b.F(37, Y, 13, 37, Y, 16, 'noteblock')
    b.F(36, Y, 14, 36, Y, 15, 'dark_oak_stairs', stairs(W))
    # harp and audience chairs
    b.F(32, Y, 12, 32, Y + 2, 12, 'fence')
    b.S(32, Y + 3, 12, 'gold_block')
    b.S(31, Y, 12, 'gold_block')
    for z in (16, 18):
        b.F(28, Y, z, 30, Y, z, 'spruce_stairs', stairs(S))
    b.S(24, Y, 18, 'jukebox', 0, '{RecordItem:{id:record_13,Count:1b}}')
    fu.chest(b, 24, Y, 17, E, [('record_cat', 1), ('record_blocks', 1), ('record_mellohi', 1),
                                ('record_stal', 1), ('record_far', 1)])
    fu.chandelier(b, 30, 14, F3_CEIL, drop=2, wide=True)
    for (gx, gz) in ((25, 11), (35, 11), (25, 17), (35, 17)):
        b.S(gx, F3, gz, *GLOW)
    # --- trophy room (mx 23..38, mz 21..35) ---
    b.F(23, F3, 21, 38, F3, 35, *DO_PLANK)
    fu.rug(b, 27, 25, 34, 31, Y, 12, border=15)     # bearskin
    for z in (23, 26, 32):
        for t in BOTH:
            b.S(t.x(24), Y, z, *QPILLAR)
    for (x, z, blk) in ((24, 23, 'gold_block'), (37, 23, 'diamond_block'), (24, 26, 'emerald_block'),
                        (37, 26, 'beacon'), (24, 32, 'enchanting_table'), (37, 32, 'dragon_egg')):
        b.S(x, Y + 1, z, blk)
    for (z, kind) in ((24, 4), (28, 1), (31, 2)):
        fu.skull(b, 23, 20, z, kind, wall=E)
        fu.skull(b, 38, 20, z + 1, (kind + 2) % 5, wall=W)
    for (sx, sz, arm) in ((30.5, 22.5, 'diamond'), (26.5, 34.5, 'golden'), (34.5, 34.5, 'chainmail')):
        b.SUM('ArmorStand', sx, Y, sz,
              '{Rotation:[0f,0f],ShowArms:1,Equipment:[{id:%s_sword},{id:%s_boots},{id:%s_leggings},'
              '{id:%s_chestplate},{id:%s_helmet}]}' % ('diamond' if arm == 'chainmail' else arm, arm, arm, arm, arm))
    fu.banner(b, 30, 21, 35, N, 14, (('bo', 15), ('mc', 4)))
    fu.banner(b, 31, 21, 35, N, 14, (('bo', 15), ('mc', 4)))
    fu.chandelier(b, 30, 28, F3_CEIL, drop=2, wide=True)
    for (gx, gz) in ((27, 25), (34, 25), (27, 31), (34, 31)):
        b.S(gx, F3, gz, *GLOW)


def west_wing(b):
    b.section = 'F3 west: old bedroom, washroom, nursery, lumber room'
    # the Old Bedroom (mx 8..16, mz 1..9) with the wardrobe hiding the attic ladder
    b.F(8, F3, 1, 16, F3, 9, *DO_PLANK)
    fu.rug(b, 9, 4, 13, 8, Y, 14, border=15)
    fu.double_bed(b, 11, Y, 2, N, E, canopy=13)
    for (wx, wz) in ((8, 1), (16, 9), (8, 9), (13, 1)):
        b.S(wx, 22, wz, 'web')
    b.S(9, Y, 7, 'spruce_stairs', stairs(E))           # rocking chair
    b.S(9, Y, 1, 'bookshelf')
    fu.skull(b, 9, Y + 1, 1, 0, rot=10)
    b.F(10, Y, 9, 12, Y, 9, 'quartz_stairs', stairs(S, True))
    fu.pot(b, 11, Y + 1, 9, 'deadbush', 0)
    # wardrobe (x 15..16, z 1..3) that is really a closet with a ladder
    b.F(15, Y, 1, 16, 22, 3, *DO_PLANK)
    b.F(16, Y, 2, 16, F3_CEIL, 2, 'ladder', wallmount(W))
    b.door(15, Y, 2, E)
    fu.chandelier(b, 12, 6, F3_CEIL, drop=2, arms=False)
    # old washroom (mx 1..6, mz 8..13)
    b.F(1, F3, 8, 6, F3, 13, *CRACK)
    b.S(6, Y, 8, 'cauldron', 0)
    b.S(1, Y, 8, 'quartz_stairs', stairs(N))
    b.F(1, Y, 12, 2, Y, 13, 'quartz_stairs', stairs(E, True))
    b.S(3, 22, 11, 'web')
    b.S(1, 22, 9, 'web')
    # corridor
    b.F(8, F3, 11, 16, F3, 14, *DO_PLANK)
    b.F(9, Y, 12, 15, Y, 13, 'carpet', 7)
    # nursery (mx 1..16, mz 16..24)
    b.F(1, F3, 16, 16, F3, 24, *BIRCH_PLANK)
    fu.rug(b, 4, 18, 12, 23, Y, 6, border=3)
    for z in (17, 20):
        fu.bed(b, 2, Y, z, W)                          # cribs with rails
        b.S(2, Y, z + 1, 'birch_fence')
        b.S(3, Y, z + 1, 'birch_fence')
    b.F(14, Y, 17, 15, Y, 17, 'wool', 14)              # toy blocks
    b.S(14, Y + 1, 17, 'wool', 4)
    b.S(16, Y, 19, 'wool', 11)
    b.S(8, Y, 20, 'birch_fence')                        # rocking horse
    b.S(9, Y, 20, 'birch_fence')
    b.F(8, Y + 1, 20, 9, Y + 1, 20, 'wool', 12)
    b.S(10, Y + 1, 20, 'birch_stairs', stairs(E, True))
    b.S(16, Y, 23, 'noteblock')                         # music box
    b.F(12, Y, 22, 13, Y, 23, 'wooden_slab', 10)        # tea table
    fu.pot(b, 12, Y + 1, 22, 'red_flower', 6)
    b.S(13, Y + 1, 23, 'cake')
    fu.chest(b, 16, Y, 21, W, [('bone', 3), ('string', 5), ('feather', 2)])
    b.S(16, 22, 16, 'web')
    b.S(1, 22, 24, 'web')
    fu.chandelier(b, 8, 21, F3_CEIL, drop=2, arms=False)
    # lumber room (mx 1..16, mz 26..39): furniture under dust sheets
    b.F(1, F3, 26, 16, F3, 39, *SPRUCE_PLANK)
    for (x1, z1, x2, z2) in ((2, 27, 4, 28), (7, 30, 8, 33), (12, 27, 14, 28), (3, 34, 5, 37), (11, 35, 13, 37)):
        b.F(x1, Y, z1, x2, Y, z2, *OAK_PLANK)
        b.F(x1, Y + 1, z1, x2, Y + 1, z2, 'carpet', 0)
    b.F(16, Y, 30, 16, Y + 1, 31, 'log', 4)
    b.F(15, Y, 38, 16, Y + 1, 39, 'log', 8)
    fu.chest(b, 1, Y, 32, E, [('painting', 2), ('clock', 1), ('gold_nugget', 7)])
    fu.chest(b, 9, Y, 39, N)
    for (wx, wz) in ((1, 26), (16, 26), (1, 39), (8, 39)):
        b.S(wx, 22, wz, 'web')
    b.F(1, Y, 29, 1, F3_CEIL, 29, 'ladder', wallmount(E))   # ladder to the west attic


def tower_west(b):
    """NW tower: F3 room, L-shaped stair to the star room (F4) and the observatory (F5)."""
    b.section = 'NW tower stairs + observatory'
    b.F(0, F3, 0, 6, F3, 6, 'stone', 6)
    # openings in F4 and F5 floors above the flights
    b.F(0, EAVE - 1, 0, 0, EAVE, 5, 'air')
    b.F(1, 29, 0, 6, 30, 0, 'air')
    # flight 1 along the west wall, rising north (y 18..24)
    for k in range(7):
        z, y = 6 - k, 18 + k
        b.S(0, y, z, 'stone_brick_stairs', stairs(N))
        if k > 0:
            b.F(0, 18, z, 0, y - 1, z, *WALL)
    # flight 2 along the north wall, rising east (y 25..30)
    for k in range(6):
        x, y = 1 + k, 25 + k
        b.S(x, y, 0, 'stone_brick_stairs', stairs(E))
        if y - 1 >= EAVE + 1:
            b.F(x, EAVE + 1, 0, x, y - 1, 0, *WALL)
    b.F(2, 25, 1, 6, 25, 1, 'nether_brick_fence')
    b.F(1, 31, 1, 5, 31, 1, 'nether_brick_fence')
    # F3 tower room: map chests + armchair
    fu.armchair(b, 4, Y, 4, N)
    fu.chest(b, 6, Y, 6, W, [('map', 2), ('compass', 1)])
    b.S(3, F3, 3, *GLOW)
    # F4 "star room" (y 25..29)
    b.F(1, EAVE, 1, 6, EAVE, 6, 'wool', 11)
    for (sx, sz) in ((2, 3), (4, 5), (5, 2), (3, 6)):
        b.S(sx, 30, sz, *GLOW)
    b.F(6, 25, 4, 6, 26, 6, 'bookshelf')
    b.S(3, 25, 3, 'enchanting_table')
    # F5 observatory (y 31..35): telescope + star charts
    b.F(0, 36, 0, 6, 36, 6, 'stone_slab', 13)
    b.S(3, 31, 3, 'dark_oak_fence')
    b.S(3, 32, 3, 'dark_oak_fence')
    b.S(3, 33, 3, 'dispenser', 1)
    b.S(2, 31, 4, 'dark_oak_fence')
    b.S(4, 31, 4, 'dark_oak_fence')
    fu.chair(b, 3, 31, 5, N, 'dark_oak_stairs')
    fu.chest(b, 0, 31, 6, E, [('map', 4), ('compass', 1), ('clock', 1)])
    for (gx, gz) in ((0, 3), (6, 3)):
        b.S(gx, 30, gz, *GLOW)


def east_wing(b):
    b.section = 'F3 east: governess, servants, laundry, NE tower'
    # governess room (mx 45..53, mz 1..9)
    b.F(45, F3, 1, 53, F3, 9, *SPRUCE_PLANK)
    fu.rug(b, 47, 3, 51, 7, Y, 8, border=None)
    fu.bed(b, 46, Y, 2, N)
    b.S(45, Y, 1, 'bookshelf')
    b.S(45, Y + 1, 1, 'torch', 5)
    b.F(51, Y, 1, 53, Y, 1, 'wooden_slab', 9)
    fu.chair(b, 52, Y, 2, N, 'spruce_stairs')
    fu.wardrobe(b, 53, Y, 8, W, SPRUCE_PLANK)
    fu.pot(b, 51, Y + 1, 1, 'red_flower', 3)
    b.S(49, F3, 5, *GLOW)
    b.S(58, F3, 3, *GLOW)
    b.S(58, 29, 3, *GLOW)
    b.S(58, 30, 3, *GLOW)
    # NE tower F3: ladder up to the lookout
    b.F(55, F3, 0, 61, F3, 6, 'stone', 6)
    fu.armchair(b, 57, Y, 3, E)
    b.F(55, EAVE, 0, 61, EAVE, 6, *SPRUCE_PLANK)
    b.F(61, Y, 1, 61, EAVE, 1, 'ladder', wallmount(W))
    fu.armchair(b, 58, 25, 3, S)
    for (gx, gz) in ((56, 1), (60, 5), (56, 5), (60, 1)):       # lookout: glowstone under rugs
        b.S(gx, EAVE, gz, *GLOW)
        b.S(gx, EAVE + 1, gz, 'carpet', 14)
    # corridor
    b.F(45, F3, 11, 53, F3, 14, *SPRUCE_PLANK)
    b.F(46, Y, 12, 52, Y, 13, 'carpet', 7)
    # servants' quarters (mx 45..60, mz 16..29)
    b.F(45, F3, 16, 60, F3, 29, *OAK_PLANK)
    for z in (17, 20, 23, 26):
        fu.bed(b, 59, Y, z, E)
        fu.chest(b, 57, Y, z, E)
    fu.rug(b, 46, 17, 55, 28, Y, 12, border=15)
    for (gx, gz) in ((48, 19), (53, 26), (48, 26), (53, 19)):
        b.S(gx, F3, gz, *GLOW)
    b.F(46, Y, 21, 48, Y, 23, 'wooden_slab', 8)
    b.F(45, Y, 22, 45, Y, 22, 'oak_stairs', stairs(W))
    b.F(49, Y, 22, 49, Y, 22, 'oak_stairs', stairs(E))
    b.S(45, Y, 17, 'cauldron', 3)
    b.S(45, Y, 28, 'crafting_table')
    # laundry (mx 45..60, mz 31..39)
    b.F(45, F3, 31, 60, F3, 39, *WALL)
    for x in (47, 49, 51):
        b.S(x, Y, 39, 'cauldron', 3)
    b.F(53, 21, 32, 60, 21, 32, 'fence')
    b.F(53, 21, 36, 60, 21, 36, 'fence')
    b.F(53, Y, 32, 53, 20, 32, 'fence')
    b.F(53, Y, 36, 53, 20, 36, 'fence')
    b.F(54, 22, 32, 58, 22, 32, 'carpet', 0)
    b.F(54, 22, 36, 58, 22, 36, 'carpet', 3)
    b.F(46, Y, 33, 48, Y, 33, 'wooden_slab', 8)       # ironing / folding table
    b.S(47, Y + 1, 33, 'heavy_weighted_pressure_plate')
    b.F(56, Y, 38, 60, Y, 39, 'hay_block')
    for (lx, lz) in ((48, 36), (57, 34), (49, 32)):
        b.S(lx, 22, lz, 'fence')
        b.S(lx, 21, lz, *GLOW)
    b.S(45, Y, 35, 'crafting_table')
    b.F(60, Y, 31, 60, F3_CEIL, 31, 'ladder', wallmount(W))   # ladder to the east attic


def secret_attic(b):
    """The concealed room in the front sub-gable's attic, reached only by the wardrobe ladder."""
    b.section = 'secret attic room'
    b.F(8, EAVE, 1, 17, EAVE, 7, 'air')              # clear the hip roof's eave that pokes in here
    b.F(8, F3_CEIL, 1, 17, F3_CEIL, 7, *DO_PLANK)
    b.S(16, F3_CEIL, 2, 'ladder', wallmount(W))
    fu.rug(b, 10, 2, 13, 5, EAVE, 15, border=14)
    # a single chair facing a covered portrait, candles, dead flowers
    fu.chair(b, 12, EAVE, 5, N, 'dark_oak_stairs')
    b.late_paintings.append((12, 25, 1, S, 'Graham', 1, 2))
    for x in (10, 14):
        b.S(x, EAVE, 1, 'dark_oak_fence')
        b.S(x, EAVE + 1, 1, 'torch', 5)
    fu.pot(b, 11, EAVE, 1, 'deadbush', 0)
    fu.pot(b, 13, EAVE, 1, 'deadbush', 0)
    fu.chest(b, 9, EAVE, 6, E, [('golden_apple', 1), ('record_11', 1), ('writable_book', 1),
                                  ('diamond', 2)])
    for (wx, wy, wz) in ((9, 25, 2), (15, 25, 6), (12, 26, 4), (10, 25, 7)):
        b.S(wx, wy, wz, 'web')


def central_attic(b):
    """Dusty attic under the hipped roof: ladder from the E hall, ladder up into the cupola."""
    b.section = 'central attic + cupola ladder'
    A = EAVE      # items stand on the slab floor (y=23)
    # ladder from the F3 east hall, against the hall's west wall
    b.S(39, F3_CEIL, 33, *SPRUCE_PLANK)
    b.F(40, Y, 33, 40, F3_CEIL, 33, 'ladder', wallmount(E))
    # ladder up to the widow's walk, surfacing inside the glass cupola
    b.F(31, A, 20, 31, 34, 20, *DO_PLANK)
    b.F(30, 35, 19, 31, 35, 20, *DO_PLANK)
    b.F(30, A, 20, 30, 35, 20, 'ladder', wallmount(W))
    # trunks, sheeted furniture (white carpet over posts/stairs), a dress form
    for (cx, cz, f) in ((20, 8, E), (20, 12, E), (41, 9, W), (41, 24, W), (25, 34, N)):
        fu.chest(b, cx, A, cz, f)
    fu.chest(b, 20, A, 30, E, [('leather_chestplate', 1), ('clock', 1), ('book', 6), ('name_tag', 1)])
    for (sx, sz) in ((25, 8), (26, 8), (25, 9), (26, 9)):
        b.S(sx, A, sz, 'oak_stairs', stairs(E))
        b.S(sx, A + 1, sz, 'carpet', 0)
    for (sx, sz) in ((35, 30), (36, 30), (35, 31)):
        b.S(sx, A, sz, 'dark_oak_fence')
        b.S(sx, A + 1, sz, 'carpet', 0)
    fu.bed(b, 35, A, 8, S)
    fu.bed(b, 36, A, 8, S)
    b.SUM('ArmorStand', 27.5, A, 31.5,
          '{NoBasePlate:1b,Rotation:[200f],Equipment:[{},{},{},'
          '{id:leather_chestplate,Count:1b,tag:{display:{color:10040115}}},{}]}')
    b.P(24, 25, 28, E, 'Sunset', 2, 1)                  # hung on the salon chimney
    b.P(37, 25, 27, W, 'Pool', 2, 1)
    fu.skull(b, 21, A, 20, 0, rot=12)
    for (wx, wy, wz) in ((19, 25, 4), (42, 25, 4), (19, 25, 35), (42, 25, 35), (28, 30, 14), (33, 29, 26)):
        b.S(wx, wy, wz, 'web')
    # two lamps so the attic is not pitch black
    for (lx, lz) in ((24, 18), (37, 18)):
        b.S(lx, A, lz, 'dark_oak_fence')
        b.S(lx, A + 1, lz, *GLOW)
