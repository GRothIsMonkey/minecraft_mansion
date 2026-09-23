# Ashgrove Manor — final EaglerHost Java 1.8 installation

This is the single end-to-end procedure for the completed `astra/refurbishment`
branch. It installs Claude's tested base first, then Astra's additive refurbishment.
The exact requested commit `48c3462f04651a84a4cc94d64dab97ae7dc4da1e` is included in this branch; the
final packaging commit adds only this guide, the manifest, and its generator.

## 1. Server settings and preflight

1. Back up or download the world. The base stage 2 clears the inclusive box
   **X -309..-227, Y 62..118, Z 226..308**; do not place anything you need inside it.
2. In EaglerHost's web dashboard, set `enable-command-block=true` and
   `view-distance=6` or higher in `server.properties`, then restart the server.
   A client render distance does not replace the server setting.
3. Make sure the sky is clear around **X -221..-219, Y 124..127, Z 267**.
4. Join the Overworld and stand at **X -225, Y 73, Z 267**. Stay there for all
   34 stages; this keeps the relevant chunks loaded. Face west toward the house.
5. Open the EaglerHost **web dashboard Console**. Paste each complete file as one
   line, with no leading `/`, and press Enter. Paste the next file only after the
   exact completion message below appears. Do not paste two stages together.

## 2. Exact coordinates and orientation

- Front entrance center: **-251 73 267**; door blocks: **-251 76 266** and
  **-251 76 267**.
- Entrance faces **EAST**: exiting moves +X; entering moves -X. The mansion is
  primarily west of the doors.
- Player stand: **-225 73 267** (chunk **-15, 16**).
- Temporary installer pad: **-221 124 267**. It is removed by the final stage.

## 3. Claude base — `console_01.txt` through `console_24.txt`

Run these files in exact order. The character count excludes the final newline.

| Order | File | Characters | Exact completion message |
|---:|---|---:|---|
| 1 | `commands_console/console_01.txt` | 29 | `Block placed` |
| 2 | `commands_console/console_02.txt` | 2634 | `[Installer] Mansion Console Stage 2/24 complete. Next: paste console_03.txt` |
| 3 | `commands_console/console_03.txt` | 1902 | `[Installer] Mansion Console Stage 3/24 complete. Next: paste console_04.txt` |
| 4 | `commands_console/console_04.txt` | 2384 | `[Installer] Mansion Console Stage 4/24 complete. Next: paste console_05.txt` |
| 5 | `commands_console/console_05.txt` | 15869 | `[Installer] Mansion Console Stage 5/24 complete. Next: paste console_06.txt` |
| 6 | `commands_console/console_06.txt` | 15915 | `[Installer] Mansion Console Stage 6/24 complete. Next: paste console_07.txt` |
| 7 | `commands_console/console_07.txt` | 15855 | `[Installer] Mansion Console Stage 7/24 complete. Next: paste console_08.txt` |
| 8 | `commands_console/console_08.txt` | 15879 | `[Installer] Mansion Console Stage 8/24 complete. Next: paste console_09.txt` |
| 9 | `commands_console/console_09.txt` | 15848 | `[Installer] Mansion Console Stage 9/24 complete. Next: paste console_10.txt` |
| 10 | `commands_console/console_10.txt` | 15907 | `[Installer] Mansion Console Stage 10/24 complete. Next: paste console_11.txt` |
| 11 | `commands_console/console_11.txt` | 15861 | `[Installer] Mansion Console Stage 11/24 complete. Next: paste console_12.txt` |
| 12 | `commands_console/console_12.txt` | 15768 | `[Installer] Mansion Console Stage 12/24 complete. Next: paste console_13.txt` |
| 13 | `commands_console/console_13.txt` | 15719 | `[Installer] Mansion Console Stage 13/24 complete. Next: paste console_14.txt` |
| 14 | `commands_console/console_14.txt` | 15919 | `[Installer] Mansion Console Stage 14/24 complete. Next: paste console_15.txt` |
| 15 | `commands_console/console_15.txt` | 15872 | `[Installer] Mansion Console Stage 15/24 complete. Next: paste console_16.txt` |
| 16 | `commands_console/console_16.txt` | 15873 | `[Installer] Mansion Console Stage 16/24 complete. Next: paste console_17.txt` |
| 17 | `commands_console/console_17.txt` | 15882 | `[Installer] Mansion Console Stage 17/24 complete. Next: paste console_18.txt` |
| 18 | `commands_console/console_18.txt` | 15868 | `[Installer] Mansion Console Stage 18/24 complete. Next: paste console_19.txt` |
| 19 | `commands_console/console_19.txt` | 15835 | `[Installer] Mansion Console Stage 19/24 complete. Next: paste console_20.txt` |
| 20 | `commands_console/console_20.txt` | 15886 | `[Installer] Mansion Console Stage 20/24 complete. Next: paste console_21.txt` |
| 21 | `commands_console/console_21.txt` | 15899 | `[Installer] Mansion Console Stage 21/24 complete. Next: paste console_22.txt` |
| 22 | `commands_console/console_22.txt` | 15867 | `[Installer] Mansion Console Stage 22/24 complete. Next: paste console_23.txt` |
| 23 | `commands_console/console_23.txt` | 15866 | `[Installer] Mansion Console Stage 23/24 complete. Next: paste console_24.txt` |
| 24 | `commands_console/console_24.txt` | 7459 | `[Installer] Mansion Console Stage 24/24 complete. Mansion construction complete.` |

