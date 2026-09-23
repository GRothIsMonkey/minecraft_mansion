"""Quick PIL renderers for the voxel model: isometric views and floor plans."""
import numpy as np
from PIL import Image, ImageDraw

from blockids import BLOCK_IDS

B = BLOCK_IDS

# approximate average colours (r, g, b); metadata-specific entries keyed (id, meta)
COL = {
    B['stone']: (125, 125, 125), B['grass']: (95, 150, 60), B['dirt']: (134, 96, 67),
    B['cobblestone']: (110, 110, 110), B['planks']: (160, 130, 80), B['bedrock']: (60, 60, 60),
    B['log']: (100, 80, 50), B['leaves']: (60, 110, 40), B['glass']: (200, 230, 240),
    B['sandstone']: (215, 205, 160), B['wool']: (230, 230, 230), B['gold_block']: (250, 215, 60),
    B['iron_block']: (220, 220, 220), B['double_stone_slab']: (165, 165, 165),
    B['stone_slab']: (165, 165, 165), B['brick_block']: (150, 75, 60), B['bookshelf']: (120, 90, 60),
    B['mossy_cobblestone']: (90, 110, 90), B['obsidian']: (20, 15, 30), B['torch']: (255, 220, 100),
    B['fire']: (255, 140, 30), B['oak_stairs']: (160, 130, 80), B['chest']: (160, 110, 40),
    B['redstone_wire']: (170, 0, 0), B['diamond_block']: (100, 220, 220),
    B['crafting_table']: (140, 100, 60), B['furnace']: (100, 100, 100), B['lit_furnace']: (120, 100, 90),
    B['standing_sign']: (160, 130, 80), B['wooden_door']: (150, 120, 70), B['ladder']: (140, 110, 60),
    B['stone_stairs']: (110, 110, 110), B['wall_sign']: (160, 130, 80), B['lever']: (120, 100, 80),
    B['stone_pressure_plate']: (130, 130, 130), B['iron_door']: (200, 200, 200),
    B['wooden_pressure_plate']: (160, 130, 80), B['redstone_torch']: (200, 30, 30),
    B['unlit_redstone_torch']: (100, 30, 30), B['stone_button']: (130, 130, 130),
    B['snow_layer']: (240, 250, 250), B['jukebox']: (120, 80, 60), B['fence']: (160, 130, 80),
    B['pumpkin']: (220, 130, 20), B['netherrack']: (110, 50, 50), B['glowstone']: (250, 220, 130),
    B['lit_pumpkin']: (240, 170, 40), B['unpowered_repeater']: (160, 150, 150),
    B['stained_glass']: (180, 180, 220), B['trapdoor']: (140, 110, 60), B['stonebrick']: (122, 122, 122),
    B['iron_bars']: (160, 160, 160), B['glass_pane']: (200, 230, 240), B['vine']: (50, 100, 30),
    B['fence_gate']: (160, 130, 80), B['brick_stairs']: (150, 75, 60), B['stone_brick_stairs']: (122, 122, 122),
    B['nether_brick']: (50, 25, 30), B['nether_brick_fence']: (50, 25, 30),
    B['nether_brick_stairs']: (50, 25, 30), B['enchanting_table']: (130, 40, 40),
    B['brewing_stand']: (150, 140, 120), B['cauldron']: (70, 70, 70), B['end_portal_frame']: (100, 130, 110),
    B['redstone_lamp']: (140, 80, 50), B['lit_redstone_lamp']: (240, 190, 120),
    B['double_wooden_slab']: (160, 130, 80), B['wooden_slab']: (160, 130, 80),
    B['emerald_block']: (60, 200, 100), B['spruce_stairs']: (105, 80, 50), B['birch_stairs']: (200, 180, 120),
    B['jungle_stairs']: (160, 115, 80), B['command_block']: (180, 130, 100), B['cobblestone_wall']: (110, 110, 110),
    B['flower_pot']: (130, 70, 50), B['wooden_button']: (160, 130, 80), B['skull']: (200, 200, 190),
    B['anvil']: (70, 70, 70), B['trapped_chest']: (160, 110, 40), B['unpowered_comparator']: (160, 150, 150),
    B['redstone_block']: (170, 20, 10), B['quartz_block']: (235, 230, 225), B['quartz_stairs']: (235, 230, 225),
    B['activator_rail']: (150, 100, 80), B['stained_hardened_clay']: (150, 100, 90),
    B['stained_glass_pane']: (180, 180, 220), B['leaves2']: (50, 90, 30), B['log2']: (60, 45, 30),
    B['acacia_stairs']: (170, 90, 50), B['dark_oak_stairs']: (65, 45, 25), B['iron_trapdoor']: (200, 200, 200),
    B['prismarine']: (100, 160, 150), B['sea_lantern']: (200, 230, 220), B['hay_block']: (180, 160, 40),
    B['carpet']: (200, 60, 60), B['hardened_clay']: (150, 90, 65), B['coal_block']: (25, 25, 25),
    B['standing_banner']: (200, 200, 200), B['wall_banner']: (200, 200, 200), B['spruce_fence']: (105, 80, 50),
    B['dark_oak_fence']: (65, 45, 25), B['birch_fence']: (200, 180, 120), B['spruce_fence_gate']: (105, 80, 50),
    B['dark_oak_fence_gate']: (65, 45, 25), B['spruce_door']: (105, 80, 50), B['dark_oak_door']: (65, 45, 25),
    B['birch_door']: (200, 180, 120), B['water']: (50, 90, 220), B['flowing_water']: (50, 90, 220),
    B['lava']: (230, 100, 20), B['red_flower']: (200, 30, 30), B['yellow_flower']: (240, 220, 40),
    B['tallgrass']: (90, 150, 50), B['double_plant']: (90, 160, 60), B['sapling']: (70, 130, 40),
    B['bed']: (170, 40, 40), B['piston']: (150, 130, 100), B['sticky_piston']: (130, 150, 100),
    B['piston_head']: (160, 140, 110), B['noteblock']: (120, 80, 60), B['cake']: (240, 230, 220),
    B['web']: (230, 230, 230), B['deadbush']: (130, 100, 50), B['waterlily']: (40, 120, 40),
    B['brown_mushroom']: (150, 110, 80), B['red_mushroom']: (200, 40, 40), B['cactus']: (40, 120, 40),
    B['melon_block']: (120, 160, 40), B['clay']: (160, 165, 180), B['gravel']: (130, 120, 115),
    B['sand']: (220, 210, 160), B['ender_chest']: (30, 50, 50), B['beacon']: (150, 230, 230),
    B['daylight_detector']: (180, 160, 120), B['hopper']: (70, 70, 70), B['dispenser']: (110, 110, 110),
    B['dropper']: (110, 110, 110), B['mob_spawner']: (30, 40, 60), B['tripwire_hook']: (130, 120, 100),
    B['rail']: (130, 110, 90), B['golden_rail']: (180, 150, 80), B['red_sandstone']: (180, 90, 40),
    B['packed_ice']: (160, 190, 240), B['ice']: (150, 180, 240), B['slime']: (110, 190, 90),
    B['lapis_block']: (40, 70, 160), B['farmland']: (110, 70, 40), B['wheat']: (180, 170, 60),
    B['mycelium']: (110, 90, 110), B['soul_sand']: (80, 60, 50), B['end_stone']: (220, 220, 160),
}
WOOL = [(233, 236, 236), (240, 118, 19), (189, 68, 179), (58, 175, 217), (248, 197, 39), (112, 185, 25),
        (237, 141, 172), (62, 68, 71), (142, 142, 134), (21, 137, 145), (121, 42, 172), (53, 57, 157),
        (114, 71, 40), (84, 109, 27), (160, 39, 34), (20, 21, 25)]
