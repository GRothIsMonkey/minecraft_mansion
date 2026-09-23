"""Floor 2 (floor y=10, air y=11..15, ceiling y=16): living quarters."""
from mansion_base import *   # noqa: F401,F403
from mansion_base import BOTH, ID, MI
from engine import stairs, trapdoor, torch, wallmount, horiz, N, S, E, W, UP, DOWN, OPP
import furniture as fu
from interior_f1 import checker

Y = F2 + 1   # 11


def partitions(b):
    b.section = 'F2 walls'
    wall = OAK_PLANK
    b.F(7, Y, 8, 7, 15, 14, *wall)
    b.F(8, Y, 10, 16, 15, 10, *wall)
    b.F(1, Y, 14, 6, 15, 14, *wall)
    # central: halls | foyer galleries & lounge, lounge | master suite
    for t in BOTH:
        b.tF(t, 22, Y, 4, 22, 15, 25, *wall)
    b.F(18, Y, 26, 43, 15, 26, *wall)
    b.F(24, Y, 27, 24, 15, 35, *wall)
    b.F(37, Y, 27, 37, 15, 35, *wall)
    # east wing
    b.F(45, Y, 10, 53, 15, 10, *wall)
    b.F(45, Y, 15, 53, 15, 15, *wall)
    b.F(49, Y, 16, 49, 15, 29, *wall)
    b.F(45, Y, 30, 60, 15, 30, *wall)
    # doors from the foyer galleries into the halls, and the balcony doors
    for t in BOTH:
        b.door(22, Y, 6, W, t=t)
    b.double_door(30, Y, 0, 31, 0, N)


def doors(b):
    b.section = 'F2 doors'
    d, dd = b.door, b.double_door
    for t in BOTH:
        dd(17, Y, 12, 17, 13, W, t=t)
        d(22, Y, 22, W, t=t)
        d(14, Y, 10, N, t=t)
        b.tF(t, 7, Y, 3, 7, Y + 2, 4, 'air')           # arch into the tower rooms
    dd(12, Y, 15, 13, 15, S)
    d(7, Y, 12, W)
    d(12, Y, 35, S)
    dd(30, Y, 26, 31, 26, S)
    d(24, Y, 34, W)
    d(37, Y, 33, E)
    dd(30, Y, 36, 31, 36, S)
    dd(46, Y, 15, 47, 15, S)
    d(52, Y, 15, S)
    dd(46, Y, 30, 47, 30, S)
    dd(61, Y, 17, 61, 18, E)


