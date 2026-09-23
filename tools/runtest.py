"""Run generated pastes on a real vanilla 1.8.x server and diff against the model.

The player's command block is placed at absolute (0, 60, 0) in a superflat
world whose grass surface is y=59 (local y=-1).  For every stage the harness
does exactly what a player does: put the paste into that command block and
give it a short redstone pulse (like a button).
"""
import os
import shutil
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcserver import Server          # noqa: E402
from mcworld import World            # noqa: E402
from engine import esc, SX0, SY0, SZ0  # noqa: E402
from blockids import ID_NAMES        # noqa: E402

CB = (0, 60, 0)
FLAT = 'generator-settings=3;minecraft:bedrock,55*minecraft:stone,3*minecraft:dirt,minecraft:grass;1;\n'


def make_template(server_dir):
    tpl = os.path.join(server_dir, 'world_flat60')
    if os.path.isdir(tpl):
        return tpl
    shutil.rmtree(os.path.join(server_dir, 'world'), ignore_errors=True)
    s = Server(server_dir, fresh=False, props_extra=FLAT)
    s.start()
    s.cmd('setworldspawn 0 60 0')
    s.sync()
    s.stop()
    s = Server(server_dir, fresh=False, props_extra=FLAT)
    s.start()
    s.sync()
    s.stop()
    shutil.copytree(os.path.join(server_dir, 'world'), tpl)
    return tpl


def run(server_dir, pastes, wait_ticks=80, log=print):
    tpl = make_template(server_dir)
    shutil.rmtree(os.path.join(server_dir, 'world'), ignore_errors=True)
    shutil.copytree(tpl, os.path.join(server_dir, 'world'))
    s = Server(server_dir, fresh=False, props_extra=FLAT)
    s.start()
    times = []
    try:
        x, y, z = CB
        s.cmd('gamerule commandBlockOutput false')
        s.cmd('setblock %d %d %d command_block' % CB)
        s.sync()
        for k, paste in enumerate(pastes):
            s.cmd('blockdata %d %d %d {Command:"%s"}' % (x, y, z, esc(paste)))
            s.sync()
            t0 = time.time()
            s.cmd('setblock %d %d %d stone_button 4' % (x, y, z - 1))  # button on the north face
            s.cmd('setblock %d %d %d stone_button 12' % (x, y, z - 1))  # pressed (meta 4 | 8)
            s.sync()
            s.wait_ticks(wait_ticks)
            times.append(time.time() - t0)
            s.cmd('setblock %d %d %d air' % (x, y, z - 1))
            s.sync()
            # Stage finished when the landing column is gone.
            m = s.mark()
            s.cmd('testforblock %d %d %d air' % (x, y + 3, z))
            s.sync()
            ok = any('Successfully found' in l for l in s.since(m))
            log('stage %d/%d len=%d column-cleared=%s wall=%.1fs' % (k + 1, len(pastes), len(paste), ok, times[-1]))
        s.wait_ticks(40)
        errors = [l for l in s.lines if ('Exception' in l or 'ERROR' in l or "Can't keep up" in l)]
    finally:
        s.stop()
    return errors, times


def diff(server_dir, build, box, log=print, max_report=40):
    """Compare world blocks in local box with the model."""
    (x1, y1, z1, x2, y2, z2) = box
    w = World(os.path.join(server_dir, 'world'))
    ids, metas = w.box(x1 + CB[0], y1 + CB[1], z1 + CB[2], x2 + CB[0], y2 + CB[1], z2 + CB[2])
    mid = build.ids[x1 - SX0:x2 - SX0 + 1, y1 - SY0:y2 - SY0 + 1, z1 - SZ0:z2 - SZ0 + 1]
    mme = build.meta[x1 - SX0:x2 - SX0 + 1, y1 - SY0:y2 - SY0 + 1, z1 - SZ0:z2 - SZ0 + 1]
    from blockids import BLOCK_IDS
    fire, wire = BLOCK_IDS['fire'], BLOCK_IDS['redstone_wire']
    fw, ww = BLOCK_IDS['flowing_water'], BLOCK_IDS['water']
    cascade = ((ids == fw) | (ids == ww)) & ((mid == 0) | (mid == ww))   # game-made flowing water
    lv = (mid == BLOCK_IDS['leaves']) & (ids == mid) & ((metas & 7) == (mme & 7))      # game sets check-decay bit
    lv |= (mid == BLOCK_IDS['double_plant']) & (ids == mid) & ((metas & 8) == (mme & 8) ) & (mme >= 8)  # 1.8.0 vs 1.8.9 upper meta
    bad = np.argwhere(((ids != mid) | ((metas != mme) & ~lv & (mid != 0) & (mid != fire) & (mid != wire)
                                       & (mid != ww))) & ~cascade)
    log('flowing-water cells made by the game (fountain cascade): %d' % int((cascade & (ids == fw)).sum()))
    report = []
    for (i, j, k) in bad[:max_report]:
        report.append('(%d,%d,%d) world=%s:%d model=%s:%d' % (
            i + x1, j + y1, k + z1, ID_NAMES.get(int(ids[i, j, k]), ids[i, j, k]), metas[i, j, k],
            ID_NAMES.get(int(mid[i, j, k]), mid[i, j, k]), mme[i, j, k]))
    log('diff: %d mismatching blocks' % len(bad))
    for r in report:
        log('  ' + r)
    # entities
    ents = w.entities(x1 + CB[0], y1 + CB[1], z1 + CB[2], x2 + CB[0], y2 + CB[1], z2 + CB[2])
    found = {}
    for e in ents:
        found.setdefault(e['id'], []).append(e)
    want = {}
    for (etype, pos, extra) in build.entities:
        want[etype] = want.get(etype, 0) + 1
    log('entities in world: %s ; expected: %s' % ({k: len(v) for k, v in found.items()}, want))
    for e in found.get('Painting', []):
        hx, hy, hz = e['TileX'] - CB[0], e['TileY'] - CB[1], e['TileZ'] - CB[2]
        ok = any(et == 'Painting' and tuple(p) == (hx, hy, hz) for (et, p, ex) in build.entities)
        if not ok:
            log('  painting at unexpected position %s %s' % ((hx, hy, hz), e.get('Motive')))
    for e in found.get('Item', []):
        log('  dropped item %s at %s' % (e['Item'].get('id'), [round(v - c, 1) for v, c in zip(e['Pos'], CB)]))
    return bad, ids, metas, w
