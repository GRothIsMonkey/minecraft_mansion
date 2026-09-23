"""Floor 1 (floor block y=2, air y=3..8, ceiling y=9)."""
from mansion_base import *   # noqa: F401,F403
from mansion_base import BOTH, ID, MI
from engine import stairs, trapdoor, torch, wallmount, horiz, lever, button, N, S, E, W, UP, DOWN, OPP
import furniture as fu

Y = F1 + 1   # first air level (3)


def partitions(b):
    b.section = 'F1 walls'
    wall = OAK_PLANK
    # west wing
    b.F(7, 3, 8, 7, 8, 14, *WALL)             # bath | corridor (stone, behind tower)
    b.F(8, 3, 10, 16, 8, 10, *wall)           # study | corridor
    b.F(1, 3, 14, 6, 8, 14, *WALL)            # bath south
    b.F(1, 3, 15, 16, 15, 15, *DO_PLANK)      # library north (double height)
    b.F(1, 3, 35, 16, 15, 35, *DO_PLANK)      # library south (secret door wall)
    # east wing
    b.F(54, 3, 8, 54, 8, 14, *WALL)           # stair shaft west wall
    b.F(45, 3, 10, 53, 8, 10, *wall)
    b.F(45, 3, 15, 60, 8, 15, *wall)
    b.F(45, 3, 30, 60, 8, 30, *wall)
    b.F(55, 3, 34, 60, 8, 34, *WALL)          # pantry
    b.F(55, 3, 35, 55, 8, 39, *WALL)
    # central block: halls | foyer & salon, foyer | salon
    for t in BOTH:
        b.tF(t, 22, 3, 4, 22, 8, 35, *wall)
    b.F(23, 3, 19, 38, 15, 19, *QUARTZ)       # foyer back wall (double height)
    # open the pavilion's inner wall into the foyer (both storeys)
    b.F(24, 3, 3, 37, 8, 3, 'air')
    b.F(24, 11, 3, 37, 15, 3, 'air')
    b.F(24, 9, 3, 37, 9, 3, *SPRUCE_PLANK)
    b.F(24, 10, 3, 37, 10, 3, *OAK_PLANK)


def doors(b):
    b.section = 'F1 doors'
    d = b.door
    dd = b.double_door
    b.double_door(30, Y, 0, 31, 0, S)                 # front door
    for t in BOTH:
        d(22, Y, 6, W, t=t)                            # foyer -> halls
        d(22, Y, 15, W, t=t)                           # under landing -> halls
        d(22, Y, 31, W, hinge_right=True, t=t)         # salon -> halls
        d(17, Y, 6, W, t=t)                            # hall -> study / drawing room
        dd(17, Y, 12, 17, 13, W, t=t)                  # hall -> corridor
        d(14, Y, 10, N, t=t)                           # corridor -> study / drawing room
    b.double_door(17, Y, 24, 17, 25, W)                # W hall -> library
    b.double_door(12, Y, 15, 13, 15, S)                # corridor -> library
    b.door(7, Y, 12, W)                                # corridor -> bath
    b.double_door(44, Y, 22, 44, 23, E)                # E hall -> dining
    b.door(44, Y, 33, E)                               # E hall -> kitchen
    b.double_door(48, Y, 15, 49, 15, S)                # corridor -> dining
    b.door(54, Y, 13, E, blk='spruce_door')            # corridor -> back stairs
    b.door(51, Y, 30, S, blk='spruce_door')            # dining -> kitchen (service)
    b.door(55, Y, 37, E, blk='spruce_door')            # kitchen -> pantry
    b.double_door(52, Y, 40, 53, 40, S, blk='spruce_door')  # kitchen -> garden
    b.double_door(30, Y, 43, 31, 43, S)                # conservatory -> garden
    for t in BOTH:
        # under-landing double doors foyer -> salon
        dd(26, Y, 19, 27, 19, S, t=t)
        # archways: study -> map room ; drawing room -> morning nook
        b.tF(t, 7, Y, 3, 7, Y + 2, 4, 'air')
    # salon -> conservatory arches
    for x1, x2 in ((25, 27), (29, 32), (34, 36)):
        b.F(x1, Y, 36, x2, Y + 3, 36, 'air')


def checker(b, x1, z1, x2, z2, y, white=QUARTZ, black=('stained_hardened_clay', 15)):
    """Checkerboard via clone doubling (~9 commands for any size)."""
    b.F(x1, y, z1, x2, y, z2, *white)
    b.S(x1, y, z1, *black)
    w, h = x2 - x1 + 1, z2 - z1 + 1
    n = 2
    while n < w:
        m = min(n, w - n)
        b.C(x1, y, z1, x1 + m - 1, y, z1, x1 + n, y, z1)
        n += m
    if h >= 2:
        b.C(x1, y, z1, x2 - 1, y, z1, x1 + 1, y, z1 + 1)
    n = 2
    while n < h:
        m = min(n, h - n)
        b.C(x1, y, z1, x2, y, z1 + m - 1, x1, y, z1 + n)
        n += m