def west_rooms(b):
    b.section = 'F2 west: blue room, tower, bath, corridor'
    # Blue Room (mx 8..16, mz 1..9) + tower sitting room (mx 0..6, mz 0..6)
    b.F(8, F2, 1, 16, F2, 9, *BIRCH_PLANK)
    fu.rug(b, 10, 3, 14, 8, Y, 11, border=3)
    fu.double_bed(b, 12, Y, 2, N, E, canopy=11)          # head against the north wall
    for x in (10, 15):
        b.S(x, Y, 1, 'bookshelf')
    b.S(10, Y + 1, 1, 'torch', 5)
    fu.pot(b, 15, Y + 1, 1, 'red_flower', 1)
    fu.wardrobe(b, 16, Y, 7, W, BIRCH_PLANK)
    fu.wardrobe(b, 16, Y, 8, W, BIRCH_PLANK)
    b.F(8, Y, 8, 9, Y, 9, 'wooden_slab', 10)
    fu.chair(b, 10, Y, 9, W, 'birch_stairs')
    b.S(8, Y + 1, 9, 'flower_pot', 0, '{Item:sapling,Data:2}')
    b.F(0, F2, 0, 6, F2, 6, 'wool', 11)
    fu.rug(b, 1, 1, 5, 5, Y, 3, border=11)
    fu.sofa(b, 1, 2, 1, 4, Y, E, 'birch_stairs')
    fu.armchair(b, 3, Y, 5, N, 'birch_stairs')
    b.S(3, Y, 3, 'birch_fence')
    b.S(3, Y + 1, 3, 'wooden_pressure_plate')
    fu.pot(b, 5, Y, 1, 'sapling', 2)
    fu.chandelier(b, 12, 5, F2_CEIL, drop=2, arms=False)
    fu.chandelier(b, 3, 3, F2_CEIL, drop=2, arms=False)
    # bath (mx 1..6, mz 8..13)
    checker(b, 1, 8, 6, 13, F2, white=QUARTZ, black=('stained_hardened_clay', 11))
    b.water.append((1, F2, 11, 2, F2, 13))
    b.F(1, F2 - 1, 11, 2, F2 - 1, 13, *QUARTZ)
    b.F(3, Y, 11, 3, Y, 13, 'quartz_stairs', stairs(W))
    b.S(6, Y, 8, 'cauldron', 3)
    b.S(6, Y + 1, 8, 'tripwire_hook', 0)
    b.S(1, Y, 8, 'quartz_stairs', stairs(N))
    b.F(2, Y, 8, 2, Y + 1, 9, 'stained_glass_pane', 0)
    b.S(4, F2_CEIL, 10, *GLOW)
    b.S(6, Y + 2, 12, 'torch', torch(W))
    # corridor
    b.F(8, F2, 11, 16, F2, 14, *OAK_PLANK)
    b.F(9, Y, 12, 15, Y, 13, 'carpet', 11)
    b.S(10, F2, 12, *GLOW)
    b.S(15, F2, 13, *GLOW)
    b.late_paintings.append((16, Y + 1, 12, W, 'Sea', 2, 1))
    # Scholar's bedroom above the secret study (mx 1..16, mz 36..39)
    b.F(1, F2, 36, 16, F2, 39, *SPRUCE_PLANK)
    fu.rug(b, 3, 37, 9, 38, Y, 12, border=15)
    fu.bed(b, 15, Y, 38, E)
    b.S(16, Y, 36, 'bookshelf')
    b.S(16, Y + 1, 36, 'torch', 5)
    b.F(1, Y, 36, 1, Y + 2, 39, 'bookshelf')
    b.F(5, Y, 39, 7, Y, 39, 'wooden_slab', 9)
    fu.chair(b, 6, Y, 38, S, 'spruce_stairs')
    b.S(5, Y + 1, 39, 'brewing_stand')
    b.S(7, Y + 1, 39, 'flower_pot', 0, '{Item:tallgrass,Data:2}')
    fu.chest(b, 13, Y, 39, N, [('book', 20), ('ink_sack', 4), ('feather', 4)])
    fu.wardrobe(b, 11, Y, 36, S, SPRUCE_PLANK)
    b.S(4, F2, 38, *GLOW)
    b.S(12, F2, 37, *GLOW)


def central_rooms(b):
    b.section = 'F2 halls + lounge'
    for t in BOTH:
        b.tF(t, 18, F2, 4, 21, F2, 25, *DO_PLANK)
        b.tF(t, 19, Y, 4, 20, Y, 25, 'carpet', 14 if not t.m else 11)
        for z in (5, 14, 23):
            b.tS(t, 19, F2, z, *GLOW)
        b.tS(t, 18, Y + 2, 9, 'torch', torch(t.d(E)))
        b.tS(t, 21, Y + 2, 18, 'torch', torch(t.d(W)))
    # lounge overlooking the foyer
    b.F(23, F2, 20, 38, F2, 25, *SPRUCE_PLANK)
    fu.rug(b, 25, 21, 36, 24, Y, 13, border=15)
    fu.sofa(b, 27, 23, 34, 23, Y, N, 'dark_oak_stairs')
    b.F(28, Y, 21, 33, Y, 21, 'wooden_slab', 13)
    fu.pot(b, 29, Y + 1, 21, 'red_flower', 0)
    fu.pot(b, 32, Y + 1, 21, 'red_flower', 8)
    b.S(30, Y + 1, 21, 'brewing_stand')
    for t in BOTH:
        fu.armchair(b, t.x(25), Y, 22, t.d(E))
        b.tF(t, 23, Y, 25, 23, Y + 2, 25, 'bookshelf')
        fu.pot(b, t.x(23), Y, 20, 'sapling', 1)
        b.tS(t, 25, F2, 24, *GLOW)
    b.S(30, F2, 22, *GLOW)
    b.S(31, F2, 22, *GLOW)
    b.S(24, Y + 2, 20, 'torch', torch(S))
    b.S(37, Y + 2, 20, 'torch', torch(S))


