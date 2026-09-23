"""Static validation of the voxel model: supports, walkability, light, fire safety."""
from collections import deque

import numpy as np

from blockids import BLOCK_IDS as B, ID_NAMES
from engine import SX0, SY0, SZ0

# ------------------------------------------------------------ block classes --
NAMES = lambda *n: {B[x] for x in n}    # noqa: E731

STAIRS = {i for n, i in B.items() if n.endswith('_stairs')}
SLABS = NAMES('stone_slab', 'wooden_slab', 'stone_slab2')
DOORS = NAMES('wooden_door', 'iron_door', 'spruce_door', 'birch_door', 'jungle_door', 'acacia_door',
              'dark_oak_door')
FENCES = NAMES('fence', 'spruce_fence', 'birch_fence', 'jungle_fence', 'dark_oak_fence', 'acacia_fence',
               'nether_brick_fence', 'cobblestone_wall')
GATES = NAMES('fence_gate', 'spruce_fence_gate', 'birch_fence_gate', 'jungle_fence_gate',
              'dark_oak_fence_gate', 'acacia_fence_gate')
TRAPDOORS = NAMES('trapdoor', 'iron_trapdoor')
# no collision at all
PASSABLE = NAMES('air', 'torch', 'redstone_torch', 'unlit_redstone_torch', 'wall_sign', 'standing_sign',
                 'red_flower', 'yellow_flower', 'tallgrass', 'deadbush', 'sapling', 'double_plant',
                 'redstone_wire', 'rail', 'golden_rail', 'detector_rail', 'activator_rail',
                 'stone_pressure_plate', 'wooden_pressure_plate', 'light_weighted_pressure_plate',
                 'heavy_weighted_pressure_plate', 'stone_button', 'wooden_button', 'lever', 'ladder',
                 'vine', 'web', 'water', 'flowing_water', 'tripwire', 'tripwire_hook', 'reeds',
                 'brown_mushroom', 'red_mushroom', 'wall_banner', 'standing_banner', 'portal',
                 'carpet', 'snow_layer', 'waterlily', 'wheat', 'carrots', 'potatoes', 'nether_wart',
                 'pumpkin_stem', 'melon_stem', 'fire') | DOORS | GATES
CLIMB = NAMES('ladder', 'vine', 'water', 'flowing_water')
TRANSPARENT_FULL = NAMES('glass', 'stained_glass', 'glowstone', 'sea_lantern', 'leaves', 'leaves2', 'ice',
                         'slime', 'tnt', 'beacon', 'mob_spawner', 'redstone_block')
NONCUBE = (STAIRS | SLABS | DOORS | FENCES | GATES | TRAPDOORS | PASSABLE |
           NAMES('glass_pane', 'stained_glass_pane', 'iron_bars', 'chest', 'trapped_chest', 'ender_chest',
                 'bed', 'cauldron', 'brewing_stand', 'enchanting_table', 'flower_pot', 'skull', 'anvil',
                 'cake', 'end_portal_frame', 'daylight_detector', 'daylight_detector_inverted', 'hopper',
                 'unpowered_repeater', 'powered_repeater', 'unpowered_comparator', 'powered_comparator',
                 'piston_head', 'piston_extension', 'cactus', 'dragon_egg', 'soul_sand', 'farmland',
                 'water', 'lava', 'flowing_lava', 'cocoa'))
LIGHT = {B['glowstone']: 15, B['sea_lantern']: 15, B['lit_pumpkin']: 15, B['fire']: 15, B['lava']: 15,
         B['torch']: 14, B['lit_redstone_lamp']: 15, B['redstone_torch']: 7, B['beacon']: 15,
         B['lit_furnace']: 13, B['end_portal_frame']: 1, B['brewing_stand']: 1,
         B['brown_mushroom']: 1, B['ender_chest']: 7, B['dragon_egg']: 1}
