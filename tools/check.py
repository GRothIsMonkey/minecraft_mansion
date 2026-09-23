"""Run all static checks on the assembled mansion and print a report."""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np                                  # noqa: E402
import build                                        # noqa: E402
import validate as V                                # noqa: E402
from mansion_base import X0, Z0                     # noqa: E402

# (name, mansion x, feet y, mansion z)
PROBES = [
    ('foyer', 26, 3, 5), ('landing', 30, 7, 15), ('W gallery', 23, 11, 6), ('E gallery', 38, 11, 6),
    ('front gallery', 30, 11, 2), ('salon', 30, 3, 25), ('conservatory', 27, 3, 41),
    ('W hall', 19, 3, 20), ('E hall', 42, 3, 20), ('study', 9, 3, 7), ('map room', 1, 3, 1),
    ('bath F1', 4, 3, 10), ('corridor W F1', 10, 3, 12), ('library', 3, 3, 30),
    ('library gallery', 5, 11, 17), ('secret study', 12, 3, 36), ('drawing room', 46, 3, 5),
    ('breakfast nook', 57, 3, 5), ('corridor E F1', 50, 3, 12), ('dining', 46, 3, 18),
    ('kitchen', 47, 3, 34), ('pantry', 57, 3, 37), ('back stairs F1', 56, 3, 14),
    ('stair cubby', 29, 3, 13), ('portico balcony', 30, 11, -3), ('rear balcony', 30, 11, 40),
    ('blue room', 9, 11, 5), ('tower W F2', 2, 11, 2), ('bath W F2', 4, 11, 10), ('corridor W F2', 10, 11, 12),
    ('scholar room', 8, 11, 37), ('W hall F2', 19, 11, 20), ('E hall F2', 42, 11, 20), ('lounge', 30, 11, 24),
    ('master bedroom', 31, 11, 34), ('master bath', 21, 11, 29), ('closet', 40, 11, 31),
    ('rose room', 47, 11, 5), ('tower E F2', 58, 11, 2), ('corridor E F2', 50, 11, 12), ('linen hall', 46, 11, 20),
    ('green room', 55, 11, 20), ('green balcony', 62, 11, 18), ('billiards', 47, 11, 36),
    ('gallery F3', 25, 18, 6), ('alcove F3', 30, 18, 2), ('music room', 34, 18, 18), ('trophy room', 30, 18, 33),
    ('W hall F3', 20, 18, 30), ('E hall F3', 41, 18, 30), ('old bedroom', 9, 18, 5), ('washroom', 4, 18, 10),
    ('nursery', 6, 18, 17), ('lumber room', 8, 18, 29), ('tower W F3', 3, 18, 2), ('star room', 3, 25, 4),
    ('observatory', 5, 31, 5), ('governess', 49, 18, 3), ('tower E F3', 57, 18, 5), ('NE lookout', 57, 25, 5),
    ('servants', 50, 18, 18), ('laundry', 50, 18, 36), ('secret attic room', 12, 24, 4),
    ('B corridor', 30, -4, 15), ('archive', 8, -4, 11), ('crypt', 8, -4, 20), ('storage hall', 26, -4, 21),
    ('cistern', 20, -4, 31), ('causeway', 30, -4, 37), ('B storage', 46, -4, 4), ('NE tower cellar', 57, -4, 4),
    ('wine cellar', 58, -4, 22), ('utility', 50, -4, 34), ('wine stash', 64, -4, 24),
    ('redstone room', 30, -4, 8), ('antechamber', 4, -4, 38), ('vault', 8, -4, 32), ('tunnel', 7, -10, 40),
    ('hideout', 8, -10, 53), ('back stairs B', 56, -4, 13), ('central attic', 30, 24, 10),
    ('cupola', 31, 36, 19), ('widow walk', 28, 36, 15), ('rear steps', 30, 1, 46), ('gazebo', 54, 0, 49),
    ('kitchen garden', 66, 0, 35), ('fountain rim', 26, 1, -16), 
]


def local(x, y, z):
    return (x + X0, y, z + Z0)