Stage 2 levels and clears the build box; never restart the base sequence after
later stages have run. Heavy stages may pause the server briefly. Always wait for
the completion line, not a fixed number of seconds.

## 4. Astra refurbishment — `astra_01.txt` through `astra_10.txt`

Start only after the Claude completion line from stage 24. Keep the same player at
the same stand. Astra is an additive, filtered-fill patch; it does not rewrite
inventories or entity NBT.

| Order | File | Characters | Exact completion message |
|---:|---|---:|---|
| 1 | `commands_astra/astra_01.txt` | 29 | `Block placed` |
| 2 | `commands_astra/astra_02.txt` | 14828 | `[Astra] Astra Stage 2/10 complete. Next: paste astra_03.txt` |
| 3 | `commands_astra/astra_03.txt` | 14886 | `[Astra] Astra Stage 3/10 complete. Next: paste astra_04.txt` |
| 4 | `commands_astra/astra_04.txt` | 14813 | `[Astra] Astra Stage 4/10 complete. Next: paste astra_05.txt` |
| 5 | `commands_astra/astra_05.txt` | 14835 | `[Astra] Astra Stage 5/10 complete. Next: paste astra_06.txt` |
| 6 | `commands_astra/astra_06.txt` | 14888 | `[Astra] Astra Stage 6/10 complete. Next: paste astra_07.txt` |
| 7 | `commands_astra/astra_07.txt` | 14904 | `[Astra] Astra Stage 7/10 complete. Next: paste astra_08.txt` |
| 8 | `commands_astra/astra_08.txt` | 14897 | `[Astra] Astra Stage 8/10 complete. Next: paste astra_09.txt` |
| 9 | `commands_astra/astra_09.txt` | 14818 | `[Astra] Astra Stage 9/10 complete. Next: paste astra_10.txt` |
| 10 | `commands_astra/astra_10.txt` | 14344 | `[Astra] Astra Stage 10/10 complete. Astra refurbishment complete.` |

The compatibility audit found Astra's largest spatial radius is 5 chunks from the
stand. With `view-distance=6`, every target chunk has a one-chunk safety margin;
there is no geographically distant stage and no extra spatial split is required.
Do not run the workflow with a lower server view distance.

## 5. Final verification checklist

After the Astra stage 10 message, wait two seconds, then confirm:

- [ ] `testforblock -221 124 267 air` reports the pad is gone.
- [ ] `testfor @e[type=MinecartCommandBlock]` and
      `testfor @e[type=FallingSand]` return no match.
- [ ] Both east-facing front doors exist at `-251 76 266` and `-251 76 267`;
      walking out goes +X.
- [ ] Walk from the lawn through the foyer, galleries, stairs, basement and
      upper floors and back out; navigation is continuous with no sealed route.
- [ ] Check the kitchen/workshop, storage, enchanting, brewing, beds, furnaces,
      crafting tables, anvil, chests and other inventories. Existing tile-entity
      contents must remain present.
- [ ] Operate the redstone doors, secret entrances, hatches, vault/tunnel and
      other secrets; confirm no mechanism is left powered or broken.
- [ ] Inspect landscaping, fountain/gardens, lighting, fire/lantern safety,
      roofs and decorative finish. Confirm no stray command blocks, redstone,
      minecarts, falling blocks or dropped items remain.
- [ ] Restore normal logging if necessary: `gamerule commandBlockOutput true`
      and `gamerule logAdminCommands true`.

The repository's final checks report: base console **24/24**, Astra static
**34/34**, Java 1.8.0 flat **22/22**, Java 1.8.9 flat **45/45**, and Java 1.8.9
terrain **19/19**. Those are disposable vanilla validation worlds; still perform
the checklist on your EaglerHost world.

## 6. Emergency stop and recovery

Stop pasting immediately if a stage does not finish or the panel reports an error.
Keep the player at the stand and allow up to two minutes for the current tick to
finish. Run these commands one at a time in the web console, without `/`:

```text
kill @e[type=MinecartCommandBlock,x=-224,y=122,z=264,dx=6,dy=100,dz=6]
kill @e[type=FallingSand,x=-224,y=122,z=264,dx=6,dy=100,dz=6]
fill -222 124 266 -218 128 268 air
gamerule commandBlockOutput true
gamerule logAdminCommands true
kill @e[type=Item,x=-309,y=62,z=226,dx=82,dy=56,dz=82]
```

The first two commands remove installer entities; the `fill` removes the pad and
column; the gamerules restore normal logging; the last command removes dropped
items in the site. After cleanup, paste `console_01.txt` to recreate the pad only
when resuming a sequence. For an interrupted Claude stage, repeat that same stage
after the pad is restored. For an interrupted Astra stage, restore the pad with
`astra_01.txt`, then repeat the failed Astra file. Repeating an Astra stage is
safe; never repeat base stage 2 after later base stages have completed. A completed
stage cannot be undone by cleanup—restore the world backup to revert the build or
the refurbishment.

If the panel says `Cannot place blocks outside of the world` or `Cannot summon the
object out of the world`, the stand/player chunk is not loaded: return to
**-225 73 267**, verify `view-distance=6+`, and retry the same file. If it says
`Data tag parsing failed` or `Unknown command`, the dashboard truncated or changed
the line; copy the whole file again. Do not split a line manually.

## 7. Final execution manifest

`FINAL_MANIFEST.json` is authoritative for all 34 files, exact execution order,
character counts, hashes, completion messages, coordinates and the unloaded-chunk
audit. It is generated by `tools/final_package.py`.
