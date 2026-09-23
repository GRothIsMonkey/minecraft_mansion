"""Basement (floor y=-5, air y=-4..0, ceiling y=1) and the secret underground areas.

`structure()` runs BEFORE the floor-1 interiors (they cut the secret-study stair
and the library door channel into it); `late()` runs AFTER them (the hatch in
the foyer cubby floor).
"""
from mansion_base import *   # noqa: F401,F403
from engine import stairs, trapdoor, torch, wallmount, lever, repeater, N, S, E, W
import furniture as fu

Y = BF + 1   # -4, feet level
TOP = B_TOP  # 0


def structure(b):
    layout(b)
    archive(b)
    crypt(b)
    storage_hall(b)
    cistern(b)
    east_rooms(b)
    wine_secret(b)
    redstone_room(b)
    vault(b)
    tunnel(b)


def layout(b):
    b.section = 'basement layout'
    # solid (unexcavated) masses around the hidden redstone room and the vault
    b.F(18, Y, 1, 44, TOP, 13, *WALL)
    b.F(1, Y, 29, 17, TOP, 39, *WALL)
    # main corridor (mz 15..16) + room walls
    b.F(1, Y, 14, 53, TOP, 14, *WALL)
    b.F(1, Y, 17, 60, TOP, 17, *WALL)
    b.F(17, Y, 18, 17, TOP, 28, *WALL)
    b.F(44, Y, 18, 44, TOP, 39, *WALL)
    b.F(45, Y, 30, 60, TOP, 30, *WALL)
    b.F(54, Y, 1, 54, TOP, 7, *WALL)
    b.F(17, Y, 29, 43, TOP, 29, *WALL)
    b.F(17, Y, 1, 17, TOP, 13, *WALL)
    # corridor floor, opening to the storage room / back stairs
    b.F(1, BF, 15, 53, BF, 16, 'stone', 6)
    b.F(53, BF, 13, 53, BF, 14, 'stone', 6)
    b.F(53, Y, 13, 53, TOP, 14, 'air')
    for x in range(3, 54, 8):
        b.S(x, Y + 2, 16, 'torch', torch(N))
        b.S(x + 4, Y + 2, 15, 'torch', torch(S))
    # doorways off the corridor
    for (x, z, f) in ((8, 14, N), (38, 17, S), (24, 17, S), (8, 17, S), (50, 17, S), (48, 14, N)):
        b.door(x, Y, z, f, blk='spruce_door')
    b.door(26, Y, 29, S, blk='spruce_door')       # storage hall -> cistern
    b.door(52, Y, 30, S, blk='spruce_door')       # wine cellar -> utility room
    b.door(54, Y, 4, E, blk='spruce_door')        # storage -> under the NE tower


def archive(b):
    b.section = 'basement archive'
    b.F(1, BF, 1, 16, BF, 13, *SPRUCE_PLANK)
    for z in (3, 6, 9):
        b.F(3, Y, z, 14, Y + 2, z, 'bookshelf')
    b.F(1, Y, 1, 1, Y + 3, 13, 'bookshelf')
    b.F(2, Y, 12, 5, Y, 13, 'wooden_slab', 9)
    fu.chair(b, 3, Y, 11, S, 'spruce_stairs')
    for x in (7, 10, 13):
        fu.chest(b, x, Y, 1, S, [('paper', 24), ('map', 1)] if x == 10 else None)
    for (gx, gz) in ((5, 2), (11, 5), (5, 8), (11, 11), (15, 7), (8, 13)):
        b.S(gx, BF, gz, *GLOW)
    b.S(2, TOP, 2, 'web')