def foyer(b):
    b.section = 'F1 foyer + grand staircase'
    # --- open the double-height void ---
    for y in (F1_CEIL, F2):
        b.F(26, y, 4, 35, y, 18, 'air')
        b.F(23, y, 9, 25, y, 18, 'air')
        b.F(36, y, 9, 38, y, 18, 'air')
    # --- floors ---
    b.F(23, F1, 4, 38, F1, 18, 'stone', 6)                     # polished andesite border
    checker(b, 24, 4, 37, 17, F1)
    b.F(24, F1, 1, 37, F1, 3, *QUARTZ)
    b.F(30, F1, 1, 31, F1, 3, 'stone', 6)
    b.F(29, Y, 1, 32, Y, 2, 'carpet', 14)                       # welcome runner
    # --- coffered ceiling (y=16) ---
    b.F(23, F2_CEIL, 4, 38, F2_CEIL, 18, *DO_PLANK)
    for x1, x2 in ((24, 27), (29, 32), (34, 37)):
        for z1, z2 in ((5, 8), (10, 13), (15, 17)):
            b.F(x1, F2_CEIL, z1, x2, F2_CEIL, z2, *SPRUCE_PLANK)
    for gx, gz in ((25, 6), (36, 6), (25, 16), (36, 16)):
        b.S(gx, F2_CEIL, gz, *GLOW)
    # --- central flight (6 wide, rises 3 + landing) ---
    b.F(28, 3, 9, 33, 3, 9, 'dark_oak_stairs', stairs(S))
    b.F(28, 3, 10, 33, 3, 11, *DO_PLANK)
    b.F(28, 4, 10, 33, 4, 10, 'dark_oak_stairs', stairs(S))
    b.F(28, 4, 11, 33, 4, 11, *DO_PLANK)
    b.F(28, 5, 11, 33, 5, 11, 'dark_oak_stairs', stairs(S))
    # landing (top surface y=7)
    b.F(23, 6, 12, 38, 6, 18, *DO_PLANK)
    b.F(28, 7, 13, 33, 7, 17, 'carpet', 14)
    # balusters on the central flight
    for x in (28, 33):
        b.S(x, 4, 9, 'dark_oak_fence')
        b.S(x, 5, 10, 'dark_oak_fence')
        b.S(x, 6, 11, 'dark_oak_fence')
    # newel lamps
    for x in (27, 34):
        b.F(x, 3, 9, x, 4, 9, *QPILLAR)
        b.S(x, 5, 9, *GLOW)
        b.S(x, 6, 9, 'carpet', 0)
    # landing railing where it overlooks the hall
    b.F(26, 7, 12, 27, 7, 12, 'dark_oak_fence')
    b.F(34, 7, 12, 35, 7, 12, 'dark_oak_fence')
    # side flights up to the galleries (rise 4, facing north)
    for t in BOTH:
        x1, x2 = t.xs(23, 25)
        for k, (zz, yy) in enumerate(((11, 7), (10, 8), (9, 9), (8, 10))):
            b.F(x1, yy, zz, x2, yy, zz, 'dark_oak_stairs', stairs(N))
            b.S(t.x(25), yy + 1, zz, 'dark_oak_fence')
        # upside-down stringers under the side flight
        b.F(x1, 6, 11, x2, 6, 11, 'dark_oak_stairs', stairs(S, True))
        b.F(x1, 7, 10, x2, 7, 10, 'dark_oak_stairs', stairs(S, True))
        b.F(x1, 8, 9, x2, 8, 9, 'dark_oak_stairs', stairs(S, True))
        # gallery railing + columns
        b.F(t.x(25), 11, 4, t.x(25), 11, 7, 'dark_oak_fence')
        for zz in (4, 8):
            b.F(t.x(25), 3, zz, t.x(25), 8, zz, *QPILLAR)
            b.F(t.x(25), 11, zz, t.x(25), 15, zz, *QPILLAR)
        # tall landing columns (floor to ceiling)
        b.F(t.x(26), 3, 12, t.x(26), 5, 12, *QPILLAR)
        b.F(t.x(26), 7, 12, t.x(26), 15, 12, *QPILLAR)
        # banners on the aisle walls
        fu.banner(b, t.x(23), 7, 5, t.d(E), 15, (('cbo', 4), ('bo', 4)))
        fu.banner(b, t.x(23), 7, 7, t.d(E), 15, (('cbo', 4), ('bo', 4)))
        # sconces on the gallery columns (facing into the void)
        b.S(t.x(26), 6, 4, 'torch', torch(t.d(E)))
        b.S(t.x(26), 6, 8, 'torch', torch(t.d(E)))
        b.S(t.x(26), 13, 4, 'torch', torch(t.d(E)))
        b.S(t.x(26), 13, 8, 'torch', torch(t.d(E)))
        # vestibule benches + plants
        x = t.x(24)
        b.F(x, 3, 1, x, 3, 2, 'dark_oak_stairs', stairs(t.d(W)))
        fu.pot(b, t.x(25), 3, 1, 'sapling', 5)
        fu.pot(b, t.x(29), 7, 18, 'red_flower', 0)
        fu.pot(b, t.x(23), 7, 18, 'sapling', 1)
    b.F(26, 11, 3, 35, 11, 3, 'dark_oak_fence')               # front gallery railing
    # --- centerpiece table under the chandelier ---
    b.F(30, 3, 6, 31, 3, 7, 'dark_oak_fence')
    b.F(30, 4, 6, 31, 4, 7, 'wooden_slab', 13)
    fu.pot(b, 30, 5, 6, 'red_flower', 4)
    fu.pot(b, 31, 5, 7, 'red_flower', 8)
    fu.pot(b, 30, 5, 7, 'yellow_flower', 0)
    fu.pot(b, 31, 5, 6, 'red_flower', 1)
    # --- grand chandelier (hangs from y=16 to y=11) ---
    b.F(30, 13, 6, 31, 15, 7, 'dark_oak_fence')
    b.F(30, 12, 6, 31, 12, 7, *GLOW)
    b.F(28, 12, 5, 33, 12, 5, 'dark_oak_fence')
    b.F(28, 12, 8, 33, 12, 8, 'dark_oak_fence')
    b.F(28, 12, 6, 28, 12, 7, 'dark_oak_fence')
    b.F(33, 12, 6, 33, 12, 7, 'dark_oak_fence')
    for (tx, tz) in ((28, 5), (33, 5), (28, 8), (33, 8), (30, 5), (31, 8), (28, 6), (33, 7)):
        b.S(tx, 13, tz, 'torch', 5)
    b.F(30, 11, 6, 31, 11, 7, 'dark_oak_fence')
    b.F(30, 10, 6, 31, 10, 7, *GLOW)
    # --- landing wall: painting + overlook from the F2 lounge ---
    b.F(26, 11, 19, 35, 13, 19, 'air')
    b.F(26, 11, 19, 35, 11, 19, 'dark_oak_fence')
    # --- hidden cubby under the landing (behind the central flight) ---
    b.F(27, 3, 12, 27, 5, 16, *DO_PLANK)
    b.F(34, 3, 12, 34, 5, 16, *DO_PLANK)
    b.F(28, 3, 16, 33, 5, 16, *DO_PLANK)
    b.F(28, 3, 12, 33, 5, 15, 'air')
    b.F(28, F1, 12, 33, F1, 15, *SPRUCE_PLANK)
    # support pillars at the landing's rear corners
    for t in BOTH:
        b.tF(t, 23, 3, 18, 23, 5, 18, *QPILLAR)


