# Ashgrove Manor — Spigot / Bukkit 1.8.8 plugin

**File to upload: [`AshgroveManor-1.0.0.jar`](AshgroveManor-1.0.0.jar)** (69,477 bytes, SHA-256
`9f8c96fcefc57b7c95f48a1bf40238f6db720538bf6c70f753b47ae7196534bf`). On GitHub, open the file and click
**Download raw file**.

This plugin builds the **finished Ashgrove Manor**: Claude's base mansion plus Astra's refurbishment,
from the final source commit `4be5b07f0e33010fcd4dee65cd13ffa6b6fb0320`. Nothing is redesigned or
simplified. It replaces the console installer, whose 15,000-character lines your EaglerHost console
cuts off at 256 characters. The longest thing you type now is `mansion confirm` (15 characters).

> ## BACK UP THE WORLD BEFORE BUILDING.
> The build clears and rebuilds this area of your **main world** (absolute coordinates, inclusive):
>
> | | from | to |
> |---|---|---|
> | X | -309 | -227 |
> | Y | 62 | 118 |
> | Z | 226 | 308 |
>
> Everything from Y 73 up to Y 118 in that square becomes air before the mansion goes up. Y 69–72 becomes
> dirt and the lawn. The basement, cellars, cistern and escape tunnel are dug below that, down to Y 62.
> Nothing outside this box is changed, except natural gravel in caves under the site, which may drop
> when the ground above it changes (vanilla behaviour).

## Where the mansion goes

* **Main entrance: `-251 73 267`**, the centre of the front double doors (door blocks `-251 76 266` and
  `-251 76 267`, three steps up from the lawn).
* **Faces EAST.** Walking out of the front doors goes +X; the house extends west (-X).
* The lawn is grass at Y 72, so you stand on it at Y 73.
* It is always built in the server's **main world** (the `level-name` world in `server.properties`).

## Requirements

* A **Spigot or Bukkit 1.8.8** server (CraftBukkit/Spigot `v1_8_R3`). Tested on Spigot 1.8.8 built by
  Spigot's BuildTools (`git-Spigot-3c60ece-741a1bd`).
* **Java 8 or newer.** Tested on Java 8 and Java 21.
* Operator rights, or the server console.
* **No other setting is needed.** You do *not* need `enable-command-block`, a particular
  `view-distance`, or a player standing anywhere. The plugin loads the site's chunks itself.

## Install and build

1. **Back up the world** (EaglerHost dashboard: backups / world download).
2. Upload `AshgroveManor-1.0.0.jar` into the server's **`plugins`** folder (EaglerHost dashboard: file
   manager, or its plugin upload page).
3. **Restart** the server. The console shows:
   ```
   [AshgroveManor] Ashgrove Manor ready: 4518 build commands (3356 base + 1162 Astra). Entrance -251 73 267, facing east.
   [AshgroveManor] Type 'mansion build' in the console to build the mansion.
   ```
4. In the console type **`mansion build`** (in game, as an operator: `/mansion build`). It repeats the
   backup warning and the area, then asks you to confirm.
5. Within 60 seconds type **`mansion confirm`**. The console shows progress:
   ```
   [AshgroveManor] Building started: 4518 commands. Players may notice short pauses while the big walls go up.
   [AshgroveManor] Building... 586/4518 commands (12%)
   ...
   [AshgroveManor] Mansion construction complete. Checking it block by block now...
   [AshgroveManor] OK: 348,046 of 348,046 built blocks match the design; paintings 16/16, item frame 1/1, armor stands 8/8
   ```
   On the test machine the build took about 10 seconds and the check about 1 second. Players online see
   the game pause for a moment while the biggest walls go up.
6. **Done.** The `OK:` line means every block of the finished design, all 16 paintings, the item frame
   and the 8 armor stands are in your world exactly as designed. Walk up the front steps and in through
   the doors at `-251 76 266/267`.

When it has finished you can keep the plugin (for `mansion verify`) or delete the JAR. The mansion is made
of normal blocks and stays either way.

## Commands

All of them work from the console (no `/`) or in game for operators (`/mansion ...`, alias `/ashgrove`).
Permission: `ashgrove.admin` (operators by default).

| Command | What it does |
|---|---|
| `mansion` | Help, and the entrance coordinates |
| `mansion build` | Shows the warning and the area, then asks for `mansion confirm` |
| `mansion confirm` | Starts the build (within 60 s of `mansion build`) |
| `mansion status` | Progress, and the result of the last check |
| `mansion pause` | Pauses the build |
| `mansion resume` | Builds again from the first command (see below) |
| `mansion verify` | Checks the mansion against the finished design, block by block, at any time |

## If something goes wrong

* **The server restarts or crashes during the build.** After the restart the console says
  `A mansion build was interrupted ... Type 'mansion resume' ...`. Type **`mansion resume`**. The build
  runs again from the first command. That takes seconds, and the result is exactly the design however
  far the first attempt got. (Every block the mansion writes is first set outright before anything
  reads it, so a full run always ends in the same state.) This was tested by killing the server at 42%.
* **`mansion verify` reports `DIFFERENCES FOUND`** and lists coordinates. This means something changed
  those blocks after the build, for example a player or another plugin. `mansion build` +
  `mansion confirm` rebuilds the whole mansion exactly. It also replaces anything built inside the area since.
