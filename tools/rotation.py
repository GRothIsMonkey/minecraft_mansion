"""Quarter-turn rotation of the mansion for the server-console edition.

The design (and its voxel model) lives in LOCAL coordinates: the legacy
command block at (0, 0, 0), front facing north (-Z), house toward +Z.  The
console edition turns everything 90 degrees CLOCKWISE seen from above
(north -> east, east -> south, south -> west, west -> north) and places it
at absolute world coordinates:

    world block  (wx, wy, wz) = (KX - lz, KY + ly, KZ + lx)
    world point  (px, py, pz) -> (KX + 1 - pz, KY + py, KZ + px)

so the front doors face EAST (+X) and the house extends WEST (-X).

Block metadata uses the pre-1.13 numeric data values of Minecraft 1.8.  Every
orientation-dependent block used by the design (and the others a 1.8 build is
likely to contain) is remapped here; the tables follow the decompiled 1.8.9
block classes.
"""
import re

import numpy as np

from blockids import BLOCK_IDS, ID_NAMES
from engine import N, S, E, W, UP, DOWN, SX0, SX1, SY0, SZ0, SZ1

# ---------------------------------------------------------------- placement --
# Front doors: mansion (30,3,0)+(31,3,0) = local (42..43, 3, 26); their plane is
# local z=26 and the mirror axis of the design is local x=43.0.
ENTRANCE = (-251, 73, 267)       # user's reference point (feet level on the lawn)
KX = ENTRANCE[0] + 26            # local z=26 (door plane)   -> world x = -251
KY = ENTRANCE[1]                 # local y=0 (lawn feet)     -> world y =   73
KZ = ENTRANCE[2] - 43            # local x=43.0 (mirror axis)-> world z = 267.0

CW = {N: E, E: S, S: W, W: N, UP: UP, DOWN: DOWN}


def block(lx, ly, lz):
    return (KX - lz, KY + ly, KZ + lx)


def point(px, py, pz):
    return (KX + 1 - pz, KY + py, KZ + px)


def to_local(wx, wy, wz):
    return (wz - KZ, wy - KY, KX - wx)


def box(x1, y1, z1, x2, y2, z2):
    """Rotate a local box -> world (min corner, max corner)."""
    a, b = block(x1, y1, z1), block(x2, y2, z2)
    return (min(a[0], b[0]), min(a[1], b[1]), min(a[2], b[2]),
            max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2]))


# ------------------------------------------------------------ metadata ------
def _names(*suffix_or_names):
    out = set()
    for n in suffix_or_names:
        if n.startswith('*'):
            out |= {k for k in BLOCK_IDS if k.endswith(n[1:])}
        else:
            out.add(n)
    return out


STAIRS = _names('*_stairs')
DOORS = _names('wooden_door', 'iron_door', 'spruce_door', 'birch_door', 'jungle_door', 'acacia_door',
               'dark_oak_door')
TRAPDOORS = _names('trapdoor', 'iron_trapdoor')
TORCHES = _names('torch', 'redstone_torch', 'unlit_redstone_torch')
BUTTONS = _names('stone_button', 'wooden_button')
FACING6 = _names('ladder', 'wall_sign', 'wall_banner', 'chest', 'trapped_chest', 'ender_chest', 'furnace',
                 'lit_furnace', 'dispenser', 'dropper', 'hopper', 'piston', 'sticky_piston', 'piston_head',
                 'piston_extension', 'skull')
HORIZ = _names('bed', '*fence_gate', 'pumpkin', 'lit_pumpkin', 'unpowered_repeater', 'powered_repeater',
               'unpowered_comparator', 'powered_comparator', 'end_portal_frame', 'anvil', 'cocoa',
               'tripwire_hook')
AXIS_LOGS = _names('log', 'log2', 'hay_block')
STANDING16 = _names('standing_sign', 'standing_banner')
RAILS_POWERED = _names('golden_rail', 'detector_rail', 'activator_rail')
MUSHROOM = _names('brown_mushroom_block', 'red_mushroom_block')

STAIR_CW = {0: 2, 1: 3, 2: 1, 3: 0}              # E W S N  ->  S N W E
TRAP_CW = {0: 3, 1: 2, 2: 0, 3: 1}               # N S W E  ->  E W N S
TORCH_CW = {0: 0, 1: 3, 2: 4, 3: 2, 4: 1, 5: 5}  # E W S N  ->  S N W E (0 = button on ceiling)
LEVER_CW = {1: 3, 2: 4, 3: 2, 4: 1, 5: 6, 6: 5, 7: 0, 0: 7}   # floor/ceiling levers swap X/Z
FACING6_CW = {0: 0, 1: 1, 2: 5, 3: 4, 4: 2, 5: 3, 6: 6, 7: 7}  # N S W E  ->  E W N S
RAIL_CW = {0: 1, 1: 0, 2: 5, 3: 4, 4: 2, 5: 3, 6: 7, 7: 8, 8: 9, 9: 6}
MUSH_CW = {1: 3, 2: 6, 3: 9, 4: 2, 6: 8, 7: 1, 8: 4, 9: 7}