FLAMMABLE = NAMES('planks', 'double_wooden_slab', 'wooden_slab', 'fence', 'spruce_fence', 'birch_fence',
                  'jungle_fence', 'dark_oak_fence', 'acacia_fence', 'fence_gate', 'spruce_fence_gate',
                  'birch_fence_gate', 'jungle_fence_gate', 'dark_oak_fence_gate', 'acacia_fence_gate',
                  'oak_stairs', 'spruce_stairs', 'birch_stairs', 'jungle_stairs', 'acacia_stairs',
                  'dark_oak_stairs', 'log', 'log2', 'leaves', 'leaves2', 'bookshelf', 'tnt', 'tallgrass',
                  'wool', 'vine', 'coal_block', 'hay_block', 'carpet', 'double_plant', 'red_flower',
                  'yellow_flower', 'deadbush')


def is_cube(bid):
    return bid not in NONCUBE


def normal_cube(bid):
    return is_cube(bid) and bid not in TRANSPARENT_FULL


def solid_top(bid, meta):
    if normal_cube(bid):
        return True
    if bid in SLABS and (meta & 8):
        return True
    if bid in STAIRS and (meta & 4):
        return True
    if bid in NAMES('double_stone_slab', 'double_wooden_slab', 'double_stone_slab2', 'hopper'):
        return True
    return False


class Model:
    def __init__(self, b):
        self.b = b
        self.ids = b.ids
        self.meta = b.meta
        self.sh = b.ids.shape

    def at(self, x, y, z):
        i, j, k = x - SX0, y - SY0, z - SZ0
        if 0 <= i < self.sh[0] and 0 <= j < self.sh[1] and 0 <= k < self.sh[2]:
            return int(self.ids[i, j, k]), int(self.meta[i, j, k])
        return 0, 0


# ------------------------------------------------------------ supports -------
DIR_META_WALL = {2: (0, 0, 1), 3: (0, 0, -1), 4: (1, 0, 0), 5: (-1, 0, 0)}    # offset to support
TORCH_SUP = {1: (-1, 0, 0), 2: (1, 0, 0), 3: (0, 0, -1), 4: (0, 0, 1), 5: (0, -1, 0)}
TRAP_SUP = {0: (0, 0, 1), 1: (0, 0, -1), 2: (1, 0, 0), 3: (-1, 0, 0)}
LEVER_SUP = {1: (-1, 0, 0), 2: (1, 0, 0), 3: (0, 0, -1), 4: (0, 0, 1), 5: (0, -1, 0), 6: (0, -1, 0),
             0: (0, 1, 0), 7: (0, 1, 0)}
BUTTON_SUP = {1: (-1, 0, 0), 2: (1, 0, 0), 3: (0, 0, -1), 4: (0, 0, 1), 5: (0, -1, 0), 0: (0, 1, 0)}
HOOK_SUP = {0: (0, 0, -1), 1: (1, 0, 0), 2: (0, 0, 1), 3: (-1, 0, 0)}