CLAY = [(209, 178, 161), (161, 83, 37), (149, 88, 108), (113, 108, 137), (186, 133, 35), (103, 117, 52),
        (161, 78, 78), (57, 42, 35), (135, 106, 97), (86, 91, 91), (118, 70, 86), (74, 59, 91),
        (77, 51, 35), (75, 82, 42), (142, 60, 46), (37, 22, 16)]
PLANK = [(160, 130, 80), (105, 80, 50), (200, 180, 120), (160, 115, 80), (170, 90, 50), (65, 45, 25)]
LOG = [(100, 80, 50), (50, 35, 20), (215, 215, 210), (90, 70, 30)]
LOG2 = [(100, 90, 80), (55, 40, 25)]
STONE = [(125, 125, 125), (150, 105, 85), (160, 110, 90), (190, 190, 190), (200, 200, 200), (130, 130, 130),
         (135, 135, 140)]
SB = [(122, 122, 122), (110, 125, 100), (115, 115, 115), (125, 125, 125)]
SLAB = {0: (165, 165, 165), 1: (215, 205, 160), 3: (110, 110, 110), 4: (150, 75, 60), 5: (122, 122, 122),
        6: (50, 25, 30), 7: (235, 230, 225)}


def color(bid, meta):
    if bid in (B['wool'], B['carpet']):
        return WOOL[meta & 15]
    if bid in (B['stained_hardened_clay'], B['stained_glass'], B['stained_glass_pane']):
        c = WOOL[meta & 15] if bid != B['stained_hardened_clay'] else CLAY[meta & 15]
        return c
    if bid in (B['planks'], B['wooden_slab'], B['double_wooden_slab']):
        return PLANK[(meta & 7) % 6]
    if bid == B['log']:
        return LOG[meta & 3]
    if bid == B['log2']:
        return LOG2[meta & 1]
    if bid == B['stone']:
        return STONE[meta % 7]
    if bid == B['stonebrick']:
        return SB[meta & 3]
    if bid in (B['stone_slab'], B['double_stone_slab']):
        return SLAB.get(meta & 7, (165, 165, 165))
    return COL.get(bid, (255, 0, 255))


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


