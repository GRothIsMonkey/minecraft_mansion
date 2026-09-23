"""Compare two saved worlds over the mansion area: blocks, tile-entity data and entities.

    python3 plugin_compare.py <reference-world-dir> <plugin-world-dir>

Used to show that the plugin gives exactly the same world as the tested 34-stage console
installation (Claude base + Astra refurbishment): every block id and data value, every
tile entity's NBT (chest contents, sign text, the journal book, skulls, banners, flower
pots, jukebox, command block) and every painting / item frame / armor stand.

Ignored, because the game (not the build) sets them: redstone dust power, leaf decay
bits, flowing-water levels, grass under walls turning to dirt, and per-entity runtime
fields (UUID, motion, fall distance, Spigot/Bukkit bookkeeping, a command block's
run counter / last output).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                     # noqa: E402
import rotation as R                   # noqa: E402
from blockids import BLOCK_IDS as B, ID_NAMES   # noqa: E402
from engine import SX0, SX1, SY0, SY1, SZ0, SZ1   # noqa: E402
from mcworld import World              # noqa: E402

ENTITY_RUNTIME = {'UUIDMost', 'UUIDLeast', 'Motion', 'FallDistance', 'Fire', 'Air', 'OnGround', 'Dimension',
                  'PortalCooldown', 'Invulnerable', 'WorldUUIDMost', 'WorldUUIDLeast', 'Bukkit.updateLevel',
                  'Spigot.ticksLived', 'HurtByTimestamp', 'DeathTime', 'HurtTime', 'AbsorptionAmount',
                  'Attributes', 'Health', 'HealF', 'Pos', 'Rotation'}
TE_RUNTIME = {'SuccessCount', 'LastOutput', 'Bukkit.updateLevel'}


def box():
    x1, y1, z1 = R.r_to_world(SX0, SY0, SZ0)
    x2, y2, z2 = R.r_to_world(SX1, SY1, SZ1)
    return x1, y1, z1, x2, y2, z2


def clean(d, drop):
    if isinstance(d, dict):
        return {k: clean(v, drop) for k, v in sorted(d.items()) if k not in drop}
    if isinstance(d, list):
        return [clean(v, drop) for v in d]
    if isinstance(d, float):
        return round(d, 3)
    return d


def main(a_dir, b_dir):
    bx = box()
    wa, wb = World(a_dir), World(b_dir)
    ia, ma = wa.box(*bx)
    ib, mb = wb.box(*bx)
    fw, ww = B['flowing_water'], B['water']
    water = ((ia == fw) | (ia == ww)) & ((ib == fw) | (ib == ww))
    grass = np.isin(ia, [B['grass'], B['dirt']]) & np.isin(ib, [B['grass'], B['dirt']]) & (ia != ib)
    ids_differ = (ia != ib) & ~water & ~grass
    game_meta = np.isin(ia, [B['redstone_wire'], B['leaves'], B['leaves2'], fw, ww, B['fire']])
    meta_differ = (ia == ib) & (ma != mb) & ~game_meta
    bad = np.argwhere(ids_differ | meta_differ)
    rep = {'area': bx, 'blocks_compared': int(ia.size),
           'block_differences': len(bad),
           'block_examples': ['%s %s:%d vs %s:%d' % ((int(i + bx[0]), int(j + bx[1]), int(k + bx[2])),
                                                     ID_NAMES.get(int(ia[i, j, k])), ma[i, j, k],
                                                     ID_NAMES.get(int(ib[i, j, k])), mb[i, j, k])
                              for (i, j, k) in bad[:10]],
           'harmless': {'water_level_cells': int((water & (ma != mb)).sum()), 'grass_dirt_cells': int(grass.sum())}}
    ta = {(t['x'], t['y'], t['z']): clean(t, TE_RUNTIME) for t in wa.tile_entities(*bx)}
    tb = {(t['x'], t['y'], t['z']): clean(t, TE_RUNTIME) for t in wb.tile_entities(*bx)}
    te_diff = [str(k) for k in sorted(set(ta) | set(tb)) if ta.get(k) != tb.get(k)]
    kinds = {}
    for t in ta.values():
        kinds[t['id']] = kinds.get(t['id'], 0) + 1
    rep.update({'tile_entities': len(ta), 'tile_entity_kinds': kinds, 'tile_entity_differences': len(te_diff),
                'tile_entity_examples': [(k, ta.get(eval(k)), tb.get(eval(k))) for k in te_diff[:3]]})

    def ents(w):
        out = []
        for e in w.entities(bx[0], 0, bx[2], bx[3], 255, bx[5]):
            c = clean(e, ENTITY_RUNTIME)
            c['_pos'] = [round(v, 2) for v in e['Pos']]
            c['_yaw'] = round(e['Rotation'][0] % 360, 1)
            out.append(json.dumps(c, sort_keys=True, default=str))
        return sorted(out)
    ea, eb = ents(wa), ents(wb)
    rep.update({'entities': len(ea), 'entity_differences': len(set(ea) ^ set(eb)) + abs(len(ea) - len(eb)),
                'entity_examples': sorted(set(ea) ^ set(eb))[:4]})
    rep['identical'] = rep['block_differences'] == 0 and rep['tile_entity_differences'] == 0 \
        and rep['entity_differences'] == 0
    print(json.dumps(rep, indent=1, default=str))
    return rep


if __name__ == '__main__':
    r = main(sys.argv[1], sys.argv[2])
    sys.exit(0 if r['identical'] else 1)