def support_errors(b, box=None):
    m = Model(b)
    ids = b.ids
    errs = []
    it = np.argwhere(ids > 0)
    for (i, j, k) in it:
        bid = int(ids[i, j, k])
        meta = int(b.meta[i, j, k])
        x, y, z = i + SX0, j + SY0, k + SZ0
        name = ID_NAMES[bid]

        def need(off, cond, why):
            sb, sm = m.at(x + off[0], y + off[1], z + off[2])
            if not cond(sb, sm):
                errs.append((x, y, z, name, meta, why, ID_NAMES.get(sb, sb)))
        if name in ('torch', 'redstone_torch', 'unlit_redstone_torch'):
            off = TORCH_SUP.get(meta, (0, -1, 0))
            if off == (0, -1, 0):
                need(off, lambda sb, sm: solid_top(sb, sm) or sb in FENCES or sb in NAMES('glass', 'stained_glass'),
                     'torch base')
            else:
                need(off, lambda sb, sm: normal_cube(sb), 'wall torch')
        elif name == 'ladder':
            need(DIR_META_WALL.get(meta, (0, 0, 1)), lambda sb, sm: normal_cube(sb), 'ladder')
        elif name in ('wall_sign', 'wall_banner'):
            need(DIR_META_WALL.get(meta, (0, 0, 1)), lambda sb, sm: sb != 0 and sb not in PASSABLE - DOORS
                 or sb in NAMES('wall_sign', 'standing_sign'), 'wall mount')
        elif name in ('trapdoor', 'iron_trapdoor'):
            need(TRAP_SUP[meta & 3], lambda sb, sm: normal_cube(sb) or sb in SLABS or sb in STAIRS
                 or sb == B['glowstone'], 'trapdoor hinge')
        elif name == 'lever':
            need(LEVER_SUP[meta & 7], lambda sb, sm: normal_cube(sb) or solid_top(sb, sm), 'lever')
        elif name in ('stone_button', 'wooden_button'):
            need(BUTTON_SUP[meta & 7], lambda sb, sm: normal_cube(sb), 'button')
        elif name == 'tripwire_hook':
            need(HOOK_SUP[meta & 3], lambda sb, sm: normal_cube(sb), 'hook')
        elif bid in DOORS:
            if meta & 8:
                need((0, -1, 0), lambda sb, sm: sb == bid, 'door upper')
            else:
                need((0, 1, 0), lambda sb, sm: sb == bid, 'door lower->upper')
                need((0, -1, 0), lambda sb, sm: solid_top(sb, sm), 'door floor')
        elif name == 'bed':
            d = {0: (0, 0, 1), 1: (-1, 0, 0), 2: (0, 0, -1), 3: (1, 0, 0)}[meta & 3]
            if meta & 8:
                d = (-d[0], 0, -d[2])
            need(d, lambda sb, sm: sb == B['bed'], 'bed pair')
        elif name in ('carpet',):
            need((0, -1, 0), lambda sb, sm: sb != 0, 'carpet')
        elif name in ('flower_pot', 'redstone_wire', 'unpowered_repeater', 'powered_repeater',
                      'stone_pressure_plate', 'wooden_pressure_plate', 'rail', 'activator_rail'):
            need((0, -1, 0), lambda sb, sm: solid_top(sb, sm) or (name.endswith('plate') and sb in FENCES),
                 'needs solid top below')
        elif name in ('standing_sign', 'standing_banner', 'cake'):
            need((0, -1, 0), lambda sb, sm: sb != 0 and sb not in PASSABLE - {B['carpet']}, 'needs block below')
        elif name in ('red_flower', 'yellow_flower', 'tallgrass', 'double_plant', 'sapling', 'deadbush'):
            need((0, -1, 0), lambda sb, sm: sb in NAMES('grass', 'dirt', 'farmland', 'double_plant') or
                 (name == 'deadbush' and sb in NAMES('sand', 'hardened_clay', 'stained_hardened_clay')),
                 'plant soil')
        elif name == 'waterlily':
            need((0, -1, 0), lambda sb, sm: sb in NAMES('water', 'flowing_water'), 'lily')
        elif name in ('anvil', 'sand', 'gravel', 'dragon_egg'):
            need((0, -1, 0), lambda sb, sm: sb != 0 and sb not in PASSABLE, 'gravity block')
        elif name == 'fire':
            need((0, -1, 0), lambda sb, sm: sb == B['netherrack'], 'fire on netherrack')
    return errs


# ------------------------------------------------------------ light ----------
def light_opacity(ids):
    op = np.full(ids.shape, 255, dtype=np.int16)
    for bid in NONCUBE | TRANSPARENT_FULL:
        op[ids == bid] = 0
    for bid in STAIRS | SLABS:
        op[ids == bid] = 255
    for n in ('leaves', 'leaves2', 'web'):
        op[ids == B[n]] = 1
    for n in ('water', 'flowing_water', 'ice'):
        op[ids == B[n]] = 3
    for n in ('glowstone', 'sea_lantern', 'redstone_block', 'mob_spawner', 'beacon'):
        op[ids == B[n]] = 255
    op[ids == 0] = 0
    return op


def block_light(b):
    ids = b.ids
    op = light_opacity(ids)
    lvl = np.zeros(ids.shape, dtype=np.int16)
    q = deque()
    for bid, v in LIGHT.items():
        for p in np.argwhere(ids == bid):
            p = tuple(p)
            if lvl[p] < v:
                lvl[p] = v
                q.append(p)
    sh = ids.shape
    while q:
        p = q.popleft()
        v = lvl[p]
        if v <= 1:
            continue
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            n = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
            if not (0 <= n[0] < sh[0] and 0 <= n[1] < sh[1] and 0 <= n[2] < sh[2]):
                continue
            o = op[n]
            if o >= 15:
                continue
            nv = v - max(1, o)
            if nv > lvl[n]:
                lvl[n] = nv
                q.append(n)
    return lvl