def foyer_late(b):
    """Entities / attachments that must come after everything around them."""
    b.section = 'F1 foyer details'
    # the grand painting on the landing wall (4x2 'Fighters' centred on x 29..32)
    b.P(31, 8, 18, N, 'Fighters', 4, 2)
    # hidden cubby door: a doorway in the cubby's west wall hidden by a painting
    b.F(27, 3, 13, 27, 4, 13, 'air')
    b.S(27, 3, 13, 'wall_sign', wallmount(S), '{Text2:"Shh..."}')
    b.S(27, 4, 13, 'wall_sign', wallmount(S))
    b.P(26, 3, 13, W, 'Wanderer', 1, 2)


def salon(b):
    b.section = 'F1 salon + conservatory'
    b.F(23, F1, 20, 38, F1, 35, *DO_PLANK)
    b.F(24, F1, 21, 37, F1, 34, *SPRUCE_PLANK)
    for z in (24, 28, 32):
        b.F(23, F1_CEIL, z, 38, F1_CEIL, z, *DO_PLANK)
    fu.rug(b, 26, 23, 35, 33, Y, 14, border=15)
    fires = []
    for t in BOTH:
        # twin fireplaces on the side walls
        fires += fu.fireplace(b, t.x(24), F1, 28, t.d(E), width=3, depth=3)
        # seating group facing the fire
        fu.sofa(b, t.x(29), 26, t.x(29), 30, Y, t.d(W))
        b.tF(t, 27, Y, 27, 27, Y, 29, 'wooden_slab', 13)
        fu.pot(b, t.x(27), Y + 1, 28, 'red_flower', 2 if t.m else 3)
        fu.armchair(b, t.x(26), Y, 25, S)
        fu.armchair(b, t.x(26), Y, 31, N)
        # bookcases flanking the under-landing doors, lamps in the corners
        b.tF(t, 23, Y, 20, 25, Y + 2, 20, 'bookshelf')
        fu.lamp_post(b, t.x(23), Y, 33, 3)
        fu.pot(b, t.x(23), Y, 34, 'sapling', 3)
        # chandelier above each group
        fu.chandelier(b, t.x(28), 28, F1_CEIL, drop=2)
    b.fires += fires
    # tea table in the middle + card table near the garden room
    b.F(30, Y, 27, 31, Y, 29, 'dark_oak_fence')
    b.F(30, Y + 1, 27, 31, Y + 1, 29, 'wooden_slab', 13)
    b.S(30, Y + 2, 28, 'cake')
    fu.pot(b, 31, Y + 2, 28, 'red_flower', 6)
    b.F(29, Y, 33, 32, Y, 34, 'carpet', 13)
    b.F(30, Y, 33, 31, Y, 34, 'wooden_slab', 13)
    fu.chair(b, 29, Y, 33, E, 'dark_oak_stairs')
    fu.chair(b, 32, Y, 34, W, 'dark_oak_stairs')
    b.late_paintings.append((30, 5, 20, S, 'Stage', 2, 2))
    # --- conservatory ---
    b.F(24, F1, 37, 37, F1, 42, *MOSSY)
    b.F(25, F1, 38, 36, F1, 41, 'double_stone_slab', 8)
    b.F(29, Y, 38, 32, Y, 41, 'stone_slab', 7)
    b.F(30, Y, 39, 31, Y, 40, 'air')
    b.F(30, 1, 39, 31, 1, 40, 'sea_lantern')
    b.water += [(30, F1, 39, 31, F1, 40)]
    for (x1, z1) in ((24, 37), (36, 37), (24, 41), (36, 41)):
        b.F(x1, Y, z1, x1 + 1, Y, z1 + 1, 'leaves', 4)
        b.S(x1, Y + 1, z1, 'leaves', 4)
    for t in BOTH:
        fu.chair(b, t.x(27), Y, 39, t.d(E), 'birch_stairs')
        fu.chair(b, t.x(27), Y, 40, t.d(E), 'birch_stairs')
        fu.pot(b, t.x(26), Y, 42, 'red_flower', 4 if t.m else 7)
        b.tS(t, 24, F1_CEIL, 39, *GLOW)
    b.S(30, F1_CEIL, 38, *GLOW)
    b.S(31, F1_CEIL, 41, *GLOW)