def rot_meta(name, m):
    """Metadata of `name` after one clockwise quarter turn."""
    m = int(m)
    if name in STAIRS:
        return STAIR_CW[m & 3] | (m & 12)
    if name in DOORS:
        return m if m & 8 else ((m & 3) + 1) % 4 | (m & 4)
    if name in TRAPDOORS:
        return TRAP_CW[m & 3] | (m & 12)
    if name in TORCHES:
        return TORCH_CW.get(m, m)
    if name in BUTTONS:
        return TORCH_CW[m & 7] | (m & 8) if (m & 7) in TORCH_CW else m
    if name == 'lever':
        return LEVER_CW[m & 7] | (m & 8)
    if name in FACING6:
        return FACING6_CW[m & 7] | (m & 8)
    if name in HORIZ:
        return ((m & 3) + 1) % 4 | (m & 12)
    if name in AXIS_LOGS:
        ax = m & 12
        return (m & 3) | {0: 0, 4: 8, 8: 4, 12: 12}[ax]
    if name == 'quartz_block':
        return {3: 4, 4: 3}.get(m, m)
    if name in STANDING16:
        return (m + 4) % 16
    if name == 'vine':
        return ((m << 1) | (m >> 3)) & 15
    if name == 'rail':
        return RAIL_CW.get(m, m)
    if name in RAILS_POWERED:
        return (RAIL_CW[m & 7] if (m & 7) < 6 else m & 7) | (m & 8)
    if name in MUSHROOM:
        return MUSH_CW.get(m, m)
    if name == 'portal':
        return {1: 2, 2: 1}.get(m, m)
    if name == 'double_plant':
        return (m & 12) | ((m & 3) + 1) % 4 if m & 8 else m
    return m


def rot_nbt(name, meta, nbt):
    """Tile-entity NBT after the turn (floor skulls keep their facing in Rot:0..15)."""
    if nbt and name == 'skull' and (meta & 7) == 1:
        nbt = re.sub(r'Rot:(\d+)', lambda mo: 'Rot:%d' % ((int(mo.group(1)) + 4) % 16), nbt)
    return nbt


def rot_entity_nbt(entity, nbt):
    """Summon NBT after the turn: hanging Facing (S,W,N,E = 0..3) +1, yaw +90."""
    if not nbt:
        return nbt
    if entity in ('Painting', 'ItemFrame'):
        nbt = re.sub(r'Facing:(\d)', lambda mo: 'Facing:%d' % ((int(mo.group(1)) + 1) % 4), nbt, count=1)
    if 'Rotation:[' in nbt:
        def yaw(mo):
            v = (float(mo.group(1)) + 90.0) % 360.0
            return 'Rotation:[%sf' % (('%d' % v) if v == int(v) else ('%g' % v))
        nbt = re.sub(r'Rotation:\[(-?[\d.]+)f', yaw, nbt, count=1)
    return nbt


# lookup table id*16+meta -> rotated meta (for rotating whole voxel models)
LUT = np.zeros((4096 * 16,), dtype=np.int8)
for _bid in range(4096):
    _name = ID_NAMES.get(_bid)
    for _m in range(16):
        LUT[_bid * 16 + _m] = rot_meta(_name, _m) if _name else _m


# -------------------------------------------------------- model rotation ----
# The rotated model uses the same array box as the design model.  Its frame
# ("rotated local", rx = RC - lz, rz = lx) maps onto world coordinates by a
# pure translation, so the validators in validate.py run on it unchanged.
RC = SX1 + SZ0                      # 96: lz in [-8,104]  ->  rx in [-8,104]
assert SX0 == SZ0 and SX1 == SZ1
OFF = (KX - RC, KY, KZ)             # world = rotated-local + OFF


def r_local(lx, ly, lz):
    """Design local -> rotated-local frame."""
    return (RC - lz, ly, lx)


def world_to_r(wx, wy, wz):
    return (wx - OFF[0], wy - OFF[1], wz - OFF[2])


def r_to_world(rx, ry, rz):
    return (rx + OFF[0], ry + OFF[1], rz + OFF[2])


class Frame:
    """Just enough of a Build for validate.py: ids/meta arrays in the rotated-local frame."""

    def __init__(self, ids, meta):
        self.ids, self.meta = ids, meta

    def get(self, x, y, z):
        i = (x - SX0, y - SY0, z - SZ0)
        return int(self.ids[i]), int(self.meta[i])


def rotate_arrays(ids, meta):
    """new[RC - lz, y, lx] = old[lx, y, lz] with the metadata remapped."""
    nid = np.ascontiguousarray(ids.transpose(2, 1, 0)[::-1, :, :])
    nme = np.ascontiguousarray(meta.transpose(2, 1, 0)[::-1, :, :]).astype(np.int32)
    nme = LUT[nid.astype(np.int32) * 16 + (nme & 15)].astype(np.int8)
    return nid, nme


def rotated_frame(b):
    ids, meta = rotate_arrays(b.ids, b.meta)
    return Frame(ids, meta)
