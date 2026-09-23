"""Real-server test of the server-console installation workflow.

    python3 console_test.py <server-dir> [flat|terrain] [--no-functional]

What it does, exactly like the documented installation:
  * starts a vanilla 1.8.x dedicated server (server.jar in <server-dir>) with the
    documented minimum view-distance and the default 60 s tick watchdog;
  * joins a headless player (mcbot) and puts it at the documented stand point, so
    only that player keeps the site's chunks loaded (world spawn is far away);
  * types every commands_console/console_NN.txt, as shipped, into the server console
    (stdin), and waits for the documented completion line before the next one;
  * stops the server, diffs the saved world against the rotated design model, re-runs
    the design validators on the blocks READ BACK FROM THE WORLD, checks entities and
    that no installer block/entity is left;
  * restarts the server and lets the player click every lever, door, hatch, gate,
    chest, furnace, bed ... to check that they work.
"""
import collections
import json
import math
import os
import re
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                     # noqa: E402
import console_build as CB             # noqa: E402
import rotation as R                   # noqa: E402
import validate as V                   # noqa: E402
import check                           # noqa: E402
from mcserver import Server            # noqa: E402
from mcworld import World              # noqa: E402
from mcbot import Bot                  # noqa: E402
from blockids import BLOCK_IDS as B, ID_NAMES   # noqa: E402
from engine import SX0, SX1, SY0, SY1, SZ0, SZ1   # noqa: E402
from mansion_base import X0, Z0        # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLAT72 = 'generator-settings=3;minecraft:bedrock,68*minecraft:stone,3*minecraft:dirt,minecraft:grass;1;\n'
BOT = 'MansionTester'
PORT = int(os.environ.get('MC_PORT', '25599'))
VERIFY_COMMANDS = [
    'testforblock %d %d %d air' % CB.PAD,
    'testfor @e[type=MinecartCommandBlock]',
    'testfor @e[type=FallingSand]',
    'testforblock -251 76 266 dark_oak_door',
    'testforblock -251 76 267 dark_oak_door',
]
RESULTS = []


def res(name, ok, detail=''):
    RESULTS.append((name, ok, detail))
    print('  [%s] %s%s' % ('PASS' if ok else 'FAIL', name, (' - ' + detail) if detail else ''), flush=True)
    return ok


def props(kind):
    p = ('view-distance=%d\nmax-tick-time=60000\nuse-native-transport=false\nserver-port=%d\n'
         % (CB.MIN_VIEW_DISTANCE, PORT))
    if kind == 'flat':
        p += FLAT72
    else:
        # seed 20150101: at the site the ground is Y 70-92 (hills to cut), with trees and some water
        p += 'level-type=DEFAULT\ngenerate-structures=true\nlevel-seed=%s\n' % os.environ.get('MC_SEED', '20150101')
    return p


def template(server_dir, kind):
    tpl = os.path.join(server_dir, 'tpl_' + kind)
    if os.path.isdir(tpl):
        return tpl
    shutil.rmtree(os.path.join(server_dir, 'world'), ignore_errors=True)
    s = Server(server_dir, fresh=False, props_extra=props(kind))
    s.start()
    # world spawn far from the site, so spawn chunks never keep the site loaded
    s.cmd('setworldspawn 3000 80 -3000')
    s.sync()
    s.stop()
    shutil.copytree(os.path.join(server_dir, 'world'), tpl)
    return tpl


def mw(mx, y, mz):
    """mansion coords -> world."""
    return R.block(mx + X0, y, mz + Z0)


def console_files():
    d = os.path.join(ROOT, 'commands_console')
    man = json.load(open(os.path.join(d, 'manifest.json')))
    out = []
    for st in man['stages']:
        with open(os.path.join(d, st['file'])) as fh:
            text = fh.read().rstrip('\n')
        out.append((st['file'], text, st['expect']))
    return out