def halls(b):
    b.section = 'F1 halls'
    for t in BOTH:
        b.tF(t, 18, F1, 4, 21, F1, 35, *DO_PLANK)
        b.tF(t, 19, Y, 4, 20, Y, 35, 'carpet', 14 if not t.m else 11)
        for z in (9, 18, 27):
            b.tS(t, 18, 6, z, 'torch', torch(t.d(E)))
        for z in (4, 13, 22, 34):
            b.tS(t, 21, 6, z, 'torch', torch(t.d(W)))
        # console tables with plants
        b.tF(t, 18, Y, 20, 18, Y, 21, 'wooden_slab', 13)
        fu.pot(b, t.x(18), Y + 1, 20, 'red_flower', 0 if not t.m else 5)
        b.tF(t, 21, Y, 9, 21, Y, 10, 'wooden_slab', 13)
        fu.pot(b, t.x(21), Y + 1, 10, 'sapling', 0)
    # suits of armour at the south end of the west hall, a bust (skull) in the east hall
    for x in (18.5, 21.5):
        b.SUM('ArmorStand', x, Y, 34.5,
              '{Rotation:[180f,0f],ShowArms:1,Equipment:[{id:iron_sword},{id:iron_boots},{id:iron_leggings},{id:iron_chestplate},{id:iron_helmet}]}')
    b.S(43, Y, 34, *QPILLAR)
    fu.skull(b, 43, Y + 1, 34, 0, rot=4)
    b.S(40, Y, 34, *QPILLAR)
    fu.skull(b, 40, Y + 1, 34, 4, rot=12)


def study(b):
    b.section = 'F1 study + map room + bath'
    b.F(8, F1, 1, 16, F1, 9, *SPRUCE_PLANK)
    fu.rug(b, 10, 3, 14, 7, Y, 13, border=15)
    # desk (full blocks) + chair facing the oriel window
    b.F(11, Y, 5, 13, Y, 5, *DO_PLANK)
    b.S(12, Y + 1, 5, 'bookshelf')
    fu.pot(b, 11, Y + 1, 5, 'red_flower', 0)
    b.S(13, Y + 1, 5, 'torch', 5)
    fu.armchair(b, 12, Y, 6, N)
    # window seat in the oriel
    b.F(11, Y, 0, 14, Y, 0, 'spruce_stairs', stairs(S))
    b.F(10, Y, 1, 10, Y, 1, 'spruce_stairs', stairs(W))
    b.F(15, Y, 1, 15, Y, 1, 'spruce_stairs', stairs(E))
    # bookcases, filing chests, wardrobe
    b.F(16, Y, 1, 16, Y + 2, 5, 'bookshelf')
    b.F(16, Y, 7, 16, Y + 2, 8, 'bookshelf')
    b.F(8, Y, 9, 12, Y + 2, 9, 'bookshelf')
    fu.chest(b, 8, Y, 1, E, [('paper', 32), ('book', 12), ('feather', 3)])
    fu.chest(b, 8, Y, 2, E)
    fu.wardrobe(b, 16, Y, 6, W)
    b.F(10, F1_CEIL, 2, 14, F1_CEIL, 2, *DO_PLANK)
    b.F(10, F1_CEIL, 8, 14, F1_CEIL, 8, *DO_PLANK)
    fu.chandelier(b, 12, 4, F1_CEIL, drop=2)
    # --- map room (NW tower) ---
    b.F(0, F1, 0, 6, F1, 6, 'stone', 2)
    b.F(3, F1, 0, 3, F1, 6, 'stone', 4)
    b.F(0, F1, 3, 6, F1, 3, 'stone', 4)
    b.S(3, F1, 3, 'gold_block')
    b.F(0, Y, 6, 1, Y + 2, 6, 'bookshelf')
    b.F(5, Y, 6, 6, Y + 2, 6, 'bookshelf')
    b.S(3, Y, 3, 'dark_oak_fence')
    b.S(3, Y + 1, 3, 'lapis_block')                  # the globe
    fu.chest(b, 6, Y, 0, W, [('map', 3), ('compass', 1), ('paper', 16)])
    b.S(6, Y, 1, 'crafting_table')
    b.S(0, Y, 0, 'dark_oak_fence')                   # telescope on a tripod
    b.S(0, Y + 1, 0, 'dispenser', 1)
    fu.armchair(b, 1, Y, 3, E)
    fu.chandelier(b, 3, 3, F1_CEIL, drop=2, arms=False)
    # --- bathroom ---
    b.F(1, F1, 8, 6, F1, 13, *QUARTZ)
    b.water += [(1, F1, 11, 2, F1, 13)]              # sunken tub (water poured last)
    b.F(1, 1, 12, 2, 1, 12, 'sea_lantern')
    b.F(3, Y, 11, 3, Y, 13, 'stone_slab', 7)
    b.S(1, Y, 8, 'quartz_stairs', stairs(N))          # toilet
    b.S(1, Y, 9, 'trapdoor', trapdoor(S, False))
    b.F(2, Y, 8, 2, Y + 1, 9, 'stained_glass_pane', 0)  # frosted privacy screen
    b.S(6, Y, 8, 'cauldron', 3)                       # sink
    b.S(6, Y + 1, 8, 'tripwire_hook', 0)
    b.S(5, Y, 8, 'quartz_stairs', stairs(N, True))
    b.S(4, Y, 8, 'quartz_stairs', stairs(N, True))
    b.S(3, F1_CEIL, 10, *GLOW)
    b.S(6, Y, 13, 'wool', 0)                          # towels
    b.S(6, Y + 1, 13, 'wool', 3)


