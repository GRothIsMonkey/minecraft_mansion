# AGENTS.md: handoff notes for the next agent

Read this first. It records what exists, how to rebuild and test it, and the rules that keep it working.
Everything below was true at the handoff commit.

## What this repo is

**Ashgrove Manor** is a large, furnished Victorian mansion for **Minecraft Java Edition 1.8.0–1.8.9**,
built entirely with vanilla commands. It has no mods, datapacks, functions or structure blocks. A Python
generator in `tools/` produces the commands. There are two editions:

| Edition | Output | User guide | Status |
|---|---|---|---|
| **Server-console edition (current)** | `commands_console/console_01.txt` … `console_24.txt` | `CONSOLE_INSTALL.md` | Tested; this is what the owner uses |
| Command-block edition (legacy fallback) | `commands/command_01.txt` … `command_09.txt` | `MANSION.md` | Frozen; must stay byte-identical |

The owner runs their **own 1.8 server** and installs from the **hosting dashboard's server console**. They
cannot comfortably paste huge text into an in-game command block. Their requirements, all met:

* Front entrance centred at **`-251 73 267`** (door blocks `-251 76 266/267`; the lawn is grass at Y 72 so
  feet are at Y 73; the doors sit 3 steps up at feet Y 76).
* The mansion **faces EAST**. Walking out of the front doors is +X. The house extends west (-X).
* Console lines are pasted **without a leading `/`**. Every build coordinate is absolute; nothing uses
  `~` relative to the console.
* Temporary installer machinery removes itself. Progress messages read
  `[Installer] Mansion Console Stage k/24 complete ...`.

## Setup

```bash
pip install -r requirements.txt          # numpy, scipy, pillow (Python 3.9+)
tools/setup_servers.sh ~/mcservers       # vanilla 1.8.9 + 1.8.0 server.jar (sha1-checked) for the tests
java -version                            # the real-server tests need Java (tested with OpenJDK 21)
```

The server jars are **not** in the repo. The tests write `eula=true` and their own `server.properties`
into the server folder.

## Everyday commands (run from `tools/`)

| Command | What it does | Time |
|---|---|---|
| `python3 check.py` | Design checks on the untransformed model: supports, fire, walkability, lighting | ~35 s |
| `python3 console_check.py` | Console edition, static: replays the exact command text, then runs the design checks on the turned model plus placement/orientation/installer checks. **Must print `24 passed, 0 failed`** | ~40 s |
| `python3 console_export.py` | Regenerates `commands_console/`, `docs/console_*.png` and `CONSOLE_INSTALL.md` | ~40 s |
| `python3 console_test.py ~/mcservers/mc189 flat` | **Real server**: pastes every console file into the console, diffs the world, runs the validators on the world as built, runs a recovery drill, and a bot clicks every mechanism | ~15 min |
| `python3 console_test.py ~/mcservers/mc189 terrain --no-functional` | Same on generated hilly terrain (seed 20150101; override with `MC_SEED`) | ~5 min |
| `MC_PORT=25600 python3 console_profile.py <server-dir>` | Re-measures the server cost of every command → `console_costs.json` | ~10 min |
| `python3 export.py` | Legacy edition: regenerates `commands/`, `MANSION.md`, legacy docs. **Do not run unless you intend to change the legacy edition** | ~40 s |
| `python3 final_test.py <server-dir>` | Legacy edition real-server test | ~3 min |

* `MC_PORT` (default 25599) lets two test servers run at once. Use a **separate server folder** for each.
  Keep runs whose timings you will report sequential.
* `console_test.py` writes its report to `out/console_test_<folder>_<kind>.json` (`out/` is gitignored).
  To publish results, copy the reports to `docs/console_tests/mc189_flat.json`, `mc180_flat.json` and
  `mc189_terrain.json`, then re-run `console_export.py`; the "How this was tested" section of
  `CONSOLE_INSTALL.md` is generated from those files.
* Expected results at handoff: 1.8.9 flat **44/44**, 1.8.0 flat **44/44**, 1.8.9 terrain **18/18**.

## Architecture

```
design modules (local coords, front = north)          exterior.py facades.py roofs.py interior_f1/f2/f3.py
        │                                              basement.py landscape.py furniture.py mansion_base.py
        ▼
engine.Build  ── keeps a voxel model in LOCAL coords (all design code and validators read it)
        │        and emits command text:
        ├─ Build.xf = None      → legacy text: "~dx ~dy ~dz" relative to a minecart   (packer.py → commands/)
        └─ Build.xf = rotation  → console text: ABSOLUTE world coords, turned metadata (console_build.py)
```

* `rotation.py`: the quarter turn (clockwise, north → east) and placement:
  `world = (KX - lz, KY + ly, KZ + lx)` with `KX=-225, KY=73, KZ=224`, derived from `ENTRANCE`. It has a
  metadata table for every directional block (stairs, doors, trapdoors, torches, levers, buttons,
  ladders/signs/chests/furnaces, pistons, repeaters, beds, logs, skull `Rot`, and so on). It also has
  `rotated_frame(b)`, which turns the whole voxel model so `validate.py` can run on it unchanged
  (world = rotated-local + `OFF`).