def sky_mask(b):
    """True where a column is open to the sky above (outdoors)."""
    op = light_opacity(b.ids) > 0
    sky = np.zeros(b.ids.shape, dtype=bool)
    # a cell is sky-exposed if all cells above it are transparent (opacity 0)
    above_blocked = np.flip(np.cumsum(np.flip(op, axis=1), axis=1), axis=1)
    # above_blocked[:, j] counts blocking cells at j and above; exposed if none strictly above
    blocked_strictly_above = np.zeros_like(above_blocked)
    blocked_strictly_above[:, :-1, :] = above_blocked[:, 1:, :]
    sky = blocked_strictly_above == 0
    return sky


def outdoor_mask(b):
    """Air-like cells connected to the open sky through non-colliding cells (doors/glass block it)."""
    from scipy import ndimage
    ids = b.ids
    open_ = np.isin(ids, list(PASSABLE - DOORS - GATES)) | (ids == 0)
    lab, n = ndimage.label(open_)
    top = set(np.unique(lab[:, -1, :])) | set(np.unique(lab[0, :, :])) | set(np.unique(lab[-1, :, :])) \
        | set(np.unique(lab[:, :, 0])) | set(np.unique(lab[:, :, -1]))
    top.discard(0)
    return np.isin(lab, list(top))


def dark_spots(b, lvl, box):
    """Spawnable interior positions with block light < 8 inside box (local coords)."""
    ids, meta = b.ids, b.meta
    sky = outdoor_mask(b)
    x1, y1, z1, x2, y2, z2 = box
    out = []
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            for y in range(y1, y2 + 1):
                i, j, k = x - SX0, y - SY0, z - SZ0
                f = int(ids[i, j, k])
                if f != 0:
                    continue
                if ids[i, j + 1, k] != 0 and not (int(ids[i, j + 1, k]) in PASSABLE):
                    continue
                below, bm = int(ids[i, j - 1, k]), int(meta[i, j - 1, k])
                if not solid_top(below, bm) or below == B['bedrock']:
                    continue
                if sky[i, j, k]:
                    continue
                if lvl[i, j, k] < 8:
                    out.append((x, y, z, int(lvl[i, j, k])))
    return out


# ------------------------------------------------------------ fire -----------
def fire_hazards(b):
    """For every fire block, air cells within spread range that touch flammables."""
    m = Model(b)
    out = []
    for p in np.argwhere(b.ids == B['fire']):
        fx, fy, fz = p[0] + SX0, p[1] + SY0, p[2] + SZ0
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for dy in range(-1, 5):
                    x, y, z = fx + dx, fy + dy, fz + dz
                    if m.at(x, y, z)[0] != 0:
                        continue
                    for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                        nb = m.at(x + d[0], y + d[1], z + d[2])[0]
                        if nb in FLAMMABLE:
                            out.append(((fx, fy, fz), (x, y, z), ID_NAMES[nb]))
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            nb = m.at(fx + d[0], fy + d[1], fz + d[2])[0]
            if nb in FLAMMABLE:
                out.append(((fx, fy, fz), 'adjacent', ID_NAMES[nb]))
    return out


# ------------------------------------------------------------ walking --------
SMALL = NAMES('flower_pot', 'skull', 'cake', 'daylight_detector', 'daylight_detector_inverted',
              'unpowered_repeater', 'powered_repeater', 'unpowered_comparator', 'powered_comparator', 'bed')
THIN = NAMES('glass_pane', 'stained_glass_pane', 'iron_bars')


def collision(bid, meta):
    """Collision interval (lo, hi) in half-blocks relative to the cell bottom, or None."""
    if bid == 0 or bid in PASSABLE or bid == B['fire']:
        return None
    if bid in TRAPDOORS:
        if meta & 4:
            return None
        return (1, 2) if meta & 8 else None
    if bid in SLABS:
        return (1, 2) if meta & 8 else (0, 1)
    if bid in SMALL:
        return (0, 1)
    if bid in FENCES:
        return (0, 3)
    return (0, 2)