def corridors(b):
    b.section = 'F1 corridors'
    for t in BOTH:
        b.tF(t, 8, F1, 11, 16, F1, 14, *OAK_PLANK)
        b.tF(t, 9, Y, 12, 15, Y, 13, 'carpet', 12)
        b.tS(t, 8, 6, 11, 'torch', torch(t.d(E)))
        b.tS(t, 16, 6, 14, 'torch', torch(t.d(W)))
        b.tF(t, 9, Y, 14, 10, Y, 14, 'wooden_slab', 13)
        fu.pot(b, t.x(9), Y + 1, 14, 'red_flower', 8)


def library(b):
    b.section = 'F1 library (two storeys)'
    # open the double-height void (keep galleries N, S and E)
    b.F(1, F1_CEIL, 19, 13, F2, 31, 'air')
    b.F(1, F1, 16, 16, F1, 34, *DO_PLANK)
    fu.rug(b, 3, 19, 12, 31, Y, 11, border=15)
    # ground-level bookcases along N, S, E walls (full height under galleries)
    b.F(1, Y, 16, 16, 8, 16, 'bookshelf')
    b.F(12, Y, 16, 13, Y + 1, 16, 'air')              # doorway from the corridor
    b.F(1, Y, 34, 16, 8, 34, 'bookshelf')
    b.F(16, Y, 17, 16, 8, 33, 'bookshelf')
    b.F(16, Y, 24, 16, Y + 1, 25, 'air')              # doorway from the west hall
    # gallery-level bookcases
    b.F(1, 11, 16, 16, 14, 16, 'bookshelf')
    b.F(12, 11, 16, 13, 12, 16, 'air')                # door from the F2 corridor
    b.F(1, 11, 34, 16, 14, 34, 'bookshelf')
    b.F(12, 11, 34, 12, 12, 34, 'air')                # door to the scholar's room (F2)
    b.F(16, 11, 17, 16, 14, 33, 'bookshelf')
    # gallery edge: log pillars below, railing above
    for x in (1, 4, 8, 11):
        b.F(x, Y, 18, x, 8, 18, 'log', 1)
        b.F(x, Y, 32, x, 8, 32, 'log', 1)
    for z in (18, 22, 28, 32):
        b.F(14, Y, z, 14, 8, z, 'log', 1)
    b.F(1, 11, 18, 13, 11, 18, 'spruce_fence')
    b.F(1, 11, 32, 13, 11, 32, 'spruce_fence')
    b.F(14, 11, 18, 14, 11, 32, 'spruce_fence')
    b.S(1, 11, 32, 'air')
    b.F(1, Y, 31, 1, 10, 31, 'ladder', wallmount(N))  # ladder up to the south gallery
    # stone fireplace on the west wall (flue in the exterior chimney)
    b.fires += fu.fireplace(b, 0, F1, 25, E, width=3, depth=3, surround=WALL)
    fu.armchair(b, 3, Y, 23, S)
    fu.armchair(b, 3, Y, 27, N)
    b.S(4, Y, 25, 'wooden_slab', 13)
    # reading tables with bench seating and lamps (clone the first table)
    b.F(6, Y, 21, 11, Y, 21, 'wooden_slab', 13)
    b.F(6, Y, 20, 11, Y, 20, 'spruce_stairs', stairs(N))
    b.F(6, Y, 22, 11, Y, 22, 'spruce_stairs', stairs(S))
    b.S(7, Y + 1, 21, 'spruce_fence')
    b.S(7, Y + 2, 21, 'torch', 5)
    b.S(10, Y + 1, 21, 'spruce_fence')
    b.S(10, Y + 2, 21, 'torch', 5)
    b.C(6, Y, 20, 11, Y + 2, 22, 6, Y, 26)
    b.S(3, Y, 20, 'enchanting_table')
    # librarian's standing desk; the secret lever hides underneath it
    b.S(9, Y, 30, 'spruce_fence')
    b.S(11, Y, 30, 'spruce_fence')
    b.F(9, Y + 1, 30, 11, Y + 1, 30, 'wooden_slab', 9)
    fu.pot(b, 9, Y + 2, 30, 'red_flower', 2)
    b.S(11, Y + 2, 30, 'torch', 5)
    # chandeliers in the void, ladders on the gallery shelves
    fu.chandelier(b, 7, 22, F2_CEIL, drop=4, wide=True)
    fu.chandelier(b, 7, 28, F2_CEIL, drop=4, wide=True)
    for z in (21, 29):
        b.F(15, 11, z, 15, 14, z, 'ladder', wallmount(W))
    # under-gallery lights hidden in the gallery soffit
    for (gx, gz) in ((3, 17), (9, 17), (3, 33), (9, 33), (15, 20), (15, 27)):
        b.S(gx, F1_CEIL, gz, *GLOW)
    # candles on the gallery balustrade
    for (cx, cz) in ((4, 18), (10, 18), (4, 32), (10, 32), (14, 22), (14, 28)):
        b.S(cx, 12, cz, 'torch', 5)
    # gallery reading nooks
    fu.armchair(b, 15, 11, 17, W)
    fu.armchair(b, 15, 11, 33, W)