# --------------------------------------------------------------- install ----
def install(server_dir, kind):
    tpl = template(server_dir, kind)
    shutil.rmtree(os.path.join(server_dir, 'world'), ignore_errors=True)
    shutil.copytree(tpl, os.path.join(server_dir, 'world'))
    s = Server(server_dir, fresh=False, props_extra=props(kind))
    s.start()
    bot = None
    stages = []
    try:
        bot = Bot(BOT, port=PORT).connect()
        sx, sy, sz = CB.STAND
        if kind == 'terrain':
            sy = 130            # unknown ground height: hover (creative), same X/Z
        m = s.mark()
        s.cmd('tp %s %.1f %d %.1f' % (BOT, sx + 0.5, sy, sz + 0.5))
        s.wait_for('Teleported %s' % BOT, 30, m)
        time.sleep(8)                                  # let the player's chunks load
        # ---- the installation, one console line at a time ----
        files = console_files()
        for k, (fname, text, expect) in enumerate(files):
            assert not text.startswith('/') and '\n' not in text
            m = s.mark()
            t0 = time.time()
            s.cmd(text)                                # exactly what is pasted into the console
            line = s.wait_for(re.escape(expect), 900, m)
            dt = time.time() - t0
            time.sleep(1.0)                            # the cleanup block fires 1-4 ticks later
            s.sync()
            lines = s.since(m)
            lag = [ln for ln in lines if "Can't keep up" in ln]
            errs = [ln for ln in lines if re.search(r'Exception|ERROR|Cannot|out of the world|failed', ln)]
            mine = [ln for ln in lines if 'sync' not in ln and "Can't keep up" not in ln]
            stages.append({'file': fname, 'chars': len(text), 'secs': round(dt, 1), 'lines': len(mine),
                           'lag': lag, 'errors': errs, 'msg': line.split(']: ', 1)[-1]})
            print('  %s %5d chars  %5.1fs  console lines %3d  %s%s' % (
                fname, len(text), dt, len(mine), line.split(']: ', 1)[-1],
                ('  LAG ' + lag[0].split('Running ')[-1]) if lag else ''), flush=True)
            if not bot.alive:
                raise RuntimeError('player disconnected: %s' % bot.disconnect_reason)
        # ---- recovery drill, exactly as documented: pad again, repeat a stage, cleanup ----
        rep = max(files[1:], key=lambda f: f[1].count('summon Painting') + f[1].count('summon ArmorStand'))
        m = s.mark()
        s.cmd(files[0][1])
        s.wait_for(re.escape(files[0][2]), 60, m)
        m = s.mark()
        s.cmd(rep[1])
        s.wait_for(re.escape(rep[2]), 900, m)
        time.sleep(1.0)
        import console_export
        cleanup = {}
        for c in console_export.cleanup_commands():
            m = s.mark()
            s.cmd(c)
            s.sync()
            cleanup[c] = [ln.split(']: ', 1)[-1] for ln in s.since(m) if 'sync' not in ln]
        print('  repeated %s (%d paintings/armor stands in it), then ran the documented cleanup: %s' % (
            rep[0], rep[1].count('summon Painting') + rep[1].count('summon ArmorStand'), cleanup))
        s.wait_ticks(200)                              # hanging entities re-validate every 100 ticks
        # the verification commands documented in CONSOLE_INSTALL.md, with their real replies
        verify = {}
        for c in VERIFY_COMMANDS:
            m = s.mark()
            s.cmd(c)
            s.sync()
            verify[c] = [ln.split(']: ', 1)[-1] for ln in s.since(m) if 'sync' not in ln]
            print('  > %s\n      %s' % (c, verify[c]))
        stages.append({'verify': verify, 'repeated': rep[0], 'cleanup': cleanup})
        m = s.mark()
        s.cmd('gamerule commandBlockOutput')
        s.cmd('gamerule logAdminCommands')
        s.sync()
        gr = [ln.split(']: ', 1)[-1] for ln in s.since(m) if 'commandBlockOutput' in ln or 'logAdminCommands' in ln]
        res('gamerules restored afterwards', gr == ['commandBlockOutput = true', 'logAdminCommands = true'], str(gr))
        res('the test player stayed connected at the stand point for the whole install', bot.alive,
            'view-distance %d' % CB.MIN_VIEW_DISTANCE)
        allerr = [ln for ln in s.lines if re.search(r'Exception|ERROR|Watchdog|crash', ln)]
        res('no server errors, exceptions or watchdog', not allerr, '; '.join(allerr[:3]))
    finally:
        if bot:
            bot.close()
        s.stop()
    return stages


