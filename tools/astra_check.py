"""Validate the combined design plus preservation and the exact shipped patch."""
import hashlib
import json
import sys
import numpy as np

import astra_build as A
import astra_design as D
import console_build as CB
import console_check as C
from blockids import BLOCK_IDS as B


def main():
    C.OK.clear()
    C.FAIL.clear()
    base,b = D.assemble()
    original = CB.assemble
    CB.assemble = lambda: b
    try:
        good = C.main()
    finally:
        CB.assemble = original
    C.verdict('all original tile-entity NBT and hanging entities preserved',
              base.te == b.te and base.entities == b.entities)
    protected = [n for n in B if any(s in n for s in ('chest','furnace','door','piston','redstone','repeater',
                 'comparator','ladder','lever','button','bed','crafting','enchant','brewing','anvil','hopper',
                 'dispenser','dropper','pressure_plate'))]
    mask = np.isin(base.ids,[B[n] for n in protected])
    C.verdict('all original utility and mechanism blocks retain ID and metadata',
              np.array_equal(base.ids[mask],b.ids[mask]) and np.array_equal(base.meta[mask],b.meta[mask]))
    # All interior air remains air: decorative edits cannot seal a room or route.
    from engine import SX0,SY0,SZ0
    interior = np.zeros_like(mask)
    interior[12-SX0:74-SX0,-10-SY0:23-SY0,26-SZ0:67-SZ0]=True
    C.verdict('no new solid blocks in the interior circulation volume',
              not np.any(interior & (base.ids==0) & (b.ids!=0)))
    patch = b.cmds[b.astra_start:]
    frozen = json.loads((A.ROOT/'commands_console/manifest.json').read_text())
    frozen_bytes = [(A.ROOT/'commands_console'/s['file']).read_bytes() for s in frozen['stages']]
    C.verdict('all 24 base console files retain their manifest hashes and regenerate byte-for-byte',
              len(frozen_bytes)==24 and
              all(hashlib.sha1(data).hexdigest()==s['sha1'] for data,s in zip(frozen_bytes,frozen['stages'])) and
              frozen_bytes==[(p+'\n').encode() for p in CB.all_pastes(base)])
    C.verdict('patch uses only filtered 1.8 fills, never inventory or entity resets',
              all(c.text.startswith('fill ') and ' replace ' in c.text and not any(x in c.text for x in '{}~') for c in patch))
    paths = A.pack(b)
    manifest = json.loads((A.ROOT/'commands_astra/manifest.json').read_text())
    shipped = [(A.ROOT/'commands_astra'/s['file']).read_text().rstrip('\n') for s in manifest['stages']]
    C.verdict('shipped Astra stages equal regeneration using measured costs',shipped==[p[0] for p in paths])
    C.verdict('Astra manifest hashes match every shipped file',all(
        hashlib.sha256((t+'\n').encode()).hexdigest()==s['sha256'] for t,s in zip(shipped,manifest['stages'])))
    C.verdict('every Astra stage is printable ASCII, no slash, within character and measured work budgets',
              all(len(t)<=A.LIMIT and not t.startswith('/') and all(32<=ord(c)<127 for c in t)
                  and work<=A.COST_CAP for t,_,work in paths))
    carried = [t for _,cmds,_ in paths for t in cmds]
    C.verdict('Astra stages carry exactly the add-on commands in order',carried==[c.text for c in patch])
    # Applying the same condition-filtered commands twice must have no effect.
    full = [c.text for c in b.cmds]
    once = C.replay(full)
    twice = C.replay(full + carried)
    C.verdict('patch replay is idempotent',all(np.array_equal(x,y) for x,y in zip(once,twice)))
    print('\nASTRA RESULT: %d passed, %d failed' % (len(C.OK),len(C.FAIL)))
    report={'kind':'static','patch_sha256':hashlib.sha256((A.ROOT/'commands_astra/manifest.json').read_bytes()).hexdigest(),
            'results':[(n,True,'') for n in C.OK]+[(n,False,'') for n in C.FAIL]}
    out=A.ROOT/'docs/astra_tests'; out.mkdir(exist_ok=True)
    (out/'static.json').write_text(json.dumps(report,indent=1)+'\n')
    return good and not C.FAIL


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