SOLIDISH = None


def iso(ids, meta, out_path, scale=6, view='NW', ymin=None, cut=None):
    """Isometric render of a voxel sub-array (x, y, z).  view NW/NE/SW/SE = camera corner."""
    a = ids.copy()
    m = meta.copy()
    if cut is not None:
        a[:, cut:, :] = 0
    if view in ('NE', 'SE'):
        a = a[::-1, :, :]
        m = m[::-1, :, :]
    if view in ('SW', 'SE'):
        a = a[:, :, ::-1]
        m = m[:, :, ::-1]
    sx, sy, sz = a.shape
    # camera looks from -x,-z (NW) toward +x,+z; draw far-to-near
    w = int((sx + sz) * scale * 0.87) + 20
    h = int((sx + sz) * scale * 0.5 + sy * scale) + 20
    img = Image.new('RGB', (w, h), (175, 205, 235))
    d = ImageDraw.Draw(img)
    cw, ch = scale * 0.866, scale * 0.5

    def proj(x, y, z):
        px = (x - z) * cw + sz * cw + 10
        py = (sx + sz - x - z) * ch - y * scale + sy * scale + 10
        return px, py
    air = (a == 0)
    for s in range(sx + sz - 2, -1, -1):
        for x in range(max(0, s - sz + 1), min(sx, s + 1)):
            z = s - x
            col = a[x, :, z]
            ys = np.nonzero(col)[0]
            for y in ys:
                bid = int(col[y])
                c = color(bid, int(m[x, y, z]))
                top_open = y + 1 >= sy or air[x, y + 1, z]
                w_open = x - 1 < 0 or air[x - 1, y, z]
                n_open = z - 1 < 0 or air[x, y, z - 1]
                # faces toward camera: -x (left/west) and -z (right/north), top
                if top_open:
                    p = [proj(x, y + 1, z), proj(x + 1, y + 1, z), proj(x + 1, y + 1, z + 1), proj(x, y + 1, z + 1)]
                    d.polygon(p, fill=c)
                if w_open:
                    p = [proj(x, y, z), proj(x, y + 1, z), proj(x, y + 1, z + 1), proj(x, y, z + 1)]
                    d.polygon(p, fill=_shade(c, 0.78))
                if n_open:
                    p = [proj(x, y, z), proj(x + 1, y, z), proj(x + 1, y + 1, z), proj(x, y + 1, z)]
                    d.polygon(p, fill=_shade(c, 0.62))
    img.save(out_path)
    return img