# ------------------------------------------------------------- world diff ---
def world_frame(server_dir):
    w = World(os.path.join(server_dir, 'world'))
    x1, y1, z1 = R.r_to_world(SX0, SY0, SZ0)
    x2, y2, z2 = R.r_to_world(SX1, SY1, SZ1)
    ids, metas = w.box(x1, y1, z1, x2, y2, z2)
    return w, R.Frame(ids.astype(np.int16), metas.astype(np.int8)), (x1, y1, z1, x2, y2, z2)


def diff(F, W, mask=None):
    mid, mme = F.ids.astype(np.int32), F.meta.astype(np.int32)
    ids, metas = W.ids.astype(np.int32), W.meta.astype(np.int32)
    fw, ww = B['flowing_water'], B['water']
    cascade = ((ids == fw) | (ids == ww)) & ((mid == 0) | (mid == ww))
    lv = (mid == B['leaves']) & (ids == mid) & ((metas & 7) == (mme & 7))
    lv |= (mid == B['double_plant']) & (ids == mid) & ((metas & 8) == (mme & 8)) & (mme >= 8)
    bad = ((ids != mid) | ((metas != mme) & ~lv & (mid != 0) & (mid != B['fire']) & (mid != B['redstone_wire'])
                          & (mid != ww))) & ~cascade
    # vanilla grass under an opaque block turns to dirt on a random tick (hidden under walls)
    op = V.light_opacity(F.ids)
    above = np.zeros_like(op)
    above[:, :-1, :] = op[:, 1:, :]
    dead_grass = (mid == B['grass']) & (ids == B['dirt']) & (above > 2)
    diff.dead_grass = int((bad & dead_grass).sum())
    bad &= ~dead_grass
    if mask is not None:
        bad &= mask
    pts = np.argwhere(bad)
    rep = ['%s world=%s:%d model=%s:%d' % (R.r_to_world(i + SX0, j + SY0, k + SZ0),
                                           ID_NAMES.get(int(ids[i, j, k])), metas[i, j, k],
                                           ID_NAMES.get(int(mid[i, j, k])), mme[i, j, k]) for (i, j, k) in pts[:20]]
    return len(pts), rep