def main(extra_probes=(), start=(30, 0, -12), open_secret=True, verbose=True):
    b = build.assemble()
    print('commands: %d, chars: %d' % (len(b.cmds), sum(len(c.text) for c in b.cmds)))
    # --- supports ---
    errs = V.support_errors(b)
    print('\n== unsupported attachments: %d' % len(errs))
    for e in errs[:60]:
        x, y, z = e[0] - X0, e[1], e[2] - Z0
        print('  (%d,%d,%d) %s:%d %s -> %s' % (x, y, z, e[3], e[4], e[5], e[6]))
    # --- fire ---
    fh = V.fire_hazards(b)
    print('\n== fire hazards: %d' % len(fh))
    for f in fh[:20]:
        print('  ', f)
    # --- walk ---
    if open_secret:
        # simulate the library bookcase door opened (lever off)
        from engine import SX0, SY0, SZ0
        lx, ly, lz = local(8, 3, 34)
        b.ids[lx - SX0, ly - SY0, lz - SZ0] = 0
        # redstone-room hatch opened
        lx, ly, lz = local(30, 3, 12)
        b.meta[lx - SX0, ly - SY0, lz - SZ0] |= 4
        # wine cellar barrel dropped (lever off)
        from blockids import BLOCK_IDS as BI
        lx, ly, lz = local(60, -4, 24)
        b.ids[lx - SX0, ly - SY0, lz - SZ0] = 0
        b.ids[lx - SX0, ly - 1 - SY0, lz - SZ0] = BI['log']
    w = V.Walker(b)
    sx, sy, sz = local(*start)
    seen = w.run((sx, sy, sz))
    back = w.returnable()
    reach = defaultdict(set)
    for (x, z, h) in seen:
        if (x, z, h) in back:          # must be able to walk back out, too
            reach[(x, z)].add(h)
    trapped = defaultdict(set)
    for (x, z, h) in seen - back:
        trapped[(x, z)].add(h)
    print('\n== walkability: %d standing states reached, %d are one-way traps' % (len(seen), len(seen - back)))
    tr = sorted(trapped)
    if tr:
        print('  trap cells e.g.', [(x - X0, z - Z0, sorted(trapped[(x, z)])[:3]) for (x, z) in tr[:25]])
    bad = 0
    for (name, x, y, z) in list(PROBES) + list(extra_probes):
        lx, ly, lz = local(x, y, z)
        hs = reach.get((lx, lz), set())
        ok = any(abs(h - 2 * ly) <= 1 for h in hs)
        if not ok:
            bad += 1
        if verbose or not ok:
            print('  %-18s %s  (heights seen here: %s)' % (name, 'OK' if ok else 'UNREACHABLE',
                                                         sorted(h / 2 for h in hs)[:6]))
    # --- light ---
    lvl = V.block_light(b)
    box = (X0 - 2, -10, Z0 - 2, X0 + 68, 36, Z0 + 57)
    dark = V.dark_spots(b, lvl, box)
    print('\n== dark spawnable interior spots (<8): %d' % len(dark))
    byfloor = defaultdict(list)
    for (x, y, z, l) in dark:
        byfloor[y].append((x - X0, z - Z0, l))
    for y in sorted(byfloor):
        pts = byfloor[y]
        print('  y=%d: %d spots, e.g. %s' % (y, len(pts), pts[:12]))
    return b, seen, dark, errs


if __name__ == '__main__':
    main()


def dark_map(b, dark, yfeet, path):
    """Render floor plan at feet level yfeet with dark spots in red."""
    from PIL import Image, ImageDraw
    import render
    from engine import SX0, SY0, SZ0
    x1, x2 = X0 - 3, X0 + 64
    z1, z2 = Z0 - 9, Z0 + 46
    sc = 10
    img = Image.new('RGB', ((x2 - x1) * sc, (z2 - z1) * sc), (20, 20, 20))
    d = ImageDraw.Draw(img)
    for x in range(x1, x2):
        for z in range(z1, z2):
            i, k = x - SX0, z - SZ0
            j = yfeet - SY0
            bid = int(b.ids[i, j, k])
            if bid == 0:
                bid, mm = int(b.ids[i, j - 1, k]), int(b.meta[i, j - 1, k])
                c = render._shade(render.color(bid, mm), 0.6)
            else:
                c = render.color(bid, int(b.meta[i, j, k]))
            d.rectangle([(x - x1) * sc, (z - z1) * sc, (x - x1) * sc + sc - 1, (z - z1) * sc + sc - 1], fill=c)
    for (x, y, z, l) in dark:
        if y == yfeet:
            px, pz = (x - x1) * sc, (z - z1) * sc
            d.rectangle([px + 2, pz + 2, px + sc - 3, pz + sc - 3], fill=(255, 0, 0))
            d.text((px + 2, pz), str(l), fill=(255, 255, 255))
    for xx in range(x1, x2):
        if (xx - X0) % 5 == 0:
            d.line([((xx - x1) * sc, 0), ((xx - x1) * sc, (z2 - z1) * sc)], fill=(90, 90, 90))
            d.text(((xx - x1) * sc + 1, 1), str(xx - X0), fill=(255, 255, 0))
    for zz in range(z1, z2):
        if (zz - Z0) % 5 == 0:
            d.line([(0, (zz - z1) * sc), ((x2 - x1) * sc, (zz - z1) * sc)], fill=(90, 90, 90))
            d.text((1, (zz - z1) * sc + 1), str(zz - Z0), fill=(255, 255, 0))
    img.save(path)