def master_suite(b):
    b.section = 'F2 master suite'
    # bedroom (mx 25..36, mz 27..35)
    b.F(25, F2, 27, 36, F2, 35, *DO_PLANK)
    b.F(26, F2, 28, 35, F2, 34, *SPRUCE_PLANK)
    fu.rug(b, 26, 28, 33, 34, Y, 14, border=4)
    # grand four-poster bed, head against the west wall
    fu.double_bed(b, 26, Y, 30, W, S, canopy=13)
    for z in (28, 33):
        b.S(25, Y, z, 'bookshelf')
        b.S(25, Y + 1, z, 'torch', 5)
    # bench at the foot of the bed
    b.F(27, Y, 30, 27, Y, 31, 'dark_oak_stairs', stairs(W))
    # fireplace on the east wall (flue in the salon chimney)
    b.fires += fu.fireplace(b, 36, F2, 28, W, width=3, depth=3)
    fu.armchair(b, 34, Y, 31, W)
    b.S(34, Y, 33, 'wooden_slab', 13)
    fu.pot(b, 34, Y + 1, 33, 'red_flower', 4)
    # vanity and plants
    b.F(32, Y, 35, 34, Y, 35, 'quartz_stairs', stairs(S, True))
    b.S(33, Y + 1, 35, 'flower_pot', 0, '{Item:red_flower,Data:7}')
    fu.chair(b, 33, Y, 34, S, 'birch_stairs')
    fu.pot(b, 26, Y, 35, 'sapling', 5)
    fu.pot(b, 35, Y, 27, 'sapling', 0)
    # decorative coffered ceiling
    for z in (29, 33):
        b.F(25, F2_CEIL, z, 36, F2_CEIL, z, *DO_PLANK)
    for x in (28, 33):
        b.F(x, F2_CEIL, 27, x, F2_CEIL, 35, *DO_PLANK)
    fu.chandelier(b, 30, 31, F2_CEIL, drop=2, wide=True)
    b.S(27, F2, 34, *GLOW)
    # master bath (mx 18..23, mz 27..35)
    checker(b, 18, 27, 23, 35, F2, white=QUARTZ, black=('stone', 4))
    b.water.append((19, F2, 32, 21, F2, 34))                      # sunken tub
    b.F(19, F2 - 1, 32, 21, F2 - 1, 34, 'sea_lantern')
    b.F(18, Y, 31, 22, Y, 31, 'quartz_stairs', stairs(S))
    b.F(22, Y, 32, 22, Y, 35, 'stone_slab', 7)
    b.F(18, Y, 27, 20, Y, 27, 'quartz_stairs', stairs(N, True))   # double vanity
    b.S(19, Y, 28, 'air')
    b.S(21, Y, 27, 'cauldron', 3)
    b.S(18, Y, 29, 'quartz_stairs', stairs(W))                     # toilet behind a screen
    b.F(18, Y, 30, 19, Y + 1, 30, 'stained_glass_pane', 0)
    b.S(20, F2_CEIL, 29, *GLOW)
    b.S(20, F2_CEIL, 33, *GLOW)
    b.S(23, Y + 2, 33, 'torch', torch(W))
    # walk-in closet (mx 38..43, mz 27..35)
    b.F(38, F2, 27, 43, F2, 35, *DO_PLANK)
    fu.rug(b, 40, 28, 41, 34, Y, 6, border=None)
    for z in range(28, 35, 2):
        fu.wardrobe(b, 43, Y, z, W, DO_PLANK)
    b.F(38, Y, 34, 38, Y, 35, 'chest', wallmount(E))
    for (sx, sz, col) in ((39.5, 28.5, 10040115), (39.5, 30.5, 1908001)):
        b.SUM('ArmorStand', sx, Y, sz,
              '{Rotation:[90f,0f],Equipment:[{},{id:leather_boots,tag:{display:{color:%d}}},'
              '{id:leather_leggings,tag:{display:{color:%d}}},{id:leather_chestplate,tag:{display:{color:%d}}},{}]}'
              % (col, col, col))
    b.S(41, F2_CEIL, 31, *GLOW)
    b.S(40, Y + 2, 35, 'torch', torch(N))