class Walker:
    def __init__(self, b):
        self.ids, self.meta = b.ids, b.meta
        self.sh = b.ids.shape

    def cell(self, x, y, z):
        i, j, k = x - SX0, y - SY0, z - SZ0
        if 0 <= i < self.sh[0] and 0 <= j < self.sh[1] and 0 <= k < self.sh[2]:
            return int(self.ids[i, j, k]), int(self.meta[i, j, k])
        return 0, 0

    def clear(self, x, z, lo, hi, skip=None):
        for y in range(lo // 2 - 1, (hi + 1) // 2 + 1):
            if y == skip:
                continue
            bid, m = self.cell(x, y, z)
            c = collision(bid, m)
            if c is None:
                continue
            a, t = 2 * y + c[0], 2 * y + c[1]
            if bid in STAIRS and not (m & 4) and y * 2 + 1 == lo:
                t = 2 * y + 1          # standing on / next to the low half
            if a < hi and t > lo:
                return False
        return True

    def surfaces(self, x, z, near):
        out = []
        for y in range((near - 12) // 2, (near + 6) // 2 + 1):
            bid, m = self.cell(x, y, z)
            c = collision(bid, m)
            if c is None:
                if bid in CLIMB:
                    out.append((2 * y, None))
                continue
            if bid in FENCES:
                continue
            tops = [2 * y + c[1]]
            if bid in STAIRS and not (m & 4):
                tops.append(2 * y + 1)
            for t in tops:
                if self.clear(x, z, t, t + 4, skip=y):
                    out.append((t, y))
        return out

    def grounded(self, x, z, h):
        y = (h - 1) // 2
        bid, m = self.cell(x, y, z)
        c = collision(bid, m)
        if c is not None and 2 * y + c[1] == h:
            return True
        if bid in STAIRS and not (m & 4) and 2 * y + 1 == h:
            return True
        bid2, m2 = self.cell(x, h // 2, z)            # standing on a bottom slab/stair inside the cell
        c2 = collision(bid2, m2)
        return c2 is not None and 2 * (h // 2) + c2[1] == h and h % 2 == 1

    def run(self, start, limit=3_000_000):
        x0, y0, z0 = start
        s0 = (x0, z0, 2 * y0)
        seen = {s0}
        q = deque([s0])
        self.rev = rev = {}
        while q and len(seen) < limit:
            x, z, h = q.popleft()
            cur = (x, z, h)
            # climbing (ladders/vines/water)
            for yy in (h // 2, (h + 2) // 2):
                if self.cell(x, yy, z)[0] in CLIMB:
                    for dh in (2, -2):
                        n = (x, z, h + dh)
                        if self.clear(x, z, h + dh, h + dh + 4):
                            rev.setdefault(n, []).append(cur)
                            if n not in seen:
                                seen.add(n)
                                q.append(n)
                    break
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = x + dx, z + dz
                for nh, sy in self.surfaces(nx, nz, h):
                    if nh - h > 2:
                        continue
                    if nh - h == 2 and not self.clear(x, z, h, h + 6, skip=None):
                        continue
                    if nh - h == 2 and not self.grounded(x, z, h):
                        continue      # no jumping while hanging on a ladder / swimming
                    if nh < h - 20:
                        continue
                    top = max(h, nh)
                    if not self.clear(nx, nz, top, top + 4, skip=sy):
                        continue
                    if nh < h and not self.clear(nx, nz, nh, h + 4, skip=sy):
                        continue
                    n = (nx, nz, nh)
                    rev.setdefault(n, []).append(cur)
                    if n not in seen:
                        seen.add(n)
                        q.append(n)
        self.start = s0
        return seen

    def returnable(self):
        """States from which the start can be reached again (reverse BFS over recorded moves)."""
        fwd = {}
        for n, preds in self.rev.items():
            for p in preds:
                fwd.setdefault(p, []).append(n)
        back = {self.start}
        q = deque([self.start])
        # reverse graph of 'fwd': who can reach start -> predecessors of start in fwd = rev
        while q:
            s = q.popleft()
            for p in self.rev.get(s, ()):
                if p not in back:
                    back.add(p)
                    q.append(p)
        return back


# ------------------------------------------------------------ auto lighting --
FLOORISH = NAMES('planks', 'stone', 'stonebrick', 'quartz_block', 'wool', 'stained_hardened_clay',
                 'double_stone_slab', 'cobblestone', 'hardened_clay', 'double_wooden_slab')


def _spread(lvl, op, src, value, dark_set=None, apply=False):
    """BFS light from src; returns number of dark spots raised to >= 8 (optionally apply)."""
    sh = lvl.shape
    best = {src: value}
    q = deque([src])
    fixed = 0
    while q:
        p = q.popleft()
        v = best[p]
        if dark_set is not None and p in dark_set and v >= 8:
            fixed += 1
        if apply and lvl[p] < v:
            lvl[p] = v
        if v <= 1:
            continue
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            n = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
            if not (0 <= n[0] < sh[0] and 0 <= n[1] < sh[1] and 0 <= n[2] < sh[2]):
                continue
            if op[n] >= 15:
                continue
            nv = v - max(1, op[n])
            if nv > best.get(n, 0) and nv > (lvl[n] if not apply else 0):
                best[n] = nv
                q.append(n)
    return fixed


def auto_light(b, box, place, max_new=60, hidden_only=False, log=None):
    """Greedy light placement until no dark spawnable spot remains in box (local coords).

    place(kind, (x,y,z), meta) performs the placement (so it is emitted as a command).
    """
    lvl = block_light(b)
    added = []
    for it in range(max_new * 4):
        if len(added) >= max_new:
            break
        dark = dark_spots(b, lvl, box)
        if not dark:
            break
        op = light_opacity(b.ids)
        dset = {(x - SX0, y - SY0, z - SZ0) for (x, y, z, l) in dark}
        target = dark[0]
        tx, ty, tz = target[0], target[1], target[2]
        cands = []
        for dx in range(-4, 5):
            for dz in range(-4, 5):
                x, z = tx + dx, tz + dz
                for y in range(ty - 1, ty + 7):
                    i, j, k = x - SX0, y - SY0, z - SZ0
                    bid = int(b.ids[i, j, k])
                    above = int(b.ids[i, j + 1, k])
                    below = int(b.ids[i, j - 1, k])
                    # hidden: floor block under a carpet
                    if bid in FLOORISH and above == B['carpet'] and y == ty - 1:
                        cands.append((3, 'glow', (x, y, z), 0, (i, j, k), 15))
                    # ceiling light: opaque ceiling block with room air below
                    ceil_ok = bid in FLOORISH or (bid in SLABS and not int(b.meta[i, j, k]) & 8)
                    if ceil_ok and below == 0 and y >= ty + 3 and not hidden_only:
                        cands.append((1, 'glow', (x, y, z), 0, (i, j, k), 15))
                    # wall sconce at feet+1..+2
                    if bid == 0 and ty + 1 <= y <= ty + 2 and not hidden_only:
                        for (wx, wz, meta) in ((1, 0, 2), (-1, 0, 1), (0, 1, 4), (0, -1, 3)):
                            wb = int(b.ids[i + wx, j, k + wz])
                            if normal_cube(wb) and int(b.ids[i, j - 1, k]) not in DOORS:
                                cands.append((2, 'torch', (x, y, z), meta, (i, j, k), 14))
                                break
        if not cands:
            lvl[tx - SX0, ty - SY0, tz - SZ0] = 8     # give up on this spot
            if log:
                log('no candidate near', target)
            continue
        scored = []
        for (pri, kind, pos, meta, idx, val) in cands:
            n = _spread(lvl, op, idx, val, dset)
            scored.append((n + pri * 3, pri, kind, pos, meta, idx, val))
        scored.sort(key=lambda s: -s[0])
        _, pri, kind, pos, meta, idx, val = scored[0]
        place(kind, pos, meta)
        if kind == 'glow':
            op[idx] = 255
        _spread(lvl, op, idx, val, None, apply=True)
        added.append((kind, pos))
    return added