def plan(ids, meta, y_levels, out_path, scale=8, labels=None, grid=None):
    """Top-down plan: for each (x,z) show the highest non-air block in y_levels window."""
    sx, sy, sz = ids.shape
    y0, y1 = y_levels
    img = Image.new('RGB', (sx * scale, sz * scale), (20, 20, 20))
    d = ImageDraw.Draw(img)
    for x in range(sx):
        for z in range(sz):
            col = ids[x, y0:y1 + 1, z]
            nz = np.nonzero(col)[0]
            if len(nz) == 0:
                c = (40, 40, 40)
            else:
                yy = y0 + nz[-1]
                c = color(int(ids[x, yy, z]), int(meta[x, yy, z]))
                # darken by depth below the top of the window
                c = _shade(c, 0.55 + 0.45 * (yy - y0 + 1) / (y1 - y0 + 1))
            d.rectangle([x * scale, z * scale, x * scale + scale - 1, z * scale + scale - 1], fill=c)
    if grid is not None:
        gx0, gz0 = grid      # mansion coordinate of array index 0 is -gx0...
        for x in range(sx):
            if (x - 3) % 5 == 0:
                d.line([(x * scale, 0), (x * scale, sz * scale)], fill=(255, 255, 255), width=1)
                d.text((x * scale + 1, 1), str(x - 3), fill=(255, 255, 0))
        for z in range(sz):
            if (z - 9) % 5 == 0:
                d.line([(0, z * scale), (sx * scale, z * scale)], fill=(255, 255, 255), width=1)
                d.text((1, z * scale + 1), str(z - 9), fill=(255, 255, 0))
    if labels:
        for (x, z, text) in labels:
            d.text((x * scale, z * scale), text, fill=(255, 255, 0))
    img.save(out_path)
    return img


def elevation(ids, meta, out_path, side='N', scale=6, sky=(175, 205, 235)):
    """Orthographic elevation.  side = which face we look at (N = look toward +z)."""
    a, m = ids, meta
    if side == 'N':      # look along +z ; screen x = +x
        a2, m2 = a, m
    elif side == 'S':    # look along -z ; screen x = -x
        a2, m2 = a[::-1, :, ::-1], m[::-1, :, ::-1]
    elif side == 'W':    # look along +x ; screen x = -z
        a2 = np.transpose(a, (2, 1, 0))[::-1, :, :]
        m2 = np.transpose(m, (2, 1, 0))[::-1, :, :]
    else:                # E: look along -x ; screen x = +z
        a2 = np.transpose(a, (2, 1, 0))[:, :, ::-1]
        m2 = np.transpose(m, (2, 1, 0))[:, :, ::-1]
    sx, sy, sz = a2.shape
    img = Image.new('RGB', (sx * scale, sy * scale), sky)
    d = ImageDraw.Draw(img)
    for x in range(sx):
        for y in range(sy):
            col = a2[x, y, :]
            nz = np.nonzero(col)[0]
            if len(nz) == 0:
                continue
            z = nz[0]
            c = color(int(a2[x, y, z]), int(m2[x, y, z]))
            c = _shade(c, max(0.45, 1.0 - 0.012 * z))
            py = (sy - 1 - y) * scale
            d.rectangle([x * scale, py, x * scale + scale - 1, py + scale - 1], fill=c)
    img.save(out_path)
    return img