def library_secret_door(b):
    """Hidden bookcase door (lever under the librarian's desk) -> secret study.

    Closed: sticky piston (powered) holds a bookshelf in the doorway.
    Open (lever off): the bookshelf drops into the floor; the upper half of
    the doorway is a walk-through painting (wall sign behind it).
    """
    b.section = 'F1 library secret door'
    # doorway through the wall row
    b.F(8, Y, 35, 8, Y + 1, 35, 'air')
    b.F(8, Y, 34, 8, Y + 1, 34, 'air')
    # Order matters in 1.8: lever first, then the dust (computes its power when
    # placed), then the piston (checks power when placed and extends).
    b.S(10, Y, 30, 'lever', 5 + 8)                    # floor lever, ON = door closed
    # redstone channel under the floor (y=1) on a hidden beam (y=0)
    b.F(8, 0, 30, 10, 0, 30, *WALL)
    b.F(8, 0, 31, 8, 0, 34, *WALL)
    b.F(10, 1, 30, 8, 1, 30, 'redstone_wire')
    b.F(8, 1, 31, 8, 1, 33, 'redstone_wire')
    b.S(8, F1, 34, 'bookshelf')                      # sits on the piston; pushed up on power
    b.S(8, 1, 34, 'sticky_piston', 1)
    # what the game does next tick: the powered piston extends and lifts the bookshelf
    b.X(8, 1, 34, 'sticky_piston', 9)
    b.X(8, F1, 34, 'piston_head', 9)
    b.X(8, Y, 34, 'bookshelf')
    # upper half: wall sign (passable, solid-material) + painting over it
    b.S(8, Y + 1, 34, 'wall_sign', wallmount(E))
    b.late_paintings.append((8, Y + 1, 33, N, 'Kebab', 1, 1))


def secret_study(b):
    b.section = 'F1 secret study'
    b.F(1, F1, 36, 16, F1, 39, *DO_PLANK)
    fu.rug(b, 2, 36, 7, 39, Y, 14, border=15)
    b.F(1, Y, 36, 1, Y + 3, 39, 'bookshelf')
    b.F(2, Y, 39, 6, Y + 1, 39, 'bookshelf')
    # desk with the journal
    b.F(4, Y, 37, 5, Y, 37, 'wooden_slab', 13)
    fu.chair(b, 4, Y, 38, N, 'dark_oak_stairs')
    b.S(5, Y + 1, 37, 'brewing_stand')
    fu.skull(b, 4, Y + 1, 37, 0, rot=8)
    journal = ('{Items:[{Slot:13b,id:written_book,Count:1b,tag:{title:"Journal of Lord Ashgrove",'
               'author:"Lord Ashgrove",pages:['
               '"If you are reading this, you found the lever beneath my desk. The house keeps more secrets.",'
               '"Beneath the grand stair a wanderer guards a door. Walk through him and descend.",'
               '"My gold rests below this very room. Follow the stair, and mind the loose barrel in the cellar.",'
               '"Above the old bedroom, behind the wardrobe, I hid what I could not bear to look at.",'
               '"And should the house burn, the tunnel runs south to the old well. -A."]}}]}')
    b.S(2, Y, 36, 'chest', wallmount(S), journal)
    b.S(3, Y, 36, 'ender_chest', wallmount(S))
    for (wx, wz) in ((1, 36), (16, 36), (16, 39)):
        b.S(wx, 8, wz, 'web')
    b.S(6, F1_CEIL, 37, *GLOW)
    b.S(12, 6, 36, 'torch', torch(S))
    # stair down to the hidden vault (descends westward along z 38..39)
    b.F(9, 1, 38, 15, 2, 39, 'air')
    for k in range(7):
        x = 15 - k
        b.F(x, 2 - k, 38, x, 2 - k, 39, 'dark_oak_stairs', stairs(E))
        if 2 - k - 1 >= BF + 1:
            b.F(x, BF + 1, 38, x, 1 - k, 39, *WALL)
    b.F(9, Y, 37, 15, Y, 37, 'dark_oak_fence')
    b.F(8, Y, 38, 8, Y, 38, 'dark_oak_fence')


def east_front(b):
    b.section = 'F1 drawing room + breakfast nook'
    # drawing room (mx 45..53, mz 1..9) with the east oriel window seat
    b.F(45, F1, 1, 53, F1, 9, *BIRCH_PLANK)
    fu.rug(b, 47, 3, 51, 7, Y, 3, border=0)
    b.F(47, Y, 0, 50, Y, 0, 'birch_stairs', stairs(S))
    fu.sofa(b, 49, 6, 51, 6, Y, N, 'birch_stairs')
    fu.armchair(b, 47, Y, 4, E, 'birch_stairs')
    b.F(49, Y, 4, 51, Y, 4, 'wooden_slab', 10)
    fu.pot(b, 50, Y + 1, 4, 'red_flower', 7)
    b.S(45, Y, 1, 'jukebox')
    b.S(45, Y + 1, 1, 'flower_pot', 0, '{Item:red_flower,Data:3}')
    b.F(45, Y, 8, 46, Y + 2, 9, 'bookshelf')
    b.F(53, Y, 7, 53, Y, 9, 'wooden_slab', 10)
    fu.pot(b, 53, Y + 1, 8, 'sapling', 2)
    fu.chandelier(b, 49, 4, F1_CEIL, drop=2)
    # breakfast nook in the NE tower (mx 55..61, mz 0..6)
    b.F(55, F1, 0, 61, F1, 6, 'stone', 4)
    b.F(57, F1, 2, 59, F1, 4, *BIRCH_PLANK)
    b.F(58, Y, 3, 58, Y, 3, 'birch_fence')
    b.S(58, Y + 1, 3, 'birch_fence')
    b.F(57, Y, 2, 59, Y, 4, 'wooden_slab', 10)
    b.S(58, Y + 1, 3, 'cake')
    fu.pot(b, 57, Y + 1, 2, 'red_flower', 5)
    fu.chair(b, 58, Y, 1, S, 'birch_stairs')
    fu.chair(b, 58, Y, 5, N, 'birch_stairs')
    fu.chair(b, 56, Y, 3, E, 'birch_stairs')
    fu.chair(b, 60, Y, 3, W, 'birch_stairs')
    for (px, pz) in ((55, 0), (61, 0), (61, 6)):
        fu.pot(b, px, Y, pz, 'sapling', 4)
    fu.chandelier(b, 58, 3, F1_CEIL, drop=2, arms=True)


