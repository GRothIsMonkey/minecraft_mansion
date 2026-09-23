"""Export the finished Claude + Astra mansion as resources for the Bukkit/Spigot plugin.

    python3 plugin_export.py

Writes plugin/src/main/resources/ashgrove/:
  commands.txt   every build command of the final design, in the exact tested order:
                 the 3356 base commands (console_02..24) followed by the 1162 Astra commands
                 (astra_02..10).  Only the minecart-installer wrapping is left out.  The
                 generator proves the list is exactly what the 34 shipped console files run
                 by re-packing it and comparing with FINAL_MANIFEST.json (all 34 hashes).
  expected.bin.gz the finished design, block by block, over the build box, so the plugin can
                 verify the real world after building (see encoding below).
  manifest.json  counts, hashes, coordinates and the expected paintings / armor stands /
                 item frame.

expected.bin (before gzip): for every cell of the build box, looping y (outer), z, x
(inner), two bytes:  block id,  then  flags = meta | class << 4 | written << 7.
  written  the build writes this cell (348,046 cells); other cells keep your terrain
  class 0  id and data must match exactly
        1  id must match; data is the game's (leaf decay bits, dust power, fire age,
           upper half of tall plants)
        2  grass under an opaque block: grass or dirt (vanilla turns it to dirt)
        3  air: air, or water that flowed there from the fountain
        4  water: still or flowing water
"""
import gzip
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                     # noqa: E402
import astra_build as A                # noqa: E402
import astra_design as D               # noqa: E402
import console_build as CB             # noqa: E402
import rotation as R                   # noqa: E402
import validate as V                   # noqa: E402
from blockids import BLOCK_IDS as B    # noqa: E402
from engine import SX0, SY0, SZ0       # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'plugin', 'src', 'main', 'resources', 'ashgrove')


def verify_against_shipped(base, b):
    """Re-pack the command lists exactly as the console editions did; every file must match."""
    fm = json.load(open(os.path.join(ROOT, 'FINAL_MANIFEST.json')))
    got = {}
    lines = [CB.setup_command()] + [p for p, _, _ in CB.pack(base)]
    for k, t in enumerate(lines, 1):
        got['commands_console/console_%02d.txt' % k] = t + '\n'
    for k, (t, _, _) in enumerate(A.pack(b), 1):
        got['commands_astra/astra_%02d.txt' % k] = t + '\n'
    for st in fm['stages']:
        h = getattr(hashlib, st['hash_algorithm'])(got[st['file']].encode()).hexdigest()
        if h != st['hash']:
            raise SystemExit('generator output differs from the shipped %s' % st['file'])
    return len(fm['stages'])


def expected_cells(b):
    F = R.rotated_frame(b)
    rot_touched = R.rotate_arrays(b.touched.astype(np.int8), np.zeros_like(b.meta))[0].astype(bool)
    x1, y1, z1, x2, y2, z2 = CB.BUILD_BOX
    (i1, j1, k1) = [v - o for v, o in zip(R.world_to_r(x1, y1, z1), (SX0, SY0, SZ0))]
    (i2, j2, k2) = [v - o for v, o in zip(R.world_to_r(x2, y2, z2), (SX0, SY0, SZ0))]
    sl = (slice(i1, i2 + 1), slice(j1, j2 + 1), slice(k1, k2 + 1))
    ids = F.ids[sl].astype(np.int32)
    meta = F.meta[sl].astype(np.int32) & 15
    written = rot_touched[sl]
    op = V.light_opacity(F.ids)[sl]
    above = np.zeros_like(op)
    above[:, :-1, :] = op[:, 1:, :]
    cls = np.zeros_like(ids)
    for n in ('leaves', 'leaves2', 'redstone_wire', 'fire', 'double_plant'):
        cls[ids == B[n]] = 1
    cls[(ids == B['grass']) & (above > 2)] = 2
    cls[ids == 0] = 3
    cls[(ids == B['water']) | (ids == B['flowing_water'])] = 4
    # lower halves of tall plants carry their variant: keep them exact
    cls[(ids == B['double_plant']) & (meta < 8)] = 0
    assert ids.max() < 256
    flags = meta | (cls << 4) | (written.astype(np.int32) << 7)
    # [x, y, z] -> loop order y, z, x
    out = np.stack([ids, flags], axis=-1).transpose(1, 2, 0, 3).astype(np.uint8)
    return out.tobytes(), int(written.sum())


def main():
    base, b = D.assemble()
    n_files = verify_against_shipped(base, b)
    cmds = [c.text for c in b.cmds]
    assert all(all(32 <= ord(ch) < 127 for ch in c) and '~' not in c for c in cmds)
    os.makedirs(OUT, exist_ok=True)
    text = '\n'.join(cmds) + '\n'
    with open(os.path.join(OUT, 'commands.txt'), 'w', newline='\n') as fh:
        fh.write(text)
    cells, n_written = expected_cells(b)
    with gzip.GzipFile(os.path.join(OUT, 'expected.bin.gz'), 'wb', mtime=0) as fh:
        fh.write(cells)
    ents = []
    for (et, pos, extra) in b.entities:
        if et == 'Painting':
            motive, facing, _, _ = extra
            ents.append({'type': 'Painting', 'block': list(R.block(*pos)), 'motive': motive,
                         'facing': ({'S': 0, 'W': 1, 'N': 2, 'E': 3}[facing] + 1) % 4})
        elif et == 'ItemFrame':
            item, facing = extra
            ents.append({'type': 'ItemFrame', 'block': list(R.block(*pos)), 'item': item,
                         'facing': ({'S': 0, 'W': 1, 'N': 2, 'E': 3}[facing] + 1) % 4})
        elif et == 'ArmorStand':
            ents.append({'type': 'ArmorStand', 'pos': list(R.point(*pos))})
    manifest = {
        'name': 'Ashgrove Manor (final Claude + Astra, source 4be5b07)',
        'source_commit': '4be5b07f0e33010fcd4dee65cd13ffa6b6fb0320',
        'commands': len(cmds), 'base_commands': b.astra_start, 'astra_commands': len(cmds) - b.astra_start,
        'commands_sha256': hashlib.sha256(text.encode()).hexdigest(),
        'shipped_files_verified': n_files,
        'entrance': list(CB.ENTRANCE), 'build_box': list(CB.BUILD_BOX),
        'written_cells': n_written,
        'expected_sha256': hashlib.sha256(cells).hexdigest(),
        # the base installer removed dropped items in the site after every base stage
        'base_item_sweep': 'kill @e[type=Item,x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d]' % (
            CB.BUILD_BOX[0], CB.BUILD_BOX[1], CB.BUILD_BOX[2], CB.BUILD_BOX[3] - CB.BUILD_BOX[0],
            CB.BUILD_BOX[4] - CB.BUILD_BOX[1], CB.BUILD_BOX[5] - CB.BUILD_BOX[2]),
        'entities': ents,
    }
    with open(os.path.join(OUT, 'manifest.json'), 'w') as fh:
        json.dump(manifest, fh, indent=1)
    print('verified %d shipped files; wrote %d commands (%d base + %d Astra), %d written cells'
          % (n_files, len(cmds), b.astra_start, len(cmds) - b.astra_start, n_written))
    return manifest


if __name__ == '__main__':
    main()