def verify_world(server_dir, b, F, kind):
    print('\n== world vs design (rotated model)')
    w, W, fb = world_frame(server_dir)
    if kind == 'flat':
        n, rep = diff(F, W)
        res('every block in the %dx%dx%d test box matches the design' % (fb[3] - fb[0] + 1, fb[4] - fb[1] + 1,
            fb[5] - fb[2] + 1), n == 0, '%d mismatches %s (+%d hidden grass blocks under walls turned to dirt '
            'by the game)' % (n, rep[:8], diff.dead_grass))
    else:
        tm = R.rotate_arrays(b.touched.astype(np.int8), np.zeros_like(b.meta))[0].astype(bool)
        n, rep = diff(F, W, tm)
        res('every block the build writes matches the design (natural terrain around it)', n == 0,
            '%d mismatches %s' % (n, rep[:8]))
        liquid = np.isin(W.ids, [B['water'], B['flowing_water'], B['lava'], B['flowing_lava']]) & \
            (F.ids == 0) & tm
        lp = [R.r_to_world(i + SX0, j + SY0, k + SZ0) for (i, j, k) in np.argwhere(liquid)]
        res('no water or lava flowed into the cleared site from the terrain around it', not lp,
            '%d liquid blocks, e.g. %s' % (len(lp), [tuple(int(v) for v in p) for p in lp[:5]]))
    # ---- installer cleanup ----
    px, py, pz = CB.PAD
    left = [(x, y, pz) for x in range(px - 1, px + 4) for y in range(py - 1, py + 8)
            if W.get(*R.world_to_r(x, y, pz))[0] != 0]
    res('installer pad and column removed (air from Y %d to %d)' % (py - 1, py + 7), not left, str(left))
    tes = w.tile_entities(*fb)
    cbs = [(t['x'], t['y'], t['z']) for t in tes if t['id'] == 'Control']
    lab = mw(35, -4, 12)
    res('no command block left except the laboratory prop', cbs == [lab], str(cbs))
    rb = int((W.ids == B['redstone_block']).sum()) - int((F.ids == B['redstone_block']).sum())
    res('no stray redstone blocks', rb == 0, str(rb))
    ents = w.entities(fb[0], 0, fb[2], fb[3], 255, fb[5])
    cnt = collections.Counter(e['id'] for e in ents)
    res('no minecarts, falling blocks or dropped items left', not any(cnt[k] for k in (
        'MinecartCommandBlock', 'FallingSand', 'Item', 'MinecartRideable')), dict(cnt).__repr__())
    # ---- hanging entities and armor stands ----
    want_p, want_s, want_f = [], [], []
    for (et, pos, extra) in b.entities:
        if et == 'Painting':
            motive, facing, _, _ = extra
            want_p.append((R.block(*pos), motive, ({'S': 0, 'W': 1, 'N': 2, 'E': 3}[facing] + 1) % 4))
        elif et == 'ItemFrame':
            item, facing = extra
            want_f.append((R.block(*pos), 'minecraft:' + item, ({'S': 0, 'W': 1, 'N': 2, 'E': 3}[facing] + 1) % 4))
        elif et == 'ArmorStand':
            # the recorded NBT is the emitted (already turned) one
            want_s.append((R.point(*pos), float(re.search(r'Rotation:\[(-?[\d.]+)', extra).group(1)) % 360))
    got_p = [((e['TileX'], e['TileY'], e['TileZ']), e['Motive'], e.get('Facing', e.get('Direction')))
             for e in ents if e['id'] == 'Painting']
    got_f = [((e['TileX'], e['TileY'], e['TileZ']), e['Item']['id'], e.get('Facing', e.get('Direction')))
             for e in ents if e['id'] == 'ItemFrame']
    res('all %d paintings hang where designed, facing the rotated way' % len(want_p),
        sorted(got_p) == sorted(want_p), 'missing %s extra %s' % (sorted(set(want_p) - set(got_p))[:4],
                                                                 sorted(set(got_p) - set(want_p))[:4]))
    res('item frame in place and facing correctly', sorted(got_f) == sorted(want_f), '%s vs %s' % (got_f, want_f))
    got_s = [(tuple(e['Pos']), e['Rotation'][0] % 360) for e in ents if e['id'] == 'ArmorStand']
    ok = len(got_s) == len(want_s) and all(
        any(abs(g[0][0] - p[0]) < 0.01 and abs(g[0][2] - p[2]) < 0.01 and -0.51 < g[0][1] - p[1] < 0.01
            and abs(g[1] - yaw) < 0.5 for g in got_s) for (p, yaw) in want_s)
    res('all %d armor stands in place with rotated yaw' % len(want_s), ok, str(got_s[:3]))
    if kind != 'flat':
        return W
    # ---- design validators on what the server actually built ----
    print('\n== design validators run on the blocks READ BACK from the world')
    errs = V.support_errors(W)
    res('unsupported attachments in the real world', not errs, str(errs[:4]))
    res('fire hazards in the real world', not V.fire_hazards(W))
    saved = W.ids.copy(), W.meta.copy()
    for (mx, y, mz, name, orm) in ((8, 3, 34, 'air', None), (30, 3, 12, None, 4), (60, -4, 24, 'air', None),
                                   (60, -5, 24, 'log', None)):
        rx, ry, rz = R.r_local(mx + X0, y, mz + Z0)
        i = (rx - SX0, ry - SY0, rz - SZ0)
        if name:
            W.ids[i] = B[name]
        if orm:
            W.meta[i] |= orm
    wk = V.Walker(W)
    seen = wk.run(R.r_local(30 + X0, 0, -12 + Z0))
    back = wk.returnable()
    reach = collections.defaultdict(set)
    for (x, z, h) in seen:
        if (x, z, h) in back:
            reach[(x, z)].add(h)
    miss = [n for (n, mx, y, mz) in check.PROBES
            if not any(abs(h - 2 * y) <= 1 for h in reach.get(R.r_local(mx + X0, y, mz + Z0)[::2], ()))]
    res('real world: every room probe reachable on foot from the lawn and back', not miss and seen <= back,
        '%d standing states, %d one-way, unreachable %s' % (len(seen), len(seen - back), miss))
    W.ids[...], W.meta[...] = saved
    lvl = V.block_light(W)
    rx1, _, rz1 = R.r_local(X0 - 2, 0, Z0 + 57)
    rx2, _, rz2 = R.r_local(X0 + 68, 0, Z0 - 2)
    dark = V.dark_spots(W, lvl, (min(rx1, rx2), -10, min(rz1, rz2), max(rx1, rx2), 36, max(rz1, rz2)))
    res('real world: no dark spawnable interior spots', not dark, str(len(dark)))
    return W