def dining(b):
    b.section = 'F1 dining room'
    b.F(45, F1, 16, 60, F1, 29, *DO_PLANK)
    b.F(46, F1, 17, 59, F1, 28, *OAK_PLANK)
    fu.rug(b, 47, 20, 58, 25, Y, 14, border=15)
    # long table: 10 x 2 top slabs + tablecloth
    b.F(48, Y, 22, 57, Y, 23, 'wooden_slab', 13)
    # chairs every other block on both sides (clone doubling: 1 pair -> 5 pairs)
    b.S(48, Y, 21, 'dark_oak_stairs', stairs(N))
    b.S(48, Y, 24, 'dark_oak_stairs', stairs(S))
    b.C(48, Y, 21, 49, Y, 24, 50, Y, 21)
    b.C(48, Y, 21, 51, Y, 24, 52, Y, 21)
    b.C(48, Y, 21, 49, Y, 24, 56, Y, 21)
    b.F(48, Y + 1, 22, 57, Y + 1, 23, 'carpet', 0)
    # heads of the table
    fu.armchair(b, 47, Y, 22, E)
    fu.armchair(b, 58, Y, 23, W)
    b.S(47, Y, 23, 'dark_oak_stairs', stairs(W))
    b.S(58, Y, 22, 'dark_oak_stairs', stairs(E))
    # candelabras and centrepieces
    for x in (49, 52, 55):
        b.S(x, Y + 2, 22, 'brewing_stand')
    b.S(53, Y + 2, 23, 'cake')
    # sideboard on the north wall
    b.F(51, Y, 16, 57, Y, 16, 'wooden_slab', 13)
    for x in (52, 56):
        fu.pot(b, x, Y + 1, 16, 'red_flower', 4)
    b.S(54, Y + 1, 16, 'cake')
    # fireplace (flue in the east exterior chimney)
    b.fires += fu.fireplace(b, 61, F1, 25, W, width=3, depth=3)
    # china cabinets
    fu.wardrobe(b, 45, Y, 28, E, SPRUCE_PLANK)
    fu.wardrobe(b, 60, Y, 17, W, SPRUCE_PLANK)
    # chandeliers
    fu.chandelier(b, 50, 22, F1_CEIL, drop=2, wide=True)
    fu.chandelier(b, 54, 22, F1_CEIL, drop=2, wide=True)
    b.F(45, F1_CEIL, 19, 60, F1_CEIL, 19, *DO_PLANK)
    b.F(45, F1_CEIL, 26, 60, F1_CEIL, 26, *DO_PLANK)


def kitchen(b):
    b.section = 'F1 kitchen + pantry'
    checker(b, 45, 31, 60, 39, F1, white=('double_stone_slab', 8), black=('stonebrick', 0))
    # cooking hearth on the south wall (exterior chimney)
    b.fires += fu.fireplace(b, 50, F1, 40, N, width=3, depth=3, mantel='stone_brick_stairs')
    b.S(50, Y, 38, 'cauldron', 2)
    # counters: west wall with ovens, north wall with the sink
    fu.counter(b, 45, Y, 35, 45, 39, E)
    b.F(45, Y, 37, 45, Y, 38, 'furnace', wallmount(E))
    b.F(46, Y, 37, 46, Y, 38, 'air')
    fu.counter(b, 45, Y, 31, 50, 31, S)
    fu.counter(b, 52, Y, 31, 54, 31, S)
    b.S(47, Y, 31, 'cauldron', 3)
    b.S(47, Y, 32, 'air')
    b.S(47, Y + 1, 31, 'tripwire_hook', 0)
    b.S(45, Y, 32, 'crafting_table')
    # kitchen island
    b.F(49, Y, 34, 54, Y, 35, 'double_stone_slab', 8)
    b.S(49, Y, 34, 'crafting_table')
    b.S(54, Y, 35, 'crafting_table')
    b.S(51, Y + 1, 34, 'cake')
    fu.pot(b, 52, Y + 1, 35, 'brown_mushroom', 0)
    fu.pot(b, 53, Y + 1, 34, 'red_mushroom', 0)
    b.F(50, Y, 36, 53, Y, 36, 'oak_stairs', stairs(S))
    # shelves with herbs, hanging lanterns
    b.F(56, Y + 2, 31, 60, Y + 2, 31, 'wooden_slab', 8)
    for x in (56, 58, 60):
        fu.pot(b, x, Y + 3, 31, 'tallgrass', 2)
    b.F(57, Y, 31, 59, Y, 31, 'chest', wallmount(S))
    b.F(50, F1_CEIL, 33, 53, F1_CEIL, 33, *GLOW)
    b.S(47, F1_CEIL, 37, *GLOW)
    b.S(58, F1_CEIL, 33, *GLOW)
    # pantry (mx 56..60, mz 35..39)
    b.F(56, F1, 35, 60, F1, 39, 'cobblestone')
    b.F(60, Y, 35, 60, Y + 2, 39, 'log', 4)            # barrels
    b.F(56, Y, 39, 59, Y, 39, 'hay_block')
    b.F(56, Y + 1, 39, 57, Y + 1, 39, 'melon_block')
    b.F(58, Y + 1, 39, 59, Y + 1, 39, 'pumpkin', 2)
    fu.chest(b, 56, Y, 35, E, [('bread', 16), ('apple', 12), ('cooked_beef', 8), ('sugar', 10)])
    b.F(56, Y + 2, 35, 59, Y + 2, 35, 'wooden_slab', 8)
    b.S(57, Y + 3, 35, 'cake')
    b.S(58, F1_CEIL, 37, *GLOW)
    b.S(59, Y + 1, 36, 'wool', 12)                      # flour sacks
    b.S(59, Y, 36, 'wool', 12)