def east_rooms(b):
    b.section = 'F2 east: rose room, green room, billiards'
    # Rose Room (mx 45..53, mz 1..9) + tower reading room (mx 55..61, mz 0..6)
    b.F(45, F2, 1, 53, F2, 9, *OAK_PLANK)
    fu.rug(b, 46, 2, 52, 8, Y, 6, border=0)
    fu.bed(b, 51, Y, 2, N)                               # single bed, head north
    b.F(50, Y, 1, 50, Y + 2, 1, 'birch_fence')
    b.F(52, Y, 1, 52, Y + 2, 1, 'birch_fence')
    b.F(50, Y + 3, 1, 52, Y + 3, 2, 'wooden_slab', 2)
    b.S(53, Y, 1, 'bookshelf')
    fu.pot(b, 53, Y + 1, 1, 'red_flower', 7)
    fu.sofa(b, 46, 7, 48, 7, Y, N, 'birch_stairs')      # daybed / settee
    b.F(45, Y, 3, 45, Y, 4, 'quartz_stairs', stairs(W, True))   # vanity
    b.S(45, Y + 1, 3, 'flower_pot', 0, '{Item:red_flower,Data:6}')
    fu.chair(b, 46, Y, 4, W, 'birch_stairs')
    fu.wardrobe(b, 53, Y, 7, W, BIRCH_PLANK)
    fu.wardrobe(b, 53, Y, 8, W, BIRCH_PLANK)
    fu.chandelier(b, 49, 5, F2_CEIL, drop=2, arms=False)
    b.F(55, F2, 0, 61, F2, 6, *BIRCH_PLANK)
    fu.rug(b, 56, 1, 60, 5, Y, 6, border=13)
    b.F(61, Y, 0, 61, Y + 2, 2, 'bookshelf')
    fu.armchair(b, 58, Y, 3, N, 'birch_stairs')
    b.S(56, Y, 0, 'birch_fence')                        # telescope
    b.S(56, Y + 1, 0, 'dispenser', 1)
    fu.pot(b, 60, Y, 6, 'sapling', 2)
    fu.chandelier(b, 58, 3, F2_CEIL, drop=2, arms=False)
    # corridor
    b.F(45, F2, 11, 53, F2, 14, *OAK_PLANK)
    b.F(46, Y, 12, 52, Y, 13, 'carpet', 6)
    b.S(47, F2, 12, *GLOW)
    b.S(51, F2, 13, *GLOW)
    b.late_paintings.append((45, Y + 1, 12, E, 'Courbet', 2, 1))
    # linen hall (mx 45..48, mz 16..29)
    b.F(45, F2, 16, 48, F2, 29, *SPRUCE_PLANK)
    b.F(46, Y, 16, 47, Y, 29, 'carpet', 8)
    for z in (18, 21, 24, 27):
        fu.chest(b, 45, Y, z, E, [('wool', 16), ('carpet', 8)])
        fu.wardrobe(b, 48, Y, z, W, SPRUCE_PLANK)
    for z in (17, 23, 29):
        b.S(46, F2, z, *GLOW)
    # Green Room (mx 50..60, mz 16..29) with fireplace + small balcony
    b.F(50, F2, 16, 60, F2, 29, *DO_PLANK)
    fu.rug(b, 52, 19, 58, 28, Y, 13, border=12)
    b.fires += fu.fireplace(b, 61, F2, 25, W, width=3, depth=3, surround=WALL)
    fu.double_bed(b, 51, Y, 21, W, S, canopy=12)
    b.S(50, Y, 20, 'bookshelf')
    b.S(50, Y + 1, 20, 'torch', 5)
    b.S(50, Y, 23, 'bookshelf')
    fu.pot(b, 50, Y + 1, 23, 'tallgrass', 2)
    fu.armchair(b, 57, Y, 22, E)
    fu.armchair(b, 57, Y, 28, N)
    b.S(58, Y, 28, 'wooden_slab', 13)
    b.S(58, Y + 1, 28, 'brewing_stand')
    b.F(51, Y, 29, 54, Y, 29, 'wooden_slab', 13)        # writing desk
    fu.chair(b, 52, Y, 28, S, 'dark_oak_stairs')
    fu.wardrobe(b, 50, Y, 26, E)
    fu.wardrobe(b, 50, Y, 27, E)
    fu.chandelier(b, 55, 23, F2_CEIL, drop=2)
    # balcony outside the Green Room
    b.F(62, 9, 16, 63, 9, 19, 'stone_brick_stairs', stairs(W, True))
    b.F(62, F2, 16, 63, F2, 19, 'double_stone_slab', 8)
    b.F(62, Y, 16, 63, Y, 16, 'nether_brick_fence')
    b.F(62, Y, 19, 63, Y, 19, 'nether_brick_fence')
    b.F(63, Y, 17, 63, Y, 18, 'nether_brick_fence')
    # Billiard & card room (mx 45..60, mz 31..39)
    b.F(45, F2, 31, 60, F2, 39, *DO_PLANK)
    fu.rug(b, 48, 33, 57, 37, Y, 14, border=15)
    b.F(50, Y, 34, 55, Y, 36, 'wool', 13)                # billiard table
    b.F(49, Y, 34, 49, Y, 36, 'wooden_slab', 13)
    b.F(56, Y, 34, 56, Y, 36, 'wooden_slab', 13)
    for x in (50, 55):
        b.S(x, Y + 1, 35, 'stone_button', 5)
    b.S(52, Y + 1, 35, 'skull', 1, '{SkullType:0,Rot:0}')
    fu.chandelier(b, 52, 35, F2_CEIL, drop=2, wide=True, arms=False)
    b.F(45, Y, 32, 45, Y + 2, 39, 'bookshelf')
    b.F(46, Y, 39, 49, Y, 39, 'quartz_stairs', stairs(S, True))    # bar
    for x in (46, 48):
        b.S(x, Y + 1, 39, 'brewing_stand')
    b.S(47, Y + 1, 39, 'cauldron', 2)
    b.F(46, Y, 38, 49, Y, 38, 'dark_oak_fence')
    b.F(46, Y + 1, 38, 49, Y + 1, 38, 'wooden_pressure_plate')
    # card table
    b.F(58, Y, 32, 59, Y, 33, 'wooden_slab', 13)
    b.F(58, Y + 1, 32, 59, Y + 1, 33, 'carpet', 13)
    fu.chair(b, 57, Y, 32, E, 'dark_oak_stairs')
    fu.chair(b, 60, Y, 33, W, 'dark_oak_stairs')
    fu.chair(b, 58, Y, 31, S, 'dark_oak_stairs')
    fu.chair(b, 59, Y, 34, N, 'dark_oak_stairs')
    b.S(60, Y, 39, 'jukebox')
    for (gx, gz) in ((47, 34), (58, 36), (52, 32)):
        b.S(gx, F2, gz, *GLOW)
