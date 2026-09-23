"""Regenerate only Astra deliverables. No base artifacts are written."""
import hashlib
import json
import sys
from collections import Counter

import astra_build as A
import astra_design as D
import console_build as CB
import rotation as R


def images(b):
    import render
    from engine import SX0,SY0,SZ0
    F=R.rotated_frame(b)
    def idx(x,y,z):
        return tuple(v-o for v,o in zip(R.world_to_r(x,y,z),(SX0,SY0,SZ0)))
    x0,y0,z0=idx(-311,71,224)
    x1,y1,z1=idx(-220,121,310)
    ids=F.ids[x0:x1+1,y0:y1+1,z0:z1+1]
    meta=F.meta[x0:x1+1,y0:y1+1,z0:z1+1]
    for view in ('SE','NW'):
        render.iso(ids,meta,str(A.ROOT/('docs/astra_'+view.lower()+'.png')),scale=6,view=view)
    for side in ('E','W'):
        render.elevation(ids,meta,str(A.ROOT/('docs/astra_elevation_'+side.lower()+'.png')),side=side,scale=8)


def export():
    base,b=D.assemble()
    paths=A.pack(b)
    out=A.ROOT/'commands_astra'; out.mkdir(exist_ok=True)
    for f in out.glob('astra_*.txt'): f.unlink()
    total=len(paths)
    rows=[]
    for k,(t,cmds,work) in enumerate(paths,1):
        name='astra_%02d.txt'%k
        (out/name).write_text(t+'\n')
        rows.append({'file':name,'chars':len(t),'sha256':hashlib.sha256((t+'\n').encode()).hexdigest(),
                     'expect':'Block placed' if k==1 else '[Astra] '+A.message(k,total),
                     'commands':len(cmds),'measured_seconds':round(work,4)})
    manifest={'base_commit':'082e475081c6f5137e908f38d4b526e572148454','entrance':CB.ENTRANCE,
              'build_box':CB.BUILD_BOX,'pad':CB.PAD,'stand':CB.STAND,'stages':rows}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=1)+'\n')
    table='\n'.join('| `%s` | %d | `%s` |'%(r['file'],r['chars'],r['expect']) for r in rows)
    cleanup='\n'.join(A.cleanup_commands())
    reports=[]
    for p in sorted((A.ROOT/'docs/astra_tests').glob('*.json')):
        report=json.loads(p.read_text())
        current=report.get('patch_sha256')==hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest()
        results=report['results']; passed=sum(bool(r[1]) for r in results)
        reports.append('- `%s`: %d/%d passed%s.'%(p.name,passed,len(results),'' if current else ' (STALE: different patch manifest)'))
    tests='\n'.join(reports) or 'Real-server verification has not yet been recorded for this patch.'
    guide=f'''# Astra refurbishment — Ashgrove Manor

## Back up the world first

Use your host's existing-world backup/download option before changing the mansion.
This edits the existing world; it does **not** require buying or creating another world.
The patch changes decorative surfaces, roof trim and grounds inside the original estate:
**X -309..-227, Y 62..118, Z 226..308**. The temporary installer occupies
**X -221..-219, Y 124..127, Z 267**. Keep that sky space clear.
Use this on the matching base mansion before extensive personal remodeling. Filtered
fills protect other block types, but cannot distinguish your own stone/wood decoration
from matching original surfaces. Existing chests and their contents are never rewritten.

## Install after the base

1. Finish `commands_console/console_01.txt` through `console_24.txt` and wait for
   `[Installer] Mansion Console Stage 24/24 complete. Mansion construction complete.`
2. Keep one player in the **Overworld at `-225 73 267`** throughout the patch.
   If needed, type `tp YOUR_PLAYER_NAME -225 73 267` in the server console.
   The server needs `enable-command-block=true` and `view-distance=6` or higher,
   just as for the base. Java 1.8.0–1.8.9 only.
3. Open each Astra file's **Raw** contents. Copy the **whole single line** into
   your hosting dashboard's **server console**, with **no leading `/`**.
4. Paste `astra_01.txt`, then `astra_02.txt`, continuing in numbered order through
   **`astra_{total:02d}.txt`**. Paste one file at a time. Wait for its exact reply
   below, then wait another second before the next file. The first line only
   places the sky pad; `Block placed` is its successful reply.
5. The last reply is `[Astra] {A.message(total,total)}`
   After it, wait two seconds. The pad and command machinery should be gone.

You do **not** rerun the base installer to apply this patch. If the base mansion is
already built, start with `astra_01.txt`. There are **{total} additional console pastes**.

| File (in `commands_astra/`) | Characters | Expected reply |
|---|---:|---|
{table}

## Check the result

The front doors remain at `-251 76 266` and `-251 76 267`; the lawn entrance
remains `-251 73 267`. Walk out toward **east (+X)**; the house extends **west**.
Look for pale tower panels, stone-outlined gables, iron ridge cresting, clipped
window planters, stone garden walks and the dark-roof gazebo. Inside, look for
ceiling coffers, wood borders, woven rug details and clearer basement workshop aisles.

Paste `testforblock -221 124 267 air` in the console. It should report
`Successfully found the block at -221,124,267.` The base guide's door checks
still apply. A completion message confirms the stage ran; it does not detect
previous personal remodeling that caused conditional fills to skip surfaces.

## Practical survival areas

The existing 49 chests, 23 furnaces and 20 beds remain in their original places.
The basement furnace room has its 20-furnace bank, workbenches and anvil; its
stone floor now marks the work aisle. The kitchen keeps its ovens, crafting
island and food chest. The two-storey library keeps its enchanting table.
Brewing stations, valuables storage and every secret route remain intact.
See the base floor plans and room guide for their locations; this patch does
not add a new room layout or reveal secrets with new signs.

## If a stage does not finish

Stop pasting. Keep the player at the stand point and allow up to two minutes
for the server to finish. If the console reports `Data tag parsing failed`,
the host may have shortened the line: do not continue or split a summon line.
Report which file failed and the exact console reply. The longest Astra line
is {max(r['chars'] for r in rows)} characters. The host panel still has to accept it;
this workflow is not compatible with a short RCON input limit.

To stop/clear a stuck installer, paste these **five separate console commands**,
one at a time. They target the installer area, not the mansion:

```text
{cleanup}
```

Cleanup cannot undo a completed stage or interrupt a command already executing
in the current tick. To resume after cleanup, paste `astra_01.txt` to restore
the pad, then repeat the failed Astra stage and continue forward. Repeating
an Astra stage is safe: it only replaces matching original decorative blocks.
Do not rerun base stages as a patch recovery method. To undo the refurbishment,
restore the backup. On completion/cleanup, `commandBlockOutput` and
`logAdminCommands` are set to `true`, matching the base install's documented state.

## Validation

{tests}

The test scripts use local disposable worlds, not your Eaglerhost world. Vanilla
results do not establish compatibility with Eaglerhost's panel or a modified
Spigot/Paper/Eagler server. See `docs/ASTRA_DESIGN.md` for the visual critique,
scope, reproducible checks and limitations. Previews show the generated block
model, not shader screenshots.
'''
    (A.ROOT/'ASTRA_INSTALL.md').write_text(guide)
    (A.ROOT/'docs/astra_changes.json').write_text(json.dumps(dict(Counter(e[-1] for e in b.astra_edits)),indent=1)+'\n')
    if '--no-images' not in sys.argv: images(b)
    print('Exported %d Astra stages; longest %d characters'%(total,max(r['chars'] for r in rows)))


if __name__=='__main__': export()