def back_stairs(b):
    """Switchback service stair, basement -> F1 -> F2 -> F3 (shaft mx 55..60, mz 8..14)."""
    b.section = 'back stairs'
    b.F(55, -4, 8, 60, 22, 14, 'air')
    b.F(54, -4, 8, 54, 22, 14, *WALL)
    b.F(55, -4, 15, 60, 22, 15, *WALL)
    # landings / floor slabs
    b.F(55, 2, 9, 57, 2, 14, *WALL)
    b.F(58, 1, 11, 60, 2, 14, *WALL)
    b.F(55, F2_CEIL - 7, 8, 57, F2, 14, *WALL)          # F2 slab lane A (y 9..10)
    b.F(58, F1_CEIL, 13, 60, F2, 14, *WALL)
    b.F(55, F2_CEIL, 11, 60, F3, 14, *WALL)             # F3 landing (y 16..17)
    # lane A flights (ascending north) with solid wedges, lane B (ascending south)
    for base in (-5, F1, F2):
        y0 = base + 1
        b.F(55, y0, 9, 57, y0, 11, *WALL)
        b.F(55, y0 + 1, 9, 57, y0 + 1, 10, *WALL)
        b.F(55, y0 + 2, 9, 57, y0 + 2, 9, *WALL)
        for k, z in enumerate((12, 11, 10, 9)):
            b.F(55, y0 + k, z, 57, y0 + k, z, 'stone_brick_stairs', stairs(N))
        b.F(55, y0 + 3, 8, 60, y0 + 3, 8, *WALL)       # mid landing
    b.F(55, -4, 8, 60, -2, 8, *WALL)
    b.F(55, 3, 8, 60, 5, 8, *WALL)
    b.F(55, 11, 8, 60, 13, 8, *WALL)
    # lane B: basement->F1 (2 steps), F1->F2 (4 steps), F2->F3 (2 steps)
    b.F(58, -4, 9, 60, 0, 12, *WALL)
    b.F(58, 0, 9, 60, 0, 9, 'stone_brick_stairs', stairs(S))
    b.F(58, 1, 10, 60, 1, 10, 'stone_brick_stairs', stairs(S))
    for k, z in enumerate((9, 10, 11, 12)):
        b.F(58, 7 + k, z, 60, 7 + k, z, 'stone_brick_stairs', stairs(S))
    b.F(58, 15, 9, 60, 15, 9, 'stone_brick_stairs', stairs(S))
    b.F(58, 16, 10, 60, 16, 10, 'stone_brick_stairs', stairs(S))
    # railings
    b.F(55, 18, 11, 57, 18, 11, 'nether_brick_fence')
    b.F(55, 11, 13, 57, 11, 13, 'air')
    # doors to each floor's corridor and lights
    for y in (-4, 11, 18):
        b.door(54, y, 13, E, blk='spruce_door')
    for y in (-2, 5, 13, 20):
        b.S(60, y, 14, 'torch', torch(N))
        b.S(55, y, 14, 'torch', torch(N))


def lights(b):
    """Extra light: glowstone hidden under rugs/runners and a few sconces (validated for spawns)."""
    b.section = 'F1 lighting'
    G = GLOW
    under_rugs = [(27, 24), (34, 24), (27, 32), (34, 32),            # salon
                  (47, 20), (58, 20), (47, 25), (58, 25),            # dining
                  (47, 3), (51, 7), (10, 3), (14, 7),                 # drawing room, study
                  (3, 19), (12, 19), (3, 31), (12, 31),              # library
                  (2, 37), (7, 38),                                   # secret study
                  (19, 12), (20, 24), (19, 33), (42, 12), (41, 24), (42, 33)]  # hall runners
    for (x, z) in under_rugs:
        b.S(x, F1, z, *G)
    for (x, z) in ((24, 37), (37, 37), (24, 42), (37, 42)):         # under conservatory shrubs
        b.S(x, F1, z, *G)
    sconces = [(28, 6, 20, S), (33, 6, 20, S), (28, 6, 35, N), (33, 6, 35, N),   # salon
               (46, 5, 16, S), (59, 5, 16, S), (46, 5, 29, N), (55, 5, 29, N), (59, 5, 29, N),  # dining
               (0, 5, 1, E), (6, 5, 5, W), (61, 5, 1, W), (55, 5, 5, E),              # towers
               (45, 6, 34, E), (60, 6, 31, W), (6, 5, 12, W),                         # kitchen, bath
               (23, 9, 14, E), (38, 9, 14, W), (23, 9, 17, E), (38, 9, 17, W),        # landing
               (55, 0, 8, E), (60, 0, 8, W), (55, 7, 8, S), (60, 7, 8, S), (55, 15, 8, S), (60, 15, 8, S),
               (16, 5, 38, W), (1, 5, 21, E), (1, 5, 29, E), (15, 5, 33, N), (46, 5, 8, N), (52, 5, 1, S),
               (8, 5, 8, N), (16, 5, 2, W)]
    for (x, y, z, f) in sconces:
        b.S(x, y, z, 'torch', torch(f))