# ------------------------------------------------------------- functional ---
class Probe:
    def __init__(self, s, bot):
        self.s, self.bot = s, bot

    def goto(self, x, y, z):
        m = self.bot.mark()
        self.s.cmd('tp %s %.1f %d %.1f' % (BOT, x + 0.5, y, z + 0.5))
        ok = self.bot.wait_event('tp', m, 10, lambda d: abs(d[0] - x - 0.5) < 1e-6 and abs(d[2] - z - 0.5) < 1e-6)
        time.sleep(0.15)
        return ok

    def click(self, x, y, z, kind, pred=None, timeout=3.0):
        self.goto(x, y, z)
        m = self.bot.mark()
        self.bot.use_block(x, y, z)
        return self.bot.wait_event(kind, m, timeout, pred)

    def block(self, x, y, z):
        """(name, meta) via /testforblock from the console (no world save needed)."""
        m = self.s.mark()
        self.s.cmd('testforblock %d %d %d air' % (x, y, z))
        self.s.sync()
        for ln in self.s.since(m):
            if 'Successfully found the block' in ln:
                return ('air', 0)
            mo = re.search(r'The block at .* is (.+?) \(expected', ln)
            if mo:
                return (mo.group(1), None)
        return (None, None)

    def is_block(self, x, y, z, name, meta=-1):
        m = self.s.mark()
        self.s.cmd('testforblock %d %d %d %s %d' % (x, y, z, name, meta))
        self.s.sync()
        return any('Successfully found the block' in ln for ln in self.s.since(m))


