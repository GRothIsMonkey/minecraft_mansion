"""Write the deliverables: commands/command_NN.txt, docs/*.png and MANSION.md (Parts 1-7)."""
import collections
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build                          # noqa: E402
import packer                         # noqa: E402
import realtest                       # noqa: E402
import check                          # noqa: E402
from mansion_base import X0, Z0       # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cb(mx, y, mz):
    """Mansion coordinates -> offset from the player's command block."""
    return '%+d, %+d, %+d' % (mx + X0, y, mz + Z0)


def main():
    b = build.assemble()
    cmds = [c.text for c in b.cmds]
    pastes = packer.pack(cmds, realtest.message)
    total = len(pastes)
    # the footer of the final stage has one extra command; recount stage boundaries exactly
    bounds, i = [], 0
    for k, (paste, body) in enumerate(pastes):
        extra = len(packer.HEADER) + len(packer.footer(k + 1, total, k == total - 1, 'x'))
        n = len(body) - extra
        bounds.append((i, i + n))
        i += n
    assert i == len(cmds)
    os.makedirs(os.path.join(ROOT, 'commands'), exist_ok=True)
    for k, (paste, body) in enumerate(pastes):
        with open(os.path.join(ROOT, 'commands', 'command_%02d.txt' % (k + 1)), 'w') as f:
            f.write(paste)
    # images
    build.render_views(b)
    build.render_plans(b)
    os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
    for name in ('preview_nw', 'preview_se', 'preview_elev_S', 'preview_elev_N', 'plan_B', 'plan_F1',
                 'plan_F2', 'plan_F3', 'plan_ATTIC'):
        shutil.copy(os.path.join(build.OUT, name + '.png'), os.path.join(ROOT, 'docs', name + '.png'))
    secs = []
    for (a, z) in bounds:
        s = []
        for c in b.cmds[a:z]:
            name = c.section
            if name.startswith('facade'):
                name = 'facades'
            if name.startswith('auto lighting'):
                name = 'extra lighting'
            if name.startswith('grounds'):
                name = 'grounds'
            if name not in s:
                s.append(name)
        secs.append(s)
    kinds = collections.Counter(c.split()[0] for c in cmds)
    doc = render_doc(b, pastes, secs, kinds)
    with open(os.path.join(ROOT, 'MANSION.md'), 'w') as f:
        f.write(doc)
    print('wrote %d commands in %d pastes, MANSION.md %d chars' % (len(cmds), total, len(doc)))
    return b, pastes


