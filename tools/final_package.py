"""Generate the final EaglerHost installation guide and execution manifest."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
REQUESTED_COMMIT = "48c3462f04651a84a4cc94d64dab97ae7dc4da1e"


def rows(folder, manifest_name, algo):
    source = json.loads((ROOT / folder / manifest_name).read_text())
    out = []
    for order, stage in enumerate(source["stages"], 1):
        path = ROOT / folder / stage["file"]
        data = path.read_bytes()
        text = data.decode("ascii").rstrip("\n")
        digest = hashlib.new(algo, data).hexdigest()
        out.append({
            "order": order,
            "edition": "Claude base" if folder == "commands_console" else "Astra patch",
            "file": f"{folder}/{stage['file']}",
            "chars": len(text),
            "bytes": len(data),
            "hash": digest,
            "hash_algorithm": algo,
            "completion": stage["expect"],
        })
    return out


def table(items):
    lines = ["| Order | File | Characters | Exact completion message |", "|---:|---|---:|---|"]
    for item in items:
        lines.append(f"| {item['order']} | `{item['file']}` | {item['chars']} | `{item['completion']}` |")
    return "\n".join(lines)


def main():
    base = rows("commands_console", "manifest.json", "sha1")
    astra = rows("commands_astra", "manifest.json", "sha256")
    all_rows = []
    for item in base + astra:
        item = dict(item)
        item["execution_order"] = len(all_rows) + 1
        all_rows.append(item)

    spatial = [
        {"stage": 1, "scope": "installer pad only", "chunk_x": [-14, -14], "chunk_z": [16, 16], "radius_from_stand": 1},
        {"stage": 2, "bbox": [-292, 76, 235, -250, 118, 298], "chunk_x": [-19, -16], "chunk_z": [14, 18], "radius_from_stand": 4},
        {"stage": 3, "bbox": [-257, 76, 235, -250, 93, 298], "chunk_x": [-17, -16], "chunk_z": [14, 18], "radius_from_stand": 2},
        {"stage": 4, "bbox": [-291, 76, 235, -249, 103, 298], "chunk_x": [-19, -16], "chunk_z": [14, 18], "radius_from_stand": 4},
        {"stage": 5, "bbox": [-308, 72, 232, -227, 103, 301], "chunk_x": [-20, -15], "chunk_z": [14, 18], "radius_from_stand": 5},
        {"stage": 6, "bbox": [-307, 73, 231, -228, 82, 302], "chunk_x": [-20, -15], "chunk_z": [14, 18], "radius_from_stand": 5},
        {"stage": 7, "bbox": [-293, 75, 236, -251, 89, 297], "chunk_x": [-19, -16], "chunk_z": [14, 18], "radius_from_stand": 4},
        {"stage": 8, "bbox": [-290, 83, 254, -251, 96, 297], "chunk_x": [-19, -16], "chunk_z": [15, 18], "radius_from_stand": 4},
        {"stage": 9, "bbox": [-286, 90, 237, -252, 96, 296], "chunk_x": [-18, -16], "chunk_z": [14, 18], "radius_from_stand": 3},
        {"stage": 10, "bbox": [-290, 68, 237, -252, 103, 296], "chunk_x": [-19, -16], "chunk_z": [14, 18], "radius_from_stand": 4},
    ]
    final_manifest = {
        "project": "GRothIsMonkey/minecraft_mansion",
        "branch": "astra/refurbishment",
        "requested_commit_included": REQUESTED_COMMIT,
        "execution": {"base_stages": 24, "astra_stages": 10, "total_stages": 34},
        "character_count_definition": "ASCII characters excluding the single trailing newline; bytes includes it",
        "stages": all_rows,
        "coordinates": {
            "entrance": [-251, 73, 267],
            "front_door_blocks": [[-251, 76, 266], [-251, 76, 267]],
            "stand": [-225, 73, 267],
            "stand_chunk": [-15, 16],
            "installer_pad": [-221, 124, 267],
            "build_box_inclusive": [-309, 62, 226, -227, 118, 308],
        },
        "compatibility_audit": {
            "server_view_distance_required": 6,
            "maximum_stage_chunk_radius_from_stand": 5,
            "one_chunk_safety_margin": True,
            "spatial_split_required": False,
            "reason": "Every stage remains within the six-chunk server-side loading envelope around the player stand; no distant unloaded chunk is required.",
            "astra_stage_scopes": spatial,
        },
        "validation_reports": [
            "out/final_pre_console_check.log",
            "out/astra_mc180_flat.log",
            "out/astra_mc189_flat.log",
            "out/astra_mc189_terrain.log",
            "out/astra_check_final2.log",
        ],
    }
    (ROOT / "FINAL_MANIFEST.json").write_text(json.dumps(final_manifest, indent=2) + "\n")

    guide = f"""# Ashgrove Manor — final EaglerHost Java 1.8 installation

This is the single end-to-end procedure for the completed `astra/refurbishment`
branch. It installs Claude's tested base first, then Astra's additive refurbishment.
The exact requested commit `{REQUESTED_COMMIT}` is included in this branch; the
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

{table(base)}

Stage 2 levels and clears the build box; never restart the base sequence after
later stages have run. Heavy stages may pause the server briefly. Always wait for
the completion line, not a fixed number of seconds.

## 4. Astra refurbishment — `astra_01.txt` through `astra_10.txt`

Start only after the Claude completion line from stage 24. Keep the same player at
the same stand. Astra is an additive, filtered-fill patch; it does not rewrite
inventories or entity NBT.

{table(astra)}

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
"""
    (ROOT / "FINAL_INSTALL.md").write_text(guide)


if __name__ == "__main__":
    main()
