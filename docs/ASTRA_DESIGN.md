# Astra refurbishment: design and engineering notes

## Visual critique and direction

The base is already a coherent, furnished Victorian house: asymmetric towers,
cross gables, a glazed cupola, chimney stacks, two-storey foyer and library, and
working survival rooms. Replacing these would lose valuable design and testing.
Its weaker features are long uninterrupted roof edges, visually heavy gray
towers, repetitive wall bays, brightly colored rectangular flower carpets,
and garden destinations that are not connected by a continuous designed walk.
Some secondary rooms and corridors have large plain ceiling or floor surfaces.

The owner's reference calls for warm pale wall panels against dark timber,
strong stone roof outlines, planting close to the building, and connected formal
gardens. It is a style reference, not an exact blueprint. This pass retains the
base's taller proportions and all room volumes. Shader light, terrain, distant
trees and modern lanterns in the reference are not part of this 1.8 patch.

## Refurbishment plan implemented

| Area | Treatment | Reason |
|---|---|---|
| Roof | Stone stair bargeboards on front/rear gables and side dormers; restrained iron cresting | Makes roof intersections and ridges read as finished architecture |
| Towers and pavilion | Warm sandstone infill with existing stone bands, glass and quoins | Lightens the stone mass without changing its silhouette or openings |
| Upper facade | Selected planted sills and timber rear-gable details | Adds depth and breaks repetition without decorating every bay identically |
| Entrance | Quartz corbels, porch light covers, foyer threshold and landing accents | Strengthens the arrival sequence and preserves the wide stair routes |
| Forecourt | Stone walks around the existing fountain and front beds | Connects gate, fountain and front steps into one composition |
| Side/rear grounds | Side walks, rear links, clipped borders, white/pink/red planting, capped lamps, dark gazebo roof | Makes the estate continuous and uses a consistent palette |
| Living spaces | Room-specific timber borders, inset corners, ceiling coffers and sparse rug motifs | Adds craft while retaining furniture, negative space and room identities |
| Hallways | Repeated but spaced runner accents and landing details | Makes transitions intentional without narrowing circulation |
| Basement | Stone aisle/border treatments in archive, crypt, storage and workshop | Gives the survival work areas clearer visual organization |

The secret study, vault, wine mechanism, tunnel, well shaft, wardrobe route,
attic access, redstone lab and hidden roof room are deliberately preserved.
Their existing atmosphere and presentation matter more than indiscriminate
decoration. The cistern, kitchens, baths, utility blocks, all beds, and hanging
art retain their working fixtures. Not every room receives new furniture.

## Implementation

`tools/astra_design.py` assembles the existing base, applies a separate decorative
layer to its voxel model, and emits only the new layer's conditional fills.
Adjacent writes with identical material preconditions are coalesced. No base
design module, engine, transformation, packer, console file or legacy file is
changed. No base inventory NBT or entity summon is replayed by the patch.

`tools/astra_build.py` reuses the base's proven falling-block / minecart installer
geometry and six-cart riding groups. It supplies Astra messages and a narrower
cleanup: only installer-area dropped items are removed, not items across the
occupied estate. Files live in `commands_astra/`, after all 24 base stages.
The patch uses only old-material-filtered 1.8 `/fill` commands, with absolute
world coordinates and rotated metadata. Repeating a patch stage is idempotent.

The preserved placement is entrance lawn `-251 73 267`, door blocks
`-251 76 266/267`, east-facing front, with the house extending west. Neither
the permanent write bounds nor temporary installer location moves.

## Reproduce and validate

Run from `tools/` with the repository's dependencies installed:

```bash
python3 console_check.py
python3 astra_test.py /path/to/mc189 flat --profile
python3 astra_export.py
python3 astra_check.py
python3 astra_test.py /path/to/mc189 flat
python3 astra_test.py /path/to/mc180 flat
python3 astra_test.py /path/to/mc189 terrain --no-functional
python3 astra_export.py --no-images
python3 console_check.py
```

The Astra-specific profiler follows `console_profile.py`'s method: measure each
new command on a real server after installing the frozen base, subtract median
sync overhead, then pack with measured cost and character limits. It writes
`astra_costs.json`, preserving `console_costs.json` so the frozen 24 base stages
remain reproducible. Unlike the base's sparse cost map, **every** Astra command
must have a measurement; export refuses unknown commands. Costs are machine
dependent, not a guarantee of timing on the owner's host.

The static check runs the existing absolute-command replay, rotation, support,
fire, walkability and interior-light checks on the composite model. It also
checks preservation of tile/entity data and mechanism metadata, no new solid
interior obstructions, patch hashes, packing limits, command coverage and
idempotent replay. The independent world interpreter reads command text rather
than trusting the design calls.

The real-server harness installs the shipped base then the shipped Astra files,
waits for their documented replies, repeats a patch stage in a recovery drill,
and reads the saved world back for block-by-block comparison and design checks.
The existing protocol-47 bot exercises secrets and interactive blocks. The
terrain test checks the natural-world installation and world diff; interactive
tests are performed on the two flat-world versions. These are disposable local
server worlds, never the owner's hosted world.

Reports are in `docs/astra_tests/`; the generated install guide lists their
pass counts and rejects stale evidence by marking reports whose patch manifest
hash differs. `docs/astra_changes.json` records edit counts by design section.

## Visual review and limits

`astra_se.png` shows the east/front and south side of the final block model;
`astra_nw.png` shows the rear/north elevations. The elevation images expose
roof outlines and facade relationships. These are schematic voxel renders,
not in-game screenshots and not evidence of shader lighting or exact texture
appearance. Static lighting covers spawnable **interior** locations; it is not
a claim that every outdoor lawn/roof block is spawn-proof at night.

The host dashboard still needs to accept a complete long console line. Vanilla
test evidence does not certify Eaglerhost input length or modified-server
behavior. Keep a world backup, install onto the matching base, and consult
`ASTRA_INSTALL.md` for exact sequence, recovery and cleanup.
