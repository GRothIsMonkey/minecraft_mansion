"""Static validation of the server-console edition (rotated, absolute placement).

  1. Replays the emitted ABSOLUTE command text with an independent interpreter and compares
     the result with the rotated voxel model (catches coordinate / clone-corner / metadata
     text errors without a server).
  2. Re-runs the design checks on the ROTATED model: supports (uses the rotated metadata to
     find each torch/ladder/sign/lever/button/trapdoor/door/bed's support), fire safety,
     two-way walkability to every room probe (secret doors open), and interior lighting.
  3. Position / orientation / installer-safety checks.
"""
import collections
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                     # noqa: E402
import console_build as CB             # noqa: E402
import rotation as R                   # noqa: E402
import validate as V                   # noqa: E402
import check                           # noqa: E402
from blockids import BLOCK_IDS, ID_NAMES   # noqa: E402
from engine import SX0, SY0, SZ0       # noqa: E402
from mansion_base import X0, Z0        # noqa: E402

OK = []
FAIL = []


def verdict(name, good, detail=''):
    (OK if good else FAIL).append(name)
    print('  [%s] %s%s' % ('PASS' if good else 'FAIL', name, (' - ' + detail) if detail else ''))
    return good


def mansion_to_world(mx, y, mz):
    return R.block(mx + X0, y, mz + Z0)


def mansion_to_r(mx, y, mz):
    return R.r_local(mx + X0, y, mz + Z0)


# ------------------------------------------------------------ interpreter --
def fresh_terrain():
    shape = (R.SX1 - SX0 + 1, 72 - SY0 + 1, R.SZ1 - SZ0 + 1)
    ids = np.zeros(shape, dtype=np.int16)
    me = np.zeros(shape, dtype=np.int8)
    ids[:, :(-5 - SY0) + 1, :] = BLOCK_IDS['stone']
    ids[:, (-4 - SY0):(-2 - SY0) + 1, :] = BLOCK_IDS['dirt']
    ids[:, (-1 - SY0), :] = BLOCK_IDS['grass']
    return ids, me


def replay(cmds):
    """Apply absolute fill/setblock/clone text to a world-aligned voxel array."""
    ids, me = fresh_terrain()

    def idx(wx, wy, wz):
        rx, ry, rz = R.world_to_r(wx, wy, wz)
        return rx - SX0, ry - SY0, rz - SZ0

    def sl(a, b):
        (i1, j1, k1), (i2, j2, k2) = idx(*a), idx(*b)
        return (slice(min(i1, i2), max(i1, i2) + 1), slice(min(j1, j2), max(j1, j2) + 1),
                slice(min(k1, k2), max(k1, k2) + 1))

    for t in cmds:
        p = t.split(' ')
        if p[0] == 'setblock':
            x, y, z = map(int, p[1:4])
            ids[idx(x, y, z)] = BLOCK_IDS[p[4]]
            me[idx(x, y, z)] = int(p[5]) if len(p) > 5 else 0
        elif p[0] == 'fill':
            a, b = tuple(map(int, p[1:4])), tuple(map(int, p[4:7]))
            bid = BLOCK_IDS[p[7]]
            m = int(p[8]) if len(p) > 8 else 0
            mode = p[9] if len(p) > 9 else None
            s = sl(a, b)
            if mode in (None, 'destroy') or (mode == 'replace' and len(p) == 10):
                ids[s] = bid
                me[s] = m
            elif mode == 'keep':
                mask = ids[s] == 0
                ids[s][mask] = bid
                me[s][mask] = m
            elif mode == 'replace':
                mask = ids[s] == BLOCK_IDS[p[10]]
                if len(p) > 11:
                    mask &= me[s] == int(p[11])
                ids[s][mask] = bid
                me[s][mask] = m
            elif mode in ('hollow', 'outline'):
                sub_i, sub_m = ids[s], me[s]
                shell = np.ones(sub_i.shape, dtype=bool)
                shell[1:-1, 1:-1, 1:-1] = False
                if mode == 'hollow':
                    sub_i[...] = 0
                    sub_m[...] = 0
                sub_i[shell] = bid
                sub_m[shell] = m
            else:
                raise ValueError(t)
        elif p[0] == 'clone':
            a, b = tuple(map(int, p[1:4])), tuple(map(int, p[4:7]))
            d = tuple(map(int, p[7:10]))
            s = sl(a, b)
            src_i, src_m = ids[s].copy(), me[s].copy()
            lo = (min(a[0], b[0]), min(a[1], b[1]), min(a[2], b[2]))
            hi = (max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2]))
            dhi = (d[0] + hi[0] - lo[0], d[1] + hi[1] - lo[1], d[2] + hi[2] - lo[2])
            ds = sl(d, dhi)
            if 'masked' in p[10:]:
                mask = src_i != 0
                ids[ds][mask] = src_i[mask]
                me[ds][mask] = src_m[mask]
            else:
                ids[ds] = src_i
                me[ds] = src_m
        elif p[0] in ('summon', 'kill'):
            pass
        else:
            raise ValueError('unexpected command: ' + t)
    return ids, me