def crypt(b):
    b.section = 'basement family crypt'
    b.F(1, BF, 18, 16, BF, 28, *CRACK)
    for (x, z) in ((3, 20), (3, 25), (13, 20), (13, 25)):
        b.F(x, Y, z, x + 1, Y, z + 1, *WALL)                     # stone coffins
        b.F(x, Y + 1, z, x + 1, Y + 1, z + 1, 'stone_slab', 5)
        fu.skull(b, x, Y + 2, z, 0, rot=4)
    b.F(7, Y, 27, 10, Y, 28, *CHISEL)                            # the family tomb
    b.F(7, Y + 1, 27, 10, Y + 1, 28, 'stone_slab', 13)
    fu.sign(b, 8, Y, 26, N, 'Here lies', 'Lady Ashgrove', '1789 - 1822', '')
    b.S(8, Y + 2, 27, 'flower_pot', 0, '{Item:red_flower,Data:0}')
    for (x, z) in ((6, 19), (11, 19), (6, 24), (11, 24)):
        b.S(x, Y, z, 'cobblestone_wall')
        b.S(x, Y + 1, z, 'torch', 5)
    for (wx, wz) in ((1, 18), (16, 18), (1, 28), (16, 28)):
        b.S(wx, TOP, wz, 'web')
    b.S(8, BF, 22, *GLOW)


def storage_hall(b):
    b.section = 'basement storage hall'
    b.F(18, BF, 18, 43, BF, 28, 'stone', 5)
    for x in (20, 24, 36, 40):
        b.F(x, Y, 19, x + 1, Y + 1, 26, 'log', 4)                # crate stacks
    for x in (28, 31):
        fu.chest(b, x, Y, 19, S, [('wheat', 32), ('potato', 24)] if x == 28 else [('apple', 16)])
    b.S(33, Y, 19, 'pumpkin', 0)
    b.F(28, Y, 27, 33, Y, 28, 'hay_block')
    b.F(28, Y + 1, 28, 33, Y + 1, 28, 'melon_block')
    b.F(18, Y + 2, 18, 43, Y + 2, 18, 'wooden_slab', 8)          # shelf along the north wall
    b.F(29, Y, 22, 32, Y, 24, 'crafting_table')                  # work tables
    b.S(30, Y + 1, 23, 'anvil', 0)
    b.S(31, Y + 1, 23, 'anvil', 5)
    for (gx, gz) in ((22, 23), (38, 23), (30, 20), (30, 26), (26, 27), (35, 27), (19, 27), (42, 27)):
        b.S(gx, BF, gz, *GLOW)


def cistern(b):
    """Vaulted rain cistern under the salon (mx 18..43, mz 30..39) with a causeway."""
    b.section = 'basement cistern'
    b.F(18, BF, 30, 43, BF, 39, *WALL)
    b.F(19, BF - 1, 33, 42, BF - 1, 38, *WALL)
    b.F(19, BF, 33, 42, BF, 38, 'water')
    b.F(30, BF, 33, 31, BF, 38, 'stone_slab', 13)                # causeway to the far side
    for (sx, sz) in ((21, 35), (25, 37), (36, 34), (40, 36)):
        b.S(sx, BF - 1, sz, 'sea_lantern')                       # glowing through the water
    for x in (23, 38):
        for z in (35, 36):
            b.F(x, BF, z, x, TOP, z, *WALL)
            b.S(x, Y + 2, z, *CHISEL)
    b.F(18, TOP, 30, 43, TOP, 30, 'stone_brick_stairs', stairs(S, True))
    b.F(18, Y, 39, 43, Y, 39, 'stone_brick_stairs', stairs(S))  # a bench along the south wall
    b.S(30, Y, 39, *CHISEL)
    b.S(31, Y, 39, *CHISEL)
    for (gx, gz) in ((20, 31), (41, 31), (26, 31), (35, 31)):
        b.S(gx, BF, gz, *GLOW)
    for x in (22, 39):
        b.S(x, Y + 1, 30, 'torch', torch(S))
    b.S(18, TOP, 39, 'web')