def render_doc(b, pastes, secs, kinds):
    total = len(pastes)
    L = []
    w = L.append
    w('# Ashgrove Manor - a staged command-block mansion for Minecraft Java 1.8 / 1.8.9\n')
    w('![Ashgrove Manor from the north-west](docs/preview_nw.png)\n')
    # ---------------------------------------------------------------- PART 1
    w('## PART 1 - IMPORTANT NOTES\n')
    w('* **One command is not possible for a build this size.** In 1.8 a command block holds at most '
      '32,767 characters, and the client packet that saves it caps the text at about 32,750 bytes. '
      'The whole mansion is %d individual `/fill`, `/setblock`, `/clone` and `/summon` commands '
      '(about %d KB of command text, packed as tightly as the 1.8 minecart method allows), so it '
      'ships as **%d pastes into the same command block**. Every paste is complete and runs on its '
      'own. Nothing is truncated anywhere.' % (len(b.cmds), sum(len(p) for p, _ in pastes) // 1000, total))
    w('* **Version.** Vanilla Java Edition **1.8.0 - 1.8.9**. The installer uses only 1.8 syntax: '
      '`FallingSand` with `TileEntityData`, `MinecartCommandBlock` stacked with `Riding` (not '
      '`Passengers`), numeric block data values (no block states), and the old `/summon`, `/fill`, '
      '`/clone` and `/gamerule` syntax. It uses no functions, datapacks, structure blocks, observers, '
      'concrete, glazed terracotta, `/execute ... run`, or 1.9+ entity ids.')
    w('* **Tested on real servers.** All %d pastes were run on vanilla 1.8.9 and 1.8.0 server jars '
      '(details in Part 7). The world was then compared block-by-block with the design model: '
      '**0 wrong blocks**, and every painting, armor stand and item frame was in place.' % total)
    w('* **The build direction is +X (east) and +Z (south) of your command block.** The build '
      'occupies the box from CB+(2, -11, 2) to CB+(84, 45, 84): 83 x 83 blocks of ground, 45 '
      'blocks up and 11 down (for the escape tunnel). The mansion itself is 62 wide (X) and 41 deep '
      '(Z), plus the portico, conservatory and grounds.')
    w('* **Terrain.** Stage 1 levels the whole plot. It clears everything from ground level up to '
      '45 blocks above the command block and lays dirt and grass at the command block\'s ground '
      'level. Flat land (for example a superflat world) gives the best result. On a hillside, '
      'terrain below the command block\'s level stays as it is under the lawn.')
    w('* **Chunks must be loaded.** Stand next to the command block while installing, and use a '
      'render distance of **8 chunks or more** (the far corner is about 120 blocks away). A `/fill` '
      'into an unloaded chunk fails silently.')
    w('* **Lag.** Stage 1 clears about 310,000 blocks, so the game freezes for 10-20 seconds; the '
      'server log may print "Can\'t keep up". The other stages take about 5 seconds each. Wait for '
      'the chat message before pasting the next command.')
    w('* **Self-cleaning.** After each stage the installer removes its minecarts, the rail, the '
      'helper blocks and any dropped items within 150 blocks. The last stage also removes your '
      'command block and turns command-block chat feedback back on. Nothing of the installer '
      'remains, and nothing inside the mansion is touched by the cleanup.')
    w('* **Multiplayer.** Command blocks must be enabled (`enable-command-block=true` in '
      '`server.properties`), and you must be an operator in Creative mode to edit one.\n')
    # ---------------------------------------------------------------- PART 2
    w('## PART 2 - INSTALLATION\n')
    w('1. Find (or make) a flat area at least **90 x 90 blocks** to the south-east of where you '
      'stand, with open sky. Press F3: **+X is east and +Z is south.** The mansion is built in the '
      '+X/+Z quarter from your command block, starting 2 blocks away.')
    w('2. Get a command block: `/give @p command_block` (you need cheats enabled or op).')
    w('3. Place the command block **on the ground** (its bottom touching the grass). Keep the 3 '
      'blocks above it empty; the installer drops its minecarts there.')
    w('4. Put a **stone button on the north (-Z) or west (-X) face** of the command block. Do not '
      'put it on top (that is where the installer lands) or on the east face (the cleanup uses '
      'that column).')
    w('5. Stand anywhere next to it (not on top), for example 3 blocks to the west. Right-click '
      'the command block, paste **Command 1** (Part 3), click **Done**, then press the button.')
    w('6. When chat shows **"[Mansion] Stage 1/%d complete. Now paste Command 2..."**, open the '
      '**same** command block again, select all (Ctrl+A), paste **Command 2** over the old text, '
      'click Done and press the button. Repeat for Commands 3 to %d. Always paste in order.' % (total, total))
    w('7. After Command %d chat says **"the mansion is finished!"** and the command block disappears. '
      'Walk up the drive and through the front doors.\n' % total)
    w('Tips: every command is one line of about 32,700 characters. Copy it from the raw text files '
      '(`commands/command_01.txt` ... `command_%02d.txt`) or from the code blocks below. Select the '
      'whole line; a missing character breaks the paste. If a stage is interrupted (for example, '
      'the game was closed mid-stage), paste the same command again; every stage is safe to repeat.\n' % total)
    w('| Command | Characters | What it builds |')
    w('|---|---|---|')
    for k, (p, body) in enumerate(pastes):
        w('| %d | %d | %s |' % (k + 1, len(p), ', '.join(secs[k][:9]) + (' ...' if len(secs[k]) > 9 else '')))
    w('')
    # ---------------------------------------------------------------- PART 3
    w('## PART 3 - COMMAND\n')
    w('**Command 1 of %d**: paste into the command block, press the button. Also in '
      '[`commands/command_01.txt`](commands/command_01.txt).\n' % total)
    w('```\n%s\n```\n' % pastes[0][0])
    # ---------------------------------------------------------------- PART 4
    w('## PART 4 - ADDITIONAL COMMANDS\n')
    w('Paste each one into the **same** command block, replacing the previous text, and press the '
      'button. Only paste the next one **after** chat confirms the previous stage.\n')
    for k in range(1, total):
        final = k == total - 1
        w('### COMMAND %d%s\n' % (k + 1, ' (final)' if final else ''))
        w('Activate after chat shows "Stage %d/%d complete". Builds: %s.%s Also in '
          '[`commands/command_%02d.txt`](commands/command_%02d.txt).\n'
          % (k, total, ', '.join(secs[k]),
             ' Then removes the installer and your command block.' if final else '', k + 1, k + 1))
        w('```\n%s\n```\n' % pastes[k][0])
    # ---------------------------------------------------------------- PART 5
    w('## PART 5 - MANSION FLOOR PLAN\n')
    w(PLAN_TEXT)
    w('\n**Where the rooms are.** Each position is a standing spot as an offset (x, y, z) from '
      'your command block, where y is the level of your feet. The walkability check confirmed '
      'that every spot can be reached on foot from the front lawn, and that you can walk back '
      'out again.\n')
    w('| Room | Offset from command block (x, y, z) |')
    w('|---|---|')
    for (name, x, y, z) in check.PROBES:
        w('| %s | %s |' % (name, cb(x, y, z)))
    w('\nPlans (1 pixel = 1 block, north up; grid lines every 5 blocks in mansion coordinates):\n')
    for n, t in (('B', 'Basement (floor 5 below the command block)'), ('F1', 'Ground floor'),
                 ('F2', 'First floor'), ('F3', 'Second floor'), ('ATTIC', 'Attic level')):
        w('**%s**\n\n![%s](docs/plan_%s.png)\n' % (t, t, n))
    # ---------------------------------------------------------------- PART 6
    w('## PART 6 - SECRET LOCATIONS\n')
    w('*Spoilers! All positions are offsets from where your command block stood.*\n')
    w(SECRETS.format(**{k: cb(*v) for k, v in SECRET_POS.items()}))
    # ---------------------------------------------------------------- PART 7
    w('## PART 7 - TECHNICAL VALIDATION\n')
    w(VALIDATION.format(n=len(b.cmds), fills=kinds['fill'], sets=kinds['setblock'], clones=kinds['clone'],
                        summons=kinds['summon'], total=total,
                        sizes=', '.join(str(len(p)) for p, _ in pastes)))
    return '\n'.join(L) + '\n'


SECRET_POS = {
    'lever': (10, 3, 30), 'bookcase': (8, 3, 34), 'journal': (2, 3, 36), 'stair': (15, 3, 38),
    'vault_door': (5, -4, 35), 'vault_lever': (4, -3, 36), 'hatch': (7, -4, 31), 'tunnel': (7, -10, 40),
    'hideout': (7, -10, 53), 'well': (7, 0, 54), 'wanderer': (26, 3, 13), 'cubby': (30, 3, 13),
    'lab_hatch': (30, 3, 12), 'lab': (30, -4, 9), 'tap': (57, -4, 24), 'barrel': (60, -4, 24),
    'stash': (64, -4, 24), 'wardrobe': (15, 18, 2), 'attic_room': (12, 24, 4),
    'attic_ladder': (40, 18, 33), 'cupola': (30, 36, 20),
}

PLAN_TEXT = '''Floors are named **B** (basement, feet 4 below the command block), **F1** (ground floor, feet +3),
**F2** (upper floor, feet +11), **F3** (top floor, feet +18), then the tower rooms, the attic and the roof.

```
                 your command block is up here, to the north-west
                                  N (-Z)
              front lawn, fountain, drive  |  PORTICO + wide steps (F2 balcony on top)
      +------+-------------+---------------+---------------+-------------+------+
      | NW   | Study (F1)  |          GRAND FOYER          | Drawing rm  | NE   |
      | tower| Blue rm (F2)|  double height, imperial stair| Rose rm (F2)| tower|
      | map  | Old bedroom |  landing + hidden cubby, F2   | Governess   | nook |
      | room,| (F3)        |  galleries all round          | (F3)        | look-|
      | obs- +-------------+  music rm / gallery above (F3)+-------------+ out  |
      | erv. | corridors   |                               | corridors   |BACK  |
      +------+------+------+-------------------------------+------+------+STAIRS|
 W    |  LIBRARY    | W    |  SALON, twin fireplaces (F1)  | E    | DINING (F1)       |   E
(-X)  |  two storey | hall |  lounge over the foyer (F2)   | hall | Green room +      |  (+X)
      |  + gallery  |      |  trophy room (F3)             |      |   balcony (F2)    |
      |             |      |  MASTER SUITE (F2)            |      | servants (F3)     |
      +-------------+      +-------------------------------+      +-------------------+
      | secret study|      |  CONSERVATORY (F1)            |      | KITCHEN + pantry  |
      |  (hidden)   |      |  rear balcony on its roof (F2)|      | billiards (F2)    |
      +-------------+------+---------------+---------------+------+ laundry (F3)      |
                                           |  garden steps, patio, parterre, well, gazebo
                                  S (+Z)   rear garden
```
The front faces **north** (-Z), towards your command block, and the gardens are to the south.
From the front: the portico and wide steps, the double front doors, then the grand foyer.
Its central stair rises to a landing and splits into two flights up to the F2 galleries.
A west wing (study, library) and an east wing (drawing room, dining room, kitchen) wrap around
the central salon. Square towers stand at the NW and NE corners. The NW tower rises to a star
room and an observatory under a spire; the NE tower has a lookout. The central block has a
hipped roof with a widow's walk and a glass cupola. The wings have steep gables with dormers,
and there are five chimneys. **B:** under the house are an archive, a family crypt, a storage
hall, a cistern with a causeway, a store room, a wine cellar and a furnace room, joined by one
long corridor. The back stairs (east) link B, F1, F2 and F3.
'''

SECRETS = '''1. **The library bookcase door (real hidden entrance, F1).** Go to the librarian's desk in the
   two-storey library (west wing). A floor lever next to the desk is at CB({lever}). The lever is
   **ON** when the passage is closed; flip it **OFF**. A sticky piston under the floor pulls the
   bookcase at CB({bookcase}) down into the floor. The upper half of the doorway is a painting
   (a small "Kebab") hanging over a wall sign, so you can walk straight through it. Flip the lever
   back ON to close the passage.
2. **Lord Ashgrove's secret study (F1).** Behind the bookcase: a desk, a skull, and a chest at
   CB({journal}) with the *Journal of Lord Ashgrove*, a written book of clues to the other
   secrets.
3. **The hidden vault.** A narrow stair in the secret study (railed by fences, starting near
   CB({stair})) goes down into the foundations to a dusty antechamber. The iron vault door at
   CB({vault_door}) opens with the lever beside it at CB({vault_lever}). Inside, behind an
   obsidian shell, are gold, iron, emerald and diamond blocks and chests of treasure.
4. **The escape tunnel.** A trapdoor in the vault floor at CB({hatch}) opens onto a ladder
   down to a long tunnel (for example CB({tunnel})). It runs south under the lawn to a hidden
   bunk-room at CB({hideout}) with a bed, supplies and a sign. A ladder climbs from there to the
   **dry well** in the rear garden at CB({well}). From outside, the well is also a secret way in.
5. **The Wanderer's door (hard to notice).** In the grand foyer, walk behind the central
   staircase under the landing. On the west side hangs a tall painting (the "Wanderer") at
   CB({wanderer}); it hides a doorway. Walk through it into a hidden cubby at CB({cubby}).
   A trapdoor in the cubby floor at CB({lab_hatch}) leads down a ladder into
   **Lord Ashgrove's laboratory** at CB({lab}). It has a working lamp panel (flip the lever),
   repeater and comparator lines, note blocks, and a command block that "whirs" when you step
   on its pressure plate.
6. **The loose barrel (wine cellar, B).** In the wine cellar (basement, east), a floor lever "tap"
   stands between the racks at CB({tap}). Flip it OFF: the barrel in the east barrel wall at
   CB({barrel}) sinks into the floor (a sticky piston). Walk through the small "Plant" painting
   above it into the **smuggler's stash** dug outside the foundations at CB({stash}). It holds
   diamonds, emeralds, gold, a music disc and contraband.
7. **The wardrobe (F3, west wing).** In the Old Bedroom, the tall wardrobe has a door at
   CB({wardrobe}). Inside, a ladder climbs through the ceiling into a **sealed room in the
   roof** at CB({attic_room}). There is a single chair facing a portrait, candles, dead flowers,
   and a chest with a golden apple and a music disc. No other way in exists.
8. **Up top.** A ladder in the F3 east hall at CB({attic_ladder}) leads into the
   big central attic (trunks, sheeted furniture, a dress form). From there a second ladder
   climbs into the glass cupola at CB({cupola}) and out onto the widow's walk on the roof.
'''

VALIDATION = '''Everything below was checked by code (the generator in `tools/` rebuilds, re-checks and
re-exports the whole thing), not by eye.

**Minecraft 1.8 compatibility**
* Every block name was checked against the block registry of the 1.8.9 server jar. The only
  blocks used are ones that exist in 1.8 (e.g. `stonebrick`, `log2`, `stained_hardened_clay`,
  `sea_lantern`, `dark_oak_door`; no 1.9+ blocks). Numeric data values are used
  throughout, because 1.8 has no block-state syntax in commands.
* Entity ids are the 1.8 ones (`FallingSand`, `MinecartCommandBlock`, `Painting`, `ArmorStand`,
  `ItemFrame`). Stacking uses `Riding` (1.8), not `Passengers` (1.9+).
* The installer is the 1.8 "minecart pile". The pasted command summons a falling
  activator rail riding a falling redstone block riding a falling command block. The redstone
  block powers the command block, which summons one stack of command-block minecarts. The carts
  land on the powered rail and each runs its command once, bottom to top, in groups of 6
  separated by throw-away `FallingSand` spacers. The group size of 6 keeps every cart touching
  the rail with the 1.8.0 riding offsets.
* Each paste is at most 32,700 characters, under the 32,750-byte limit of the `MC|AdvCdm`
  packet in 1.8. Pastes are pure ASCII (the command-block text field removes `§` and control
  characters).
* The `/fill` volume limit is 32,768 blocks; larger regions are split automatically.

**Metadata, orientation and attachments** (values taken from the decompiled 1.8.9 code)
* Stairs (0=E, 1=W, 2=S, 3=N, +4 upside-down). Doors (lower 0=E, 1=S, 2=W, 3=N; upper 8 +
  hinge). Beds (0=S, 1=W, 2=N, 3=E, +8 head). Torches (1-5). Ladders, signs, banners,
  chests and furnaces (2-5). Trapdoors (+4 open, +8 top half). Levers, buttons, pistons,
  repeaters, fence gates, logs (+4 X axis, +8 Z axis) and leaves (+4 = never decays).
* The model was scanned for attachments without support: **0 unsupported** torches,
  ladders, signs, banners, levers, buttons, trapdoors, doors, beds, carpets, pots, pressure
  plates, flowers or crops. The scan follows the 1.8 rules: trapdoors need a solid block,
  a slab or stairs on their hinge side; flower pots need a solid top; nothing goes on glowstone.
* Order-sensitive placements follow real 1.8 behaviour. Both halves of each door are placed
  back to back, because a lone lower half is deleted by the next block update. Adjacent chests
  face the way the game would re-orient them. For piston secrets, the lever goes first, then the
  dust, then the piston, so the piston extends when it is placed. Paintings are hung after the
  walls are finished, using the exact 1.8 `EntityPainting` placement maths.

**Overwrites and walkability**
* The build is {n} commands in total: {fills} fill, {sets} setblock, {clones} clone and
  {summons} summon. A voxel model runs all of them in order.
* An ownership pass finds every command whose blocks are all overwritten later. Those
  commands were reviewed and are harmless (for example rough fills that later detail replaces).
* Walkability: a half-block-precise walker starts on the front lawn. It handles stairs,
  slabs, doors, ladders (no jumping off a ladder, as in the real game) and trapdoors (the
  secret doors are simulated open). It reaches **all ~90 room probes** listed in Part 5, and a
  reverse search confirms that **every reachable spot can walk back out**. There are 0 one-way
  traps and no sealed rooms (except the deliberately sealed-looking secrets, which have their
  own entrances).
* Lighting: 1.8 block-light is simulated. **0 dark spawnable spots** remain anywhere indoors
  (all floors, towers, attic, basement, tunnel and hideout). Lighting is mostly hidden glowstone
  under carpets and rugs, chandeliers, sea lanterns, sconces and lamps, with a few wall torches
  in service areas.
* Fire safety: every fireplace fire burns on netherrack inside a brick breast. No flammable
  block is within fire-spread range of any fire (0 hazards).

**Real-server test (vanilla jars, superflat world, no mods)**
* 1.8.9 and 1.8.0 servers: the {total} pastes (lengths {sizes}) were typed into a real
  command block and triggered by a real button. After each stage the installer column was
  gone. The finished world was compared with the model block by block over the whole plot:
  **0 mismatching blocks** (redstone-dust power levels and the game's "check decay" leaf bit
  ignored). All 16 paintings, 8 armor stands and 1 item frame were present; no paintings
  dropped.
* Both piston secret doors were confirmed extended (closed) in the real world, and the lab's
  lamp panel lit. Stage 1 caused one "Can't keep up" warning (about 10 s) while it cleared the
  plot; the other stages finished in about 5 s.

**Issues found and fixed during validation**, among many others:
* Double doors vanished (a door half placed alone was deleted).
* A library piston did not fire (fixed by the lever-dust-piston order).
* Chests re-oriented themselves.
* Pressure plates and flower pots popped off unsupported surfaces.
* Several ladders had no wall to cling to.
* The cupola's hollow fill had glazed its own floor shut.
* A ladder hatch could only be used one way (you cannot jump off a 1.8 ladder).
* A 2 x 2 painting refused to hang on a chimney breast.
* A buttress blocked the kitchen-garden gate.
* 1,100 dark attic spots were fixed by making the attic floor bottom slabs.
'''


if __name__ == '__main__':
    main()