def functional(server_dir, kind, F):
    print('\n== functional tests: a player clicks the mechanisms in the built world')
    s = Server(server_dir, fresh=False, props_extra=props(kind))
    s.start()
    bot = Bot(BOT, port=PORT).connect()
    P = Probe(s, bot)
    try:
        s.cmd('time set 1000')
        # ---- secrets ----
        lever, case = mw(10, 3, 30), mw(8, 3, 34)
        P.click(*lever, 'block')
        time.sleep(0.6)
        opened = P.is_block(*case, 'air') and P.is_block(case[0], case[1] - 1, case[2], 'bookshelf')
        P.click(*lever, 'block')
        time.sleep(0.6)
        closed = P.is_block(*case, 'bookshelf')
        res('library bookcase door: lever off drops the bookcase, lever on restores it', opened and closed)
        tap, barrel = mw(57, -4, 24), mw(60, -4, 24)
        P.click(*tap, 'block')
        time.sleep(0.6)
        opened = P.is_block(*barrel, 'air') and P.is_block(barrel[0], barrel[1] - 1, barrel[2], 'log')
        P.click(*tap, 'block')
        time.sleep(0.6)
        closed = P.is_block(*barrel, 'log')
        res('wine-cellar barrel: tap lever sinks the barrel and brings it back', opened and closed)
        vl, vd = mw(4, -3, 36), mw(5, -4, 35)
        P.click(*vl, 'block')
        time.sleep(0.4)
        dmeta = int(F.get(*R.world_to_r(*vd))[1])
        opened = P.is_block(*vd, 'iron_door', dmeta | 4)
        P.click(*vl, 'block')
        time.sleep(0.4)
        closed = P.is_block(*vd, 'iron_door', dmeta)
        vl2 = mw(6, -3, 34)
        P.click(*vl2, 'block')
        time.sleep(0.4)
        opened2 = P.is_block(*vd, 'iron_door', dmeta | 4)
        P.click(*vl2, 'block')
        res('vault iron door opens and shuts from the levers on both sides', opened and closed and opened2)
        ll = mw(26, -3, 6)
        lamps = [mw(x, -4, 6) for x in range(27, 35)]
        lit0 = all(P.is_block(*p, 'lit_redstone_lamp') for p in lamps)
        P.click(*ll, 'block')
        time.sleep(0.6)
        off = all(P.is_block(*p, 'redstone_lamp') for p in lamps)
        P.click(*ll, 'block')
        time.sleep(0.4)
        res('laboratory lamp panel lit, switches off and on with its lever', lit0 and off)
        plate = mw(35, -3, 12)
        m = bot.mark()
        P.goto(*plate)
        whir = bot.wait_event('chat', m, 5, lambda t: 'machine whirs' in t)
        res('laboratory pressure plate runs its command block (player gets the "whirs" message)', bool(whir))
        for label, pos in (('laboratory hatch in the stair cubby', mw(30, 3, 12)),
                           ('escape-tunnel hatch in the vault floor', mw(7, -4, 31))):
            ev = P.click(*pos, 'block', lambda d: d[0] == pos)
            ok = ev is not None and ev[2] & 4 == (0 if F.get(*R.world_to_r(*pos))[1] & 4 else 4)
            P.click(*pos, 'block', lambda d: d[0] == pos)
            res('%s opens' % label, ok)
        wd = mw(15, 18, 2)
        ev = P.click(*wd, 'block', lambda d: d[0] == wd)
        P.click(*wd, 'block', lambda d: d[0] == wd)
        res('wardrobe door to the roof room opens', ev is not None and ev[2] & 4 == 4)
        # ---- every interactive block ----
        wood_doors = {B[n] for n in ('wooden_door', 'spruce_door', 'birch_door', 'jungle_door', 'acacia_door',
                                     'dark_oak_door')}
        gates = {B[n] for n in ('fence_gate', 'spruce_fence_gate', 'birch_fence_gate', 'jungle_fence_gate',
                                'dark_oak_fence_gate', 'acacia_fence_gate')}
        windows = {'chest': 'minecraft:chest', 'trapped_chest': 'minecraft:chest', 'ender_chest': 'minecraft:container',
                   'furnace': 'minecraft:furnace', 'lit_furnace': 'minecraft:furnace',
                   'crafting_table': 'minecraft:crafting_table', 'enchanting_table': 'minecraft:enchanting_table',
                   'anvil': 'minecraft:anvil', 'brewing_stand': 'minecraft:brewing_stand',
                   'dispenser': 'minecraft:dispenser', 'dropper': 'minecraft:dropper', 'hopper': 'minecraft:hopper',
                   'beacon': 'minecraft:beacon'}
        tally = collections.defaultdict(lambda: [0, 0, []])
        for (i, j, k) in np.argwhere(F.ids > 0):
            bid, meta = int(F.ids[i, j, k]), int(F.meta[i, j, k])
            name = ID_NAMES[bid]
            pos = R.r_to_world(i + SX0, j + SY0, k + SZ0)
            if name in windows:
                ev = P.click(*pos, 'window')
                ok = ev is not None and ev[1] == windows[name]
                if ev:
                    bot.close_window(ev[0])
                key = name
            elif name == 'bed' and not meta & 8:
                ev = P.click(*pos, 'chat', lambda t: 'tile.bed' in t)
                ok = ev is not None and 'noSleep' in ev
                key = 'bed (sleep attempt answered, both halves intact)'
            elif bid in wood_doors and not meta & 8:
                ev = P.click(*pos, 'block', lambda d: d[0] == pos)
                ok = ev is not None and ev[2] == meta ^ 4
                P.click(*pos, 'block', lambda d: d[0] == pos)
                key = 'wooden door (opens and closes)'
            elif name == 'trapdoor' or bid in gates:
                ev = P.click(*pos, 'block', lambda d: d[0] == pos)
                ok = ev is not None and ev[2] == meta ^ 4
                P.click(*pos, 'block', lambda d: d[0] == pos)
                key = name + ' (opens and closes)'
            else:
                continue
            tally[key][0] += 1
            tally[key][1] += ok
            if not ok:
                tally[key][2].append((tuple(int(v) for v in pos), ev))
        for key in sorted(tally):
            n, good, badp = tally[key]
            res('%s: %d/%d work' % (key, good, n), good == n, str(badp[:5]))
        res('test player stayed connected', bot.alive, str(bot.disconnect_reason))
    finally:
        bot.close()
        s.stop()