# ------------------------------------------------------------------ main ----
def main():
    b = CB.assemble()
    F = R.rotated_frame(b)
    cmds = [c.text for c in b.cmds]
    print('console build: %d commands, %d chars' % (len(cmds), sum(map(len, cmds))))

    print('\n== 1. command text replay vs rotated model')
    ids, me = replay(cmds)
    top = ids.shape[1]
    fid, fme = F.ids[:, :top, :], F.meta[:, :top, :]
    exp_cells = {R.r_local(*p) for p in b.expects}
    bad = np.argwhere((ids != fid) | ((me != fme) & (fid != 0)))
    bad = [tuple(int(v) for v in (i + SX0, j + SY0, k + SZ0)) for (i, j, k) in bad]
    unexplained = [p for p in bad if p not in exp_cells]
    verdict('replayed absolute commands == rotated model', not unexplained,
            '%d cells differ, all %d are piston cells the game moves itself' % (len(bad), len(bad))
            if not unexplained else 'e.g. %s' % unexplained[:10])
    verdict('no relative "~" coordinates in build commands', not any('~' in c for c in cmds))
    wx1, wy1, wz1, wx2, wy2, wz2 = CB.BUILD_BOX
    outside = []
    for c in b.cmds:
        if c.box:
            a = R.box(*c.box)
            if a[0] < wx1 or a[1] < wy1 or a[2] < wz1 or a[3] > wx2 or a[4] > wy2 or a[5] > wz2:
                outside.append(c.text)
    for (e, pos, extra) in b.entities:
        wp = R.block(*[int(math.floor(v)) for v in pos])
        if not (wx1 <= wp[0] <= wx2 and wy1 <= wp[1] <= wy2 and wz1 <= wp[2] <= wz2):
            outside.append(e)
    verdict('every block write and entity lies inside the documented build box', not outside,
            'X %d..%d  Y %d..%d  Z %d..%d' % (wx1, wx2, wy1, wy2, wz1, wz2))

    print('\n== 2. position and orientation')
    door = [mansion_to_world(30, 3, 0), mansion_to_world(31, 3, 0)]
    dn = [ID_NAMES[F.get(*R.world_to_r(*d))[0]] for d in door]
    dm = [F.get(*R.world_to_r(*d))[1] for d in door]
    verdict('front doors at X=-251, Z 266-267, door feet Y=76', [d[0] for d in door] == [-251, -251]
            and sorted(d[2] for d in door) == [266, 267] and all(d[1] == 76 for d in door),
            'door blocks %s (%s)' % (door, dn))
    # door lower meta 2 = the player looks WEST (-X) walking in, EAST (+X) walking out
    verdict('front door leaves face east/west (walk in = -X, walk out = +X)', dm == [2, 2], 'meta %s' % dm)
    verdict('mansion mirror axis on Z = 267.0 (entrance centre)', R.point(43.0, 0, 0)[2] == 267.0)
    lawn = R.block(0, -1, 0)[1]
    verdict('lawn grass at Y=72 (stand on it at feet Y=73); floor of the house at Y=75', lawn == 72
            and mansion_to_world(30, 2, 5)[1] == 75)
    # bulk: count non-air blocks at or above ground, east vs west of the door plane
    nz = np.argwhere(F.ids[:, (0 - SY0):, :] != 0)
    wxs = nz[:, 0] + SX0 + R.OFF[0]
    west, east = int((wxs < -251).sum()), int((wxs > -251).sum())
    verdict('bulk of the mansion lies west of the entrance (X < -251)', west > 10 * east,
            '%d blocks west, %d east (portico, steps, courtyard, fountain, drive)' % (west, east))
    fountain = mansion_to_world(26, 1, -16)
    verdict('fountain, courtyard and drive are east of the facade', fountain[0] > -251,
            'fountain rim at %s' % (fountain,))
    garden = mansion_to_world(30, 1, 46)
    verdict('rear garden (steps, well, gazebo) is west of the house', garden[0] < -251 - 40,
            'rear steps at %s' % (garden,))

    print('\n== 3. installer placement')
    px, py, pz = CB.PAD
    col = CB.COLUMN

    def inside(p):
        return wx1 <= p[0] <= wx2 and wy1 <= p[1] <= wy2 and wz1 <= p[2] <= wz2
    cells = [(x, y, pz) for x in range(col[0], col[3] + 1) for y in range(py, col[4] + 1)]
    verdict('pad + installer column are outside every block the build writes',
            not any(inside(c) for c in cells), 'pad %s, column X %d..%d Y %d..%d Z %d' %
            (CB.PAD, col[0], col[3], col[1], col[4], col[2]))
    verdict('installer is above the tallest part of the build and above normal tree height',
            py > wy2 and py >= 120, 'pad Y %d, build top Y %d' % (py, wy2))
    verdict('player stand point is outside the build box', not inside(CB.STAND), '%s' % (CB.STAND,))
    hd = math.hypot(CB.STAND[0] - px, CB.STAND[2] - pz)
    verdict('installer within 16 blocks (horizontal) of the stand point (Spigot entity activation)', hd <= 16,
            '%.1f blocks' % hd)
    scx, scz = CB.STAND[0] >> 4, CB.STAND[2] >> 4
    need = max(abs(scx - (wx1 >> 4)), abs(scx - (wx2 >> 4)), abs(scz - (wz1 >> 4)), abs(scz - (wz2 >> 4)),
               abs(scx - ((px - 32) >> 4)), abs(scx - ((px + 32) >> 4)))
    verdict('view-distance needed at the stand point <= documented minimum', need <= CB.MIN_VIEW_DISTANCE,
            'needs %d chunks, documented %d' % (need, CB.MIN_VIEW_DISTANCE))

    print('\n== 4. metadata tables vs the engine direction encoders (proven on 1.8 servers)')
    import engine as EN
    cw = R.CW
    H = (EN.N, EN.E, EN.S, EN.W)
    sem = []
    for d in H:
        for up in (False, True):
            sem.append(('oak_stairs', EN.stairs(d, up), EN.stairs(cw[d], up)))
        for o in (False, True):
            sem.append(('dark_oak_door', EN.door_lower(d, o), EN.door_lower(cw[d], o)))
            for top in (False, True):
                sem.append(('trapdoor', EN.trapdoor(d, o, top), EN.trapdoor(cw[d], o, top)))
        for on in (False, True):
            sem.append(('lever', EN.lever(d, on), EN.lever(cw[d], on)))
        for hd in (False, True):
            sem.append(('bed', EN.bed(d, hd), EN.bed(cw[d], hd)))
        for n in ('torch', 'redstone_torch'):
            sem.append((n, EN.torch(d), EN.torch(cw[d])))
        for n in ('ladder', 'wall_sign', 'wall_banner', 'chest', 'furnace', 'dispenser', 'dropper', 'skull',
                  'ender_chest', 'hopper'):
            sem.append((n, EN.wallmount(d), EN.wallmount(cw[d])))
        sem.append(('stone_button', EN.button(d), EN.button(cw[d])))
        for ext in (False, True):
            sem.append(('sticky_piston', EN.piston(d, ext), EN.piston(cw[d], ext)))
        for dl in (1, 2, 3, 4):
            sem.append(('unpowered_repeater', EN.repeater(d, dl), EN.repeater(cw[d], dl)))
        for n in ('fence_gate', 'pumpkin', 'lit_pumpkin', 'unpowered_comparator', 'anvil', 'tripwire_hook'):
            sem.append((n, EN.horiz(d), EN.horiz(cw[d])))
    for d in (EN.UP, EN.DOWN):
        sem.append(('sticky_piston', EN.piston(d), EN.piston(d)))
        sem.append(('stone_button', EN.button(d), EN.button(d)))
    sem.append(('torch', EN.torch(EN.UP), EN.torch(EN.UP)))
    sem.append(('log', EN.log_axis('X'), EN.log_axis('Z')))
    sem.append(('log2', EN.log_axis('Z', 1), EN.log_axis('X', 1)))
    sem.append(('log', EN.log_axis('Y', 2), EN.log_axis('Y', 2)))
    wrong = [(n, m, R.rot_meta(n, m), want) for (n, m, want) in sem if R.rot_meta(n, m) != want]
    verdict('every directional metadata rotates like its direction (%d cases)' % len(sem), not wrong,
            '' if not wrong else str(wrong[:8]))
    four = [(n, m) for n in list(R.STAIRS)[:1] + list(R.DOORS)[:1] + list(R.TRAPDOORS) + ['torch', 'lever',
            'stone_button', 'ladder', 'bed', 'standing_sign', 'vine', 'rail', 'golden_rail', 'log', 'quartz_block',
            'red_mushroom_block', 'double_plant', 'skull']
            for m in range(16)
            if R.rot_meta(n, R.rot_meta(n, R.rot_meta(n, R.rot_meta(n, m)))) != m]
    verdict('four quarter turns give back the original metadata', not four, str(four[:8]))

    print('\n== 5. design checks on the ROTATED model')
    errs = V.support_errors(F)
    verdict('unsupported attachments (torches, ladders, signs, levers, buttons, trapdoors, doors, beds...)',
            not errs, '%d' % len(errs) + ('' if not errs else ' e.g. %s' % errs[:5]))
    fh = V.fire_hazards(F)
    verdict('fire hazards', not fh, '%d' % len(fh))
    # open the secret doors like the design check does
    def rset(mx, y, mz, name=None, meta_or=None):
        rx, ry, rz = mansion_to_r(mx, y, mz)
        i = (rx - SX0, ry - SY0, rz - SZ0)
        if name is not None:
            F.ids[i] = BLOCK_IDS[name]
        if meta_or is not None:
            F.meta[i] |= meta_or
    saved = F.ids.copy(), F.meta.copy()
    rset(8, 3, 34, 'air')            # library bookcase pulled down
    rset(30, 3, 12, meta_or=4)       # laboratory hatch open
    rset(60, -4, 24, 'air')          # wine-cellar barrel sunk
    rset(60, -5, 24, 'log')
    w = V.Walker(F)
    start = mansion_to_r(30, 0, -12)
    seen = w.run(start)
    back = w.returnable()
    reach = collections.defaultdict(set)
    for (x, z, h) in seen:
        if (x, z, h) in back:
            reach[(x, z)].add(h)
    traps = len(seen - back)
    verdict('walkability: no one-way traps', traps == 0, '%d standing states, %d one-way' % (len(seen), traps))
    missing = []
    for (name, mx, y, mz) in check.PROBES:
        rx, ry, rz = mansion_to_r(mx, y, mz)
        if not any(abs(h - 2 * ry) <= 1 for h in reach.get((rx, rz), ())):
            missing.append(name)
    verdict('all %d room probes reachable from the front lawn and back again' % len(check.PROBES),
            not missing, ', '.join(missing))
    F.ids[...], F.meta[...] = saved
    lvl = V.block_light(F)
    rx1, _, rz1 = R.r_local(X0 - 2, 0, Z0 + 57)
    rx2, _, rz2 = R.r_local(X0 + 68, 0, Z0 - 2)
    dark = V.dark_spots(F, lvl, (min(rx1, rx2), -10, min(rz1, rz2), max(rx1, rx2), 36, max(rz1, rz2)))
    verdict('dark spawnable interior spots', not dark, '%d' % len(dark))

    print('\n== 6. console pastes')
    st = CB.pack(b)
    lines = [CB.setup_command()] + [p for p, _, _ in st]
    verdict('every console line <= %d characters, printable ASCII, no leading "/"' % CB.LIMIT,
            all(len(p) <= CB.LIMIT and not p.startswith('/') and all(32 <= ord(c) < 127 for c in p) for p in lines),
            '%d lines, longest %d' % (len(lines), max(map(len, lines))))
    carried = []
    for k, (_, body, (a, z)) in enumerate(st):
        n_foot = len(CB.footer(k + 2, len(st) + 1))
        carried += body[len(CB.HEADER):len(body) - n_foot]
    verdict('the stages carry every build command exactly once, in order', carried == cmds)
    print('\nRESULT: %d passed, %d failed' % (len(OK), len(FAIL)))
    return not FAIL


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
