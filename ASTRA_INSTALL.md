# Astra refurbishment — Ashgrove Manor

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
   **`astra_10.txt`**. Paste one file at a time. Wait for its exact reply
   below, then wait another second before the next file. The first line only
   places the sky pad; `Block placed` is its successful reply.
5. The last reply is `[Astra] Astra Stage 10/10 complete. Astra refurbishment complete.`
   After it, wait two seconds. The pad and command machinery should be gone.

You do **not** rerun the base installer to apply this patch. If the base mansion is
already built, start with `astra_01.txt`. There are **10 additional console pastes**.

| File (in `commands_astra/`) | Characters | Expected reply |
|---|---:|---|
| `astra_01.txt` | 29 | `Block placed` |
| `astra_02.txt` | 14828 | `[Astra] Astra Stage 2/10 complete. Next: paste astra_03.txt` |
| `astra_03.txt` | 14886 | `[Astra] Astra Stage 3/10 complete. Next: paste astra_04.txt` |
| `astra_04.txt` | 14813 | `[Astra] Astra Stage 4/10 complete. Next: paste astra_05.txt` |
| `astra_05.txt` | 14835 | `[Astra] Astra Stage 5/10 complete. Next: paste astra_06.txt` |
| `astra_06.txt` | 14888 | `[Astra] Astra Stage 6/10 complete. Next: paste astra_07.txt` |
| `astra_07.txt` | 14904 | `[Astra] Astra Stage 7/10 complete. Next: paste astra_08.txt` |
| `astra_08.txt` | 14897 | `[Astra] Astra Stage 8/10 complete. Next: paste astra_09.txt` |
| `astra_09.txt` | 14818 | `[Astra] Astra Stage 9/10 complete. Next: paste astra_10.txt` |
| `astra_10.txt` | 14344 | `[Astra] Astra Stage 10/10 complete. Astra refurbishment complete.` |

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
is 14904 characters. The host panel still has to accept it;
this workflow is not compatible with a short RCON input limit.

To stop/clear a stuck installer, paste these **five separate console commands**,
one at a time. They target the installer area, not the mansion:

```text
kill @e[type=MinecartCommandBlock,x=-221,y=127,z=267,r=6]
kill @e[type=FallingSand,x=-221,y=127,z=267,r=6]
fill -221 124 267 -219 127 267 air
gamerule commandBlockOutput true
gamerule logAdminCommands true
```

Cleanup cannot undo a completed stage or interrupt a command already executing
in the current tick. To resume after cleanup, paste `astra_01.txt` to restore
the pad, then repeat the failed Astra stage and continue forward. Repeating
an Astra stage is safe: it only replaces matching original decorative blocks.
Do not rerun base stages as a patch recovery method. To undo the refurbishment,
restore the backup. On completion/cleanup, `commandBlockOutput` and
`logAdminCommands` are set to `true`, matching the base install's documented state.

## Validation

- `mc180_flat.json`: 22/22 passed.
- `mc189_flat.json`: 45/45 passed.
- `mc189_terrain.json`: 19/19 passed.
- `static.json`: 34/34 passed.

The test scripts use local disposable worlds, not your Eaglerhost world. Vanilla
results do not establish compatibility with Eaglerhost's panel or a modified
Spigot/Paper/Eagler server. See `docs/ASTRA_DESIGN.md` for the visual critique,
scope, reproducible checks and limitations. Previews show the generated block
model, not shader screenshots.