def main():
    server_dir = sys.argv[1]
    kind = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 'flat'
    b = CB.assemble()
    F = R.rotated_frame(b)
    for p in b.expects:                               # game-made piston states are in the model already
        pass
    ver = open(os.path.join(server_dir, 'logs', 'latest.log')).read().split('server version ')[1].split()[0] \
        if os.path.exists(os.path.join(server_dir, 'logs', 'latest.log')) else '?'
    print('== console installation on %s (%s world), view-distance %d, player at %s' % (
        server_dir, kind, CB.MIN_VIEW_DISTANCE, CB.STAND), flush=True)
    t0 = time.time()
    stages = install(server_dir, kind)
    extra = stages.pop() if stages and 'verify' in stages[-1] else {}
    verify = extra.get('verify', {})
    res('recovery drill: pad re-placed, %s pasted a second time, documented cleanup run' % extra.get('repeated'),
        bool(extra.get('cleanup')) and not any('Exception' in l for v in extra['cleanup'].values() for l in v),
        str(extra.get('cleanup')))
    res('documented checks answer as expected', verify and
        any('Successfully found' in l for l in verify[VERIFY_COMMANDS[0]]) and
        not any(l.startswith('Found') for l in verify[VERIFY_COMMANDS[1]] + verify[VERIFY_COMMANDS[2]]) and
        all(any('Successfully found' in l for l in verify[c]) for c in VERIFY_COMMANDS[3:]), str(verify))
    print('  total install time %.0fs' % (time.time() - t0))
    res('every console line answered with its documented completion message', len(stages) == len(console_files()))
    res('no stage lagged a tick past the 60 s watchdog',
        all(not st['lag'] or all(int(re.search(r'(\d+)ms', ln).group(1)) < 60000 for ln in st['lag'])
            for st in stages), str([(st['file'], st['lag']) for st in stages if st['lag']]))
    res('console stays readable: at most 5 installer lines per stage', all(st['lines'] <= 5 for st in stages),
        str([st['lines'] for st in stages]))
    res('no command errors reported in the console', not any(st['errors'] for st in stages),
        str([st['errors'][:2] for st in stages if st['errors']]))
    verify_world(server_dir, b, F, kind)
    if '--no-functional' not in sys.argv:
        functional(server_dir, kind, F)
    fails = [r for r in RESULTS if not r[1]]
    print('\nRESULT: %d passed, %d failed' % (len(RESULTS) - len(fails), len(fails)))
    out = os.path.join(ROOT, 'out')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'console_test_%s_%s.json' % (os.path.basename(server_dir.rstrip('/')), kind)),
              'w') as fh:
        json.dump({'stages': stages, 'verify': verify, 'extra': extra, 'results': RESULTS}, fh, indent=1)
    return not fails


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