* `console_build.py`: the installer. `console_01` places a bedrock **pad** in the sky at `-221 124 267`.
  Every later line is **one** `summon FallingSand ...` above the pad. It drops a command block, a
  redstone block and an activator rail, and the command block summons a pile of command-block
  minecarts (groups of 6, the proven 1.8.0-safe method), each running one absolute build command. At the
  end of a stage, three command blocks fire one tick later in vanilla's fixed neighbour order
  (east, down, up): logging back on, `say` the stage message, then remove the column (the last stage also
  removes the pad). Stages are split by **16,000 characters** (`LIMIT`), by **4 s of measured server
  work** (`COST_CAP`, using `console_costs.json`), and the site clearing gets a stage of its own.
* `console_check.py`: static validation of the console edition. `console_test.py`, `mcbot.py`,
  `mcserver.py` and `mcworld.py` are the real-server harness: `mcbot.py` is a headless protocol-47
  (1.8) client that keeps chunks loaded and right-clicks blocks, and `mcworld.py` reads region files.
* `validate.py`: support / fire / walker / lighting / auto-lighting logic shared by both editions.

## Rules: do not break these

1. **The legacy edition stays byte-identical.** Engine changes must keep the `Build.xf is None` path
   unchanged. Check it with:
   ```bash
   cd tools && python3 -c "import build,packer,realtest,glob; b=build.assemble(); p=packer.pack([c.text for c in b.cmds],realtest.message); print(all(open(f).read()==x for f,(x,_) in zip(sorted(glob.glob('../commands/command_*.txt')),p)))"
   ```
2. **The shipped console files are the tested ones.** `commands_console/manifest.json` holds the SHA-1
   of each file. If any file changes, re-run the real-server tests (1.8.9 flat, 1.8.0 flat, 1.8.9 terrain),
   update `docs/console_tests/` and regenerate the guide before telling the owner it works.
3. **After any design change, re-measure costs** (`console_profile.py`). Costs are keyed by a hash of
   the command text; unknown commands count as 0 s, so stale costs quietly allow heavy stages again.
4. **Strictly 1.8 syntax**: no block states, no `Passengers`, no `/execute ... run`, no 1.9+ blocks or
   entities. Every build coordinate is absolute; `~` appears only inside the installer, relative to its
   own minecarts. Console lines contain printable ASCII only and have no leading `/`.
5. **Always regenerate; never hand-edit** `commands_console/*.txt`, `CONSOLE_INSTALL.md` or `MANSION.md`.
6. The install guide must stay accurate for a non-technical owner: exact replies, where to stand
   (`-225 73 267`), and the area changed (**X -309..-227, Y 62..118, Z 226..308**). The first section is
   the backup warning.

## Moving or re-orienting the mansion

* **New location:** change `ENTRANCE` in `rotation.py`. The pad and stand point in `console_build.py`
  follow it. **Also update** the hard-coded coordinates in the guide text and checks:
  `console_export.py` (entrance/door coordinates, the ASCII orientation diagram, the plan-level Y ranges
  and the "Y 69/72/73/76/84/91…" prose) and `console_check.py` (the `-251`, `266/267`, `76` and `267.0`
  assertions). In `console_test.py`, the flat test world has grass at Y 72 (`FLAT72`), matching
  `ENTRANCE` Y 73.
* **Different facing:** `rotation.py` only implements this one clockwise quarter turn (`CW`, the
  metadata tables, `point()` and `rotate_arrays()`). Another orientation needs new tables. Validate them
  the way `console_check.py` section 4 does, by comparing against the engine's direction helpers.

## Gotchas already solved (do not reintroduce)

* **Paintings:** compute the summon point in world space (`engine.painting` with `xf`). Rotating the local
  target point puts them one block off, and they drop as items.
* **Summon coordinates:** absolute x/z in `/summon` need a `.` (`_absf`). 1.8 adds 0.5 to a bare integer.
* **`/clone`:** the destination is the MIN corner of the turned target box.
* **Console noise:** killing the minecarts while `logAdminCommands` is on prints one line per cart.
  Turn logging off first; the restore happens in a command block after the carts are gone.
* **Ender chests** open as window type `minecraft:container`, not `minecraft:chest`.
* **Java 21 + 1.8 server:** a client connection needs `use-native-transport=false` (set by the tests).
* **The bot** must wait for Join Game before sending play packets, and pack block positions as unsigned
  64-bit values.
* **Expected game-made differences** (the diff allows for them): grass under opaque blocks turns to
  dirt, leaf check-decay bits change, redstone power levels are set by the game, flowing water from
  the fountain, and the attic armor stand settles 0.5 onto its slab floor.

## Known limitations / possible next steps

* The owner's **hosting dashboard console** was not tested with ~16,000-character lines. A panel that
  shortens input makes the server answer `Data tag parsing failed` and nothing is built (verified). If
  the owner reports that, lower `LIMIT` in `console_build.py`, re-export and re-test; the number of lines
  grows roughly in proportion. RCON-based consoles (~1,400 characters) cannot be supported this way.
* **Spigot/Paper 1.8** were not tested (the pad is kept within 4 blocks of the stand point for Spigot's
  entity activation range).
* 1.8 has no `/forceload`, so a player must stand at `-225 73 267` with server `view-distance` ≥ 6
  during the install.