def east_rooms(b):
    b.section = 'basement east: storage, wine cellar, utility'
    # storage (mx 45..53, mz 1..13) and under the NE tower (mx 55..60, mz 1..7)
    b.F(45, BF, 1, 60, BF, 13, 'cobblestone')
    b.F(46, Y, 1, 52, Y + 1, 2, 'log', 8)
    for x in (47, 50):
        fu.chest(b, x, Y, 5, S, [('coal', 32)] if x == 47 else None)
    b.F(47, Y, 8, 52, Y + 2, 9, 'hay_block')
    b.F(55, Y, 1, 60, Y + 1, 2, 'log', 4)
    for x in (56, 59):
        fu.chest(b, x, Y, 6, N, [('iron_ingot', 9)] if x == 59 else None)
    for (gx, gz) in ((49, 3), (49, 11), (57, 4), (52, 6), (46, 12)):
        b.S(gx, BF, gz, *GLOW)
    # wine cellar (mx 45..60, mz 18..29)
    b.F(45, BF, 18, 60, BF, 29, *WALL)
    b.F(46, BF, 19, 59, BF, 28, 'stone', 5)
    b.F(60, Y, 18, 60, TOP, 29, 'log', 4)                          # barrel wall (east)
    for z in (20, 23, 26):
        b.F(47, Y, z, 56, Y + 1, z, 'log', 4)                      # barrel racks
        b.F(47, Y + 2, z, 56, Y + 2, z, 'wooden_slab', 8)
        b.F(48, Y + 3, z, 55, Y + 3, z, 'brewing_stand')           # bottles
    b.F(46, Y, 28, 49, Y, 28, 'wooden_slab', 13)                   # tasting table
    fu.chair(b, 47, Y, 27, S, 'dark_oak_stairs')
    fu.chair(b, 48, Y, 27, S, 'dark_oak_stairs')
    b.S(46, Y + 1, 28, 'brewing_stand')
    for (gx, gz) in ((51, 19), (51, 22), (51, 25), (51, 28), (58, 21), (58, 27), (45, 23)):
        b.S(gx, BF, gz, *GLOW)
    for (wx, wz) in ((45, 18), (59, 29)):
        b.S(wx, TOP, wz, 'web')
    # utility / furnace room (mx 45..60, mz 31..39)
    b.F(45, BF, 31, 60, BF, 39, *WALL)
    b.F(46, Y, 39, 55, Y + 1, 39, 'furnace', wallmount(N))         # furnace bank
    b.F(46, Y + 2, 39, 55, Y + 2, 39, *WALL)
    b.F(57, Y, 38, 60, Y + 1, 39, 'coal_block')
    b.F(57, Y, 31, 59, Y + 2, 33, 'iron_block')                     # the boiler
    b.S(58, Y + 3, 32, 'cauldron', 3)
    b.F(58, Y + 4, 32, 58, TOP, 32, 'iron_bars')
    b.F(46, Y, 31, 48, Y, 31, 'crafting_table')
    b.S(50, Y, 31, 'anvil', 0)
    fu.chest(b, 45, Y, 34, E, [('coal', 64), ('coal', 64), ('iron_ingot', 16)])
    b.S(52, Y, 35, 'cauldron', 3)
    for (gx, gz) in ((50, 33), (50, 37), (55, 35), (47, 35), (60, 35)):
        b.S(gx, BF, gz, *GLOW)


def wine_secret(b):
    """The 'loose barrel': floor-lever tap drops a barrel into the floor -> smuggler's stash."""
    b.section = 'wine cellar secret door + stash'
    zd = 24
    # the stash, dug into the ground outside the foundation (mx 62..66, mz 21..27),
    # entirely below the lawn (ceiling y=-2, grass at y=-1 untouched)
    b.F(61, -6, 20, 67, -2, 28, *WALL)
    b.F(62, Y, 21, 66, Y + 1, 27, 'air')
    b.F(62, BF, 21, 66, BF, 27, 'stone', 5)
    # doorway through the barrel wall (x=60) and the foundation wall (x=61)
    b.F(60, Y, zd, 61, Y + 1, zd, 'air')
    # mechanism bed under the cellar floor
    b.F(56, BF - 2, zd - 1, 60, BF - 1, zd + 1, *WALL)
    # lever first, then the dust (computes its power when placed), then the piston
    b.S(57, Y, zd, 'lever', 5 + 8)                       # the 'tap', ON = closed
    b.F(57, BF - 1, zd, 59, BF - 1, zd, 'redstone_wire')
    b.S(60, BF, zd, 'log', 4)                            # the loose barrel (sits on the piston)
    b.S(60, BF - 1, zd, 'sticky_piston', 1)
    b.X(60, BF - 1, zd, 'sticky_piston', 9)
    b.X(60, BF, zd, 'piston_head', 9)
    b.X(60, Y, zd, 'log', 4)
    # upper half: passable wall sign behind a painting
    b.S(60, Y + 1, zd, 'wall_sign', wallmount(S))   # hangs on the barrel at z-1
    b.late_paintings.append((59, Y + 1, zd, W, 'Plant', 1, 1))
    # stash contents
    fu.chest(b, 66, Y, 22, W, [('diamond', 5), ('emerald', 12), ('gold_ingot', 20), ('potion', 3)])
    fu.chest(b, 66, Y, 26, W, [('record_wait', 1), ('saddle', 1), ('name_tag', 2)])
    b.F(63, Y, 27, 65, Y + 1, 27, 'log', 8)
    b.S(62, Y, 21, 'brewing_stand')
    b.S(64, -2, 24, *GLOW)
    b.S(62, Y + 1, 27, 'web')
    fu.sign(b, 65, Y + 1, 21, S, 'Finest', 'Contraband', '- Ashgrove', '')