* **`mansion` is "Unknown command"**: the JAR is not in `plugins/`, or the server was not restarted.
* **`The mansion data inside the JAR is damaged`** in the console: download the JAR again. The plugin checks
  the SHA-256 of its build data before it runs anything.

## What the plugin does, exactly

* It contains the exact list of **4,518 vanilla 1.8 build commands** that the tested console
  installation ran: Claude's 3,356 base commands followed by Astra's 1,162 refurbishment commands, in the
  same order, all with absolute coordinates. `tools/plugin_export.py` rebuilds the list from the design
  generator. Before writing it, it re-packs the list into the 34 console files and checks all 34 against
  the hashes in `FINAL_MANIFEST.json`.
* It runs them a few milliseconds per server tick (`tick-budget-ms: 30` in `plugins/AshgroveManor/config.yml`).
  Each command gets the `minecraft:` prefix, so another plugin's `/kill` or `/fill` cannot take it over.
  The commands run from a temporary command-block minecart named `AshgroveInstaller`, the same kind of
  command sender the tested console installer used. The plugin removes the minecart when it finishes.
* While it builds it keeps the site's chunks loaded itself. It sets `logAdminCommands` and
  `commandBlockOutput` to `false` so the console is not flooded, then puts them back to **your** previous
  values.
* Only the old installer machinery (falling command blocks, minecart piles, the sky pad) is left out.
  It never was part of the mansion. The base installer's removal of dropped items inside the site is
  kept, at the same point in the sequence.
* Afterwards it compares the world with the finished design over all **348,046** blocks the design writes.
  It allows only for things the game changes by itself: leaf decay bits, redstone power levels, fountain
  water and grass under walls turning to dirt. It also checks the paintings, the item frame and the armor
  stands. Blocks outside the design (your terrain) are not touched and not checked.

## How it was tested

Every test ran on a real Spigot 1.8.8 server built with BuildTools. **No player was online during the
build**, and world spawn was far away, so the plugin alone kept the site loaded. The console received exactly
`mansion build` and `mansion confirm`. After each build the saved world was checked by an independent
program (`tools/plugin_test.py`), not by the plugin itself:

* every block of the test area against the finished Claude + Astra design;
* the 16 paintings, the item frame and the 8 armor stands (position, facing, yaw);
* no installer blocks or entities left over;
* the design checks run on the blocks read back from the world: everything that hangs on something
  is supported, every room is reachable on foot from the lawn and back, no dark spots where mobs can
  spawn indoors, no fire hazards;
* in the flat run, a player then clicked every mechanism: the bookcase door, the wine-cellar barrel,
  the vault door (both levers), the lab lamps, the lab pressure plate, both hatches, the wardrobe door,
  102 doors, 338 trapdoors, 49 chests, 23 furnaces, 22 crafting tables, 35 brewing stands, 3 enchanting
  tables, 3 anvils, 20 beds, the beacon, the ender chest, the dispensers and the dropper.

| Test | Result | Build time | Report |
|---|---|---|---|
| Spigot 1.8.8, Java 8, flat world, with a player clicking every mechanism afterwards | **39/39 passed** | 8.0 s | [`spigot188_flat_java8.json`](docs/plugin_tests/spigot188_flat_java8.json) |
| Spigot 1.8.8, Java 8, generated hilly terrain (ground Y 70–92, trees, water, caves) | **13/13 passed** | 10.6 s | [`spigot188_terrain_java8.json`](docs/plugin_tests/spigot188_terrain_java8.json) |
| Spigot 1.8.8, Java 21, server killed (kill -9) at 42 %, restarted, `mansion resume` | **17/17 passed** | 6.9 s | [`spigot188_flat_crash_resume_java21.json`](docs/plugin_tests/spigot188_flat_crash_resume_java21.json) |
| Spigot 1.8.8, Java 8, `enable-command-block=false` | **16/16 passed** | 7.7 s | [`spigot188_flat_no_command_blocks_java8.json`](docs/plugin_tests/spigot188_flat_no_command_blocks_java8.json) |

**Same world as the tested console installation.** The same 34 console stages that Claude and Astra tested
were run on vanilla 1.8.9 to build a reference world, and the plugin's world was compared with it
([`plugin_vs_console_world.json`](docs/plugin_tests/plugin_vs_console_world.json)):
**1,238,593 blocks, 227 tile entities with all their data (chest contents, signs, the journal, skulls, banners,
flower pots, jukebox discs, furnaces, brewing stands, the lab command block) and 25 entities (paintings,
armor stands with their equipment, the item frame) are identical.** The only difference is 134 grass blocks
hidden under walls. The game turns those to dirt at random moments.


## Known limitations

* Tested on **Spigot 1.8.8** only. EaglerHost's exact server build could not be tested here. Any
  Bukkit/Spigot/Paper server for Minecraft **1.8.8** (`v1_8_R3`) runs vanilla commands the same way. The
  plugin does not work on other Minecraft versions.
* A plugin that blocks or rewrites vanilla commands (some anti-cheat or command-filter plugins) could stop
  the build. The final check then reports the blocks that are missing.
* The plugin always builds in the main world, at the coordinates above. Moving the mansion needs the
  generator (see `AGENTS.md`).
* The older installers are still in the repository (`commands_console/`, `commands_astra/`,
  `commands/`) and still produce the same mansion. With this plugin you do not need them.