def redstone_room(b):
    """Hidden engineering room under the grand staircase (mx 26..35, mz 6..13)."""
    b.section = 'secret redstone room'
    b.F(26, Y, 6, 35, TOP, 13, 'air')
    b.F(26, BF, 6, 35, BF, 13, 'stone', 6)
    # ladder up to the hatch in the stair cubby (top rung + hatch are placed in late())
    b.F(31, Y, 12, 31, TOP, 12, *WALL)
    b.F(30, Y, 12, 30, 1, 12, 'ladder', wallmount(W))
    # working lamp panel: floor lever -> dust on top of a row of lamps
    b.F(27, Y, 6, 34, Y, 6, 'redstone_lamp')
    b.S(26, Y, 6, *CHISEL)
    b.S(26, Y + 1, 6, 'lever', 5 + 8)
    b.F(27, Y + 1, 6, 34, Y + 1, 6, 'redstone_wire')
    for x in range(27, 35):
        b.X(x, Y, 6, 'lit_redstone_lamp')                # what the game does: the dust lights them
    # decorative circuitry
    b.S(27, Y, 9, 'redstone_wire')
    b.F(28, Y, 9, 33, Y, 9, 'unpowered_repeater', repeater(E, 2))
    b.S(34, Y, 9, 'unpowered_comparator', repeater(E))
    b.S(35, Y, 9, 'chest', wallmount(W))
    b.S(29, Y, 11, 'redstone_torch', 5)
    b.F(30, Y, 11, 33, Y, 11, 'redstone_wire')
    b.S(35, Y, 12, 'command_block', 0,
        '{Command:"tellraw @p {\\"text\\":\\"*click* The old machine whirs, then falls silent.\\",'
        '\\"color\\":\\"gray\\",\\"italic\\":true}"}')
    b.S(35, Y + 1, 12, 'stone_pressure_plate')
    b.F(26, Y, 12, 26, Y, 13, 'noteblock')
    b.S(34, Y, 13, 'dispenser', wallmount(W))
    b.S(35, Y, 13, 'dropper', wallmount(W))
    fu.sign(b, 32, Y + 1, 13, N, 'Laboratory of', 'Lord Ashgrove', 'Do not touch', 'the levers!')
    b.F(26, Y, 8, 26, Y + 2, 10, 'bookshelf')
    fu.chair(b, 32, Y, 7, S, 'spruce_stairs')
    for (gx, gz) in ((29, 9), (32, 11), (27, 12)):
        b.S(gx, 1, gz, 'sea_lantern')


def vault(b):
    """Hidden vault below the secret study; reached from the study's secret stair."""
    b.section = 'secret vault'
    # antechamber at the bottom of the secret stair (mx 1..8, mz 36..39) + stairwell
    b.F(1, Y, 36, 8, TOP, 39, 'air')
    b.F(1, BF, 36, 8, BF, 39, *CRACK)
    b.F(9, Y, 38, 15, TOP, 39, 'air')              # the study's stair is built into this later
    b.S(1, TOP, 36, 'web')
    b.S(4, BF, 38, *GLOW)
    b.S(7, BF, 37, *GLOW)
    b.S(8, Y + 1, 39, 'torch', torch(N))
    # the vault (mx 1..14, mz 30..34): obsidian shell, treasure
    b.F(0, BF, 29, 15, TOP, 35, 'obsidian')
    b.F(1, Y, 30, 14, TOP - 1, 34, 'air')
    b.F(1, BF, 30, 14, BF, 34, 'iron_block')
    b.F(2, BF, 31, 13, BF, 33, 'stone', 6)
    b.F(1, Y, 30, 1, TOP - 1, 34, 'gold_block')
    b.F(14, Y, 30, 14, TOP - 1, 34, 'iron_block')
    b.F(2, Y, 30, 13, Y, 30, 'gold_block')
    b.F(2, Y + 1, 30, 13, Y + 1, 30, 'iron_bars')
    b.S(7, Y, 30, 'emerald_block')
    b.S(8, Y, 30, 'diamond_block')
    for x in (3, 10, 12):
        fu.chest(b, x, Y, 34, N, [('gold_ingot', 64), ('diamond', 8), ('emerald', 16)] if x == 10
                 else [('gold_nugget', 64), ('iron_ingot', 32)])
    for (gx, gz) in ((4, 32), (11, 32)):
        b.S(gx, TOP, gz, 'sea_lantern')
    # iron vault door with levers on both sides
    b.door(5, Y, 35, N, blk='iron_door')
    b.S(4, Y + 1, 36, 'lever', lever(S))
    b.S(6, Y + 1, 34, 'lever', lever(N))


def tunnel(b):
    """Escape hatch in the vault floor -> ladder -> tunnel south -> hideout -> dry well."""
    b.section = 'secret escape tunnel'
    # shaft + tunnel shells (stone brick, so real-world gravel/water cannot leak in)
    b.F(6, -11, 30, 8, -6, 32, *WALL)
    b.F(6, -11, 32, 8, -8, 50, *WALL)
    b.F(7, -10, 31, 7, BF, 31, 'air')
    b.F(7, -10, 31, 7, BF, 31, 'ladder', wallmount(S))
    b.S(7, Y, 31, 'trapdoor', trapdoor(S))          # hatch on the vault floor (hinged on the emerald block)
    b.F(7, -10, 32, 7, -9, 50, 'air')
    for z in (36, 43):
        b.S(7, -8, z, *GLOW)
    # hideout (mx 3..11, mz 51..55)
    b.F(2, -11, 50, 12, -6, 56, *WALL)
    b.F(3, -10, 51, 11, -7, 55, 'air')
    b.F(3, -11, 51, 11, -11, 55, 'cobblestone')
    b.F(7, -10, 50, 7, -9, 50, 'air')
    fu.bed(b, 4, -10, 52, N)
    fu.chest(b, 11, -10, 53, W, [('bread', 32), ('cooked_porkchop', 16), ('torch', 32), ('map', 1),
                                 ('diamond_sword', 1)])
    b.S(3, -10, 55, 'crafting_table')
    b.S(11, -10, 55, 'furnace', wallmount(W))
    b.S(9, -7, 52, *GLOW)
    b.S(4, -7, 55, *GLOW)
    b.S(3, -7, 51, 'web')
    b.S(11, -7, 51, 'web')
    fu.sign(b, 6, -9, 55, N, 'Escape route:', 'climb the', 'old well', '')
    # the dry well in the rear garden (shaft at mx 7, mz 54)
    b.F(7, -10, 55, 7, -7, 55, *WALL)                     # ladder backing inside the hideout
    b.F(6, -6, 53, 8, -2, 55, *WALL)
    b.F(6, -1, 53, 8, 0, 55, 'cobblestone')
    b.F(7, -10, 54, 7, 0, 54, 'air')
    b.F(7, -10, 54, 7, 0, 54, 'ladder', wallmount(N))
    for (px, pz) in ((6, 53), (8, 53), (6, 55), (8, 55)):
        b.F(px, 1, pz, px, 2, pz, 'spruce_fence')
    b.F(5, 3, 52, 9, 3, 56, 'wooden_slab', 1)
    b.F(6, 4, 53, 8, 4, 55, 'wooden_slab', 1)
    b.S(7, 3, 54, 'spruce_fence')                         # the winch post


def late(b):
    """Pieces cut through floor-1 surfaces (must run after the F1 interiors)."""
    b.section = 'secret hatches'
    b.S(30, F1, 12, 'ladder', wallmount(W))                 # top rung, level with the cubby floor
    b.S(30, F1 + 1, 12, 'trapdoor', trapdoor(S))            # hatch lying on the cubby floor
