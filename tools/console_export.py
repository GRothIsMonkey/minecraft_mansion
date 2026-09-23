"""Write the server-console edition: commands_console/console_NN.txt and CONSOLE_INSTALL.md.

The legacy command-block edition (commands/command_NN.txt, MANSION.md) is not touched.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import console_build as CB       # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, 'commands_console')


_TURN = {'NW': 'NE', 'NE': 'SE', 'SE': 'SW', 'SW': 'NW', 'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N',
         'north': 'east', 'east': 'south', 'south': 'west', 'west': 'north'}


def turn_words(text):
    """Design labels name compass directions of the original layout; after the quarter turn
    (N->E, E->S, S->W, W->N) the same room lies in the turned direction."""
    import re

    def rep(mo):
        w = mo.group(0)
        t = _TURN.get(w) or _TURN.get(w.lower())
        if t is None:
            return w
        return t.capitalize() if w[0].isupper() and w.lower() in _TURN and len(w) > 2 else t
    return re.sub(r'\b(?:NW|NE|SE|SW|N|E|S|W|[Nn]orth|[Ee]ast|[Ss]outh|[Ww]est)\b', rep, text)


def stage_summaries(b, st):
    out = []
    for (_, _, (a, z)) in st:
        s = []
        for c in b.cmds[a:z]:
            name = c.section
            for pre, short in (('facade', 'facades'), ('auto lighting', 'extra lighting'), ('grounds', 'grounds')):
                if name.startswith(pre):
                    name = short
            name = turn_words(name)
            if name not in s:
                s.append(name)
        out.append(s)
    return out


def write_files(b=None):
    b = b or CB.assemble()
    st = CB.pack(b)
    lines = [CB.setup_command()] + [p for p, _, _ in st]
    os.makedirs(OUTDIR, exist_ok=True)
    for f in os.listdir(OUTDIR):
        if f.startswith('console_') and f.endswith('.txt'):
            os.remove(os.path.join(OUTDIR, f))
    for k, text in enumerate(lines):
        with open(os.path.join(OUTDIR, 'console_%02d.txt' % (k + 1)), 'w') as fh:
            fh.write(text + '\n')
    total = len(lines)
    manifest = {
        'entrance': CB.ENTRANCE, 'build_box': CB.BUILD_BOX, 'pad': CB.PAD, 'stand': CB.STAND,
        'min_view_distance': CB.MIN_VIEW_DISTANCE,
        'stages': [{'file': 'console_%02d.txt' % (k + 1), 'chars': len(t),
                    'sha1': __import__('hashlib').sha1((t + '\n').encode()).hexdigest(),
                    'expect': ('Block placed' if k == 0 else
                               '[%s] %s' % (CB.SAY_NAME, CB.message(k + 1, total)))}
                   for k, t in enumerate(lines)],
    }
    with open(os.path.join(OUTDIR, 'manifest.json'), 'w') as fh:
        json.dump(manifest, fh, indent=1)
    return b, st, lines


# ------------------------------------------------------------------ images --
def render_images(b):
    """Front view and floor plans of the TURNED mansion, labelled in world coordinates."""
    import numpy as np
    from PIL import Image, ImageDraw
    import render
    import rotation as R
    from engine import SX0, SY0, SZ0
    F = R.rotated_frame(b)
    docs = os.path.join(ROOT, 'docs')
    x1, y1, z1, x2, y2, z2 = CB.BUILD_BOX
    # crop box (world) -> frame indices
    ci = lambda wx, wy, wz: tuple(v - o for v, o in zip(R.world_to_r(wx, wy, wz), (SX0, SY0, SZ0)))
    a0, b0, c0 = ci(x1 - 2, 71, z1 - 2)
    a1, b1, c1 = ci(x2 + 7, 121, z2 + 2)
    ids = F.ids[a0:a1 + 1, b0:b1 + 1, c0:c1 + 1]
    me = F.meta[a0:a1 + 1, b0:b1 + 1, c0:c1 + 1]
    render.iso(ids, me, os.path.join(docs, 'console_view_front_se.png'), scale=5, view='SE')
    levels = [('site', 'Ground floor and grounds (feet Y 76 in the house, lawn Y 73)', 72, 81),
              ('B', 'Basement (feet Y 69) and escape tunnel (feet Y 63)', 62, 70),
              ('F2', 'Upper floor (feet Y 84)', 83, 88), ('F3', 'Top floor (feet Y 91)', 90, 95),
              ('attic', 'Attic, tower rooms and roof walk (Y 96-112)', 96, 112)]
    out = []
    sc = 8
    for tag, title, ya, yb in levels:
        wx0, wz0 = x1 - 2, z1 - 2
        wx1, wz1 = min(x2 + (10 if tag == 'site' else 7), R.r_to_world(R.SX1, 0, 0)[0]), z2 + 2
        img = Image.new('RGB', ((wx1 - wx0 + 1) * sc + (130 if tag == 'site' else 0), (wz1 - wz0 + 1) * sc),
                        (30, 30, 30))
        d = ImageDraw.Draw(img)
        for wx in range(wx0, wx1 + 1):
            for wz in range(wz0, wz1 + 1):
                i, _, k = ci(wx, 0, wz)
                col = F.ids[i, ya - R.OFF[1] - SY0:yb - R.OFF[1] - SY0 + 1, k]
                nz = np.nonzero(col)[0]
                if not len(nz):
                    c = (45, 45, 45)
                else:
                    j = ya - R.OFF[1] - SY0 + nz[-1]
                    c = render.color(int(F.ids[i, j, k]), int(F.meta[i, j, k]))
                    c = render._shade(c, 0.55 + 0.45 * (nz[-1] + 1) / (yb - ya + 1))
                px, pz = (wx - wx0) * sc, (wz - wz0) * sc
                d.rectangle([px, pz, px + sc - 1, pz + sc - 1], fill=c)
        for wx in range(wx0, wx1 + 1):
            if wx % 10 == 0:
                d.line([((wx - wx0) * sc, 0), ((wx - wx0) * sc, img.size[1])], fill=(200, 200, 200))
                d.text(((wx - wx0) * sc + 2, 2), 'X%d' % wx, fill=(255, 255, 0))
        for wz in range(wz0, wz1 + 1):
            if wz % 10 == 0:
                d.line([(0, (wz - wz0) * sc), (img.size[0], (wz - wz0) * sc)], fill=(200, 200, 200))
                d.text((2, (wz - wz0) * sc + 2), 'Z%d' % wz, fill=(255, 255, 0))
        def mark(wx, wz, text, colr, dy=0):
            px, pz = (wx - wx0) * sc, (wz - wz0) * sc
            d.ellipse([px - 3, pz - 3, px + sc + 2, pz + sc + 2], outline=colr, width=3)
            d.text((px + sc + 4, pz - 2 + dy), text, fill=colr)
        mark(-251, 267, 'ENTRANCE -251 73 267', (255, 60, 60))
        if tag == 'site':
            mark(CB.STAND[0], CB.STAND[2], 'STAND HERE (-225 73 267)', (60, 255, 60), dy=-14)
            mark(CB.PAD[0], CB.PAD[2], 'installer pad (sky, Y %d)' % CB.PAD[1], (80, 200, 255), dy=12)
        d.text((img.size[0] - 150, img.size[1] - 14), 'N is up, E is right', fill=(255, 255, 255))
        name = 'console_plan_%s.png' % tag
        img.save(os.path.join(docs, name))
        out.append((name, title))
    return out


# -------------------------------------------------------------------- docs --
def load_tests():
    """Real-server reports (console_test.py writes out/console_test_*.json; the reports of the
    final runs are kept in docs/console_tests/ as mc189_flat, mc180_flat, mc189_terrain)."""
    res = {}
    d = os.path.join(ROOT, 'docs', 'console_tests')
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith('.json'):
                res[f[:-5]] = json.load(open(os.path.join(d, f)))
    return res


def mw(mx, y, mz):
    import rotation as R
    from mansion_base import X0, Z0
    return R.block(mx + X0, y, mz + Z0)


def xyz(p):
    return '`%d %d %d`' % tuple(p)


def render_doc(b, st, lines, plans):
    import check
    import rotation as R
    total = len(lines)
    x1, y1, z1, x2, y2, z2 = CB.BUILD_BOX
    px, py, pz = CB.PAD
    sx, sy, sz = CB.STAND
    tests = load_tests()
    summ = stage_summaries(b, st)
    L = []
    w = L.append
    w('# Ashgrove Manor - SERVER CONSOLE INSTALLATION (Minecraft Java 1.8 / 1.8.9)\n')
    w('> ## BACK UP THE WORLD BEFORE INSTALLATION.')
    w('> Stage 2 **clears and levels** the whole building site. Everything inside the box below is '
      'replaced for good: trees, hills, buildings, chests, redstone.')
    w('>')
    w('> **Area that will be changed (absolute world coordinates, inclusive):**')
    w('>')
    w('> | | from | to | size |')
    w('> |---|---|---|---|')
    w('> | X | %d | %d | %d blocks |' % (x1, x2, x2 - x1 + 1))
    w('> | Y | %d | %d | %d blocks |' % (y1, y2, y2 - y1 + 1))
    w('> | Z | %d | %d | %d blocks |' % (z1, z2, z2 - z1 + 1))
    w('>')
    w('> Everything from Y 73 up to Y %d in that X/Z square becomes air. Y 69-72 becomes dirt with grass on top, and '
      'the basement, cellars, cistern and escape tunnel are dug below that, down to Y %d. The installer also uses '
      'a few blocks in the sky at X %d..%d, Y %d..%d, Z %d (see below). Nothing else in the world is touched.\n'
      % (y2, y1, px, px + 2, py, py + 3, pz))
    w('![The console edition seen from the south-east: the front faces east](docs/console_view_front_se.png)\n')
    w('This file is all you need to install the mansion from your hosting dashboard\'s **server console**. '
      'You never open a command block. It is the same Ashgrove Manor as the command-block edition '
      '(`commands/command_01.txt` ... `command_09.txt` and `MANSION.md`, kept unchanged as a fallback). '
      'It has been moved to your coordinates and turned to face east.\n')
    # ------------------------------------------------------------ 1 summary
    w('## 1. Quick facts\n')
    w('| | |')
    w('|---|---|')
    w('| Minecraft | Java Edition **1.8.0 - 1.8.9**, vanilla server. Tested on real 1.8.9 and 1.8.0 servers. |')
    w('| Main entrance | Centre of the front double doors: **X -251, Z 267**. The doors themselves are the blocks '
      '`-251 76 266` and `-251 76 267`. |')
    w('| Facing | **EAST.** Walk out of the front doors and you go **+X (east)**; walk in and you go -X (west). |')
    w('| Ground level | The lawn is grass at **Y 72**, so you stand on it at **Y 73** (the F3 screen shows Y 73). '
      'The front steps start on the lawn at Y 73. The ground floor is raised over the basement, like the '
      'original design, so the door sill is 3 steps up: door feet at **Y 76**. |')
    hx1, hx2, hz1, hz2, stx = house_extent(b)
    w('| House | Walls and roofs from X %d to X %d and Z %d to Z %d; the portico balcony and front steps reach '
      'east to X %d. The whole house is west of the entrance except the portico and steps. |'
      % (hx1, hx2, hz1, hz2, stx))
    w('| Whole site (changed area) | X %d..%d, Y %d..%d, Z %d..%d |' % (x1, x2, y1, y2, z1, z2))
    w('| Console lines | **%d**, pasted in order: `commands_console/console_01.txt` ... `console_%02d.txt` |'
      % (total, total))
    w('| Longest line | %d characters (every line is at most %d) |' % (max(len(t) for t in lines), CB.LIMIT))
    w('| Leading slash | **Do not type a `/`.** Paste each file exactly as it is. (A vanilla 1.8 console would '
      'also accept a leading `/`; the files do not have one.) |')
    w('| Stand here | **X %d, Y %d, Z %d**: on the ground just outside the east edge of the site, in line '
      'with the front doors, facing west. |' % (sx, sy, sz))
    w('| Server view-distance | **%d or more** (`view-distance` in `server.properties`; vanilla default is 10). '
      'This server setting decides which chunks stay loaded around you. Your own client render distance '
      'does not change that, but set it to 8 or more if you want to watch the whole site being built. |'
      % CB.MIN_VIEW_DISTANCE)
    w('| Installer | A single bedrock "pad" at **%d %d %d** (in the sky, 4 blocks east of where you stand). Each '
      'stage drops a tiny command machine onto it. The machine removes itself, and the last stage removes the pad. |'
      % (px, py, pz))
    w('| Time | Each stage finishes in about 1-5 s on the test machine (%s of building in total), so the whole '
      'install is mostly the time you spend pasting. Slower hosts take longer. **Always wait for the message, '
      'not for a number of seconds.** |'
      % ('%d s' % sum(x.get('secs', 0) for x in tests.get('mc189_flat', {}).get('stages', []))
         if tests.get('mc189_flat') else 'under a minute'))
    w('')
    w('World orientation (north is up, east is right):\n')
    w('```')
    w('                                   NORTH (-Z)')
    w('        X -309                                                        X -227')
    w('  Z 226 +--------------------------------------------------------------+')
    w('        |  dry well    +---------------------------------------+ NE    |')
    w('        |  (tunnel     | NORTH WING: secret study | library |  |tower  |')
    w('        |   exit)      |   study, map room, blue room...      |  +--+  |')
    w('  WEST  |  parterre    +--------------+--------+--------------+     |  |  EAST')
    w('  (-X)  |  rear garden |CONSERVATORY  | SALON  | GRAND FOYER  |PORTICO |  (+X)')
    w('        |  gazebo      |              |        |    doors >>>>|steps   |  fountain  drive -->')
    w('        |              +--------------+--------+--------------+ X -251 |')
    w('        |  kitchen     | SOUTH WING: kitchen, pantry | dining | +--+   |')
    w('        |  garden      |   drawing room, back stairs          | |SE    |')
    w('        |              +---------------------------------------+ tower |')
    w('  Z 308 +--------------------------------------------------------------+')
    w('                                   SOUTH (+Z)          you stand at X %d, Z %d ->' % (sx, sz))
    w('```\n')
    w('Everything turned with the house. The original "north-west tower" (star room and observatory) is now the '
      '**north-east tower**. The original "north-east tower" (lookout) is now the **south-east tower**. The library wing '
      'is the **north wing** and the kitchen wing is the **south wing**. The gardens, gazebo and dry well are '
      'behind the house to the **west**.\n')
    for name, title in plans:
        w('**%s**\n\n![%s](docs/%s)\n' % (title, title, name))
    # ------------------------------------------------------------ 2 before
    w('## 2. Before you start\n')
    w('1. **Back up the world** (most dashboards have a Backups page; or stop the server and copy the world folder).')
    w('2. Check that nothing you want to keep is inside **X %d..%d, Y %d..%d, Z %d..%d**.' % (x1, x2, y1, y2, z1, z2))
    w('3. In `server.properties` make sure that:')
    w('   * `enable-command-block=true` (the installer uses command blocks and command-block minecarts);')
    w('   * `view-distance` is **%d or more** (10 is the vanilla default). If you change a property, restart the '
      'server.' % CB.MIN_VIEW_DISTANCE)
    w('4. The installer column needs open sky at **X %d..%d, Y %d..%d, Z %d**, which is normally empty air. If a '
      'mountain or a build of yours reaches Y %d there, move it first.' % (px, px + 2, py, py + 4, pz, py))
    w('5. Flat ground near Y 72 gives the best result. The site is levelled to a lawn at Y 72. Higher terrain '
      'inside the site is cut away; land outside the site is not changed, so a hillside next to the site will '
      'show a cut face. Terrain below Y 69 inside the site is kept, apart from what the basement digs out.')
    w('')
    # ------------------------------------------------------------ 3 install
    w('## 3. Installation, step by step\n')
    w('1. Start the server and **join it** with your Minecraft account.')
    w('2. Go to **X %d, Y %d, Z %d** and stay there until the end. That is on the ground, just east of the site, '
      'in line with the front doors. Creative mode is easiest, but survival is safe too: nothing is built '
      'where you stand. Your character keeps the site\'s chunks loaded; the server console cannot. If you '
      'wander more than a few chunks away, commands aimed at unloaded chunks fail.' % (sx, sy, sz))
    w('3. Open your hosting dashboard and go to the **Console** page.')
    w('4. Open `commands_console/console_01.txt`, copy its single line, paste it into the console input and '
      'press Enter. Paste exactly the file contents, without a leading `/`.')
    w('5. Wait for the reply in the table below. The reply comes on its own line in the console log; some '
      'panels put `[Server thread/INFO]:` in front of it.')
    w('6. Paste the next file. Continue in order until `console_%02d.txt` answers '
      '**`[Installer] Mansion Console Stage %d/%d complete. Mansion construction complete.`**' % (total, total, total))
    w('7. Walk through the front doors at -251 76 266/267 (up the front steps from the lawn).\n')
    w('What a build stage prints in the console (stage 5 as an example, copied from the test server):\n')
    w('```')
    w('Object successfully summoned')
    w('[Installer: Object successfully summoned]')
    w('[Installer: Game rule has been updated]')
    w('[Installer] %s' % CB.message(5, total))
    w('[Installer: 7 blocks filled]')
    w('```\n')
    w('The first line comes straight away and means the console accepted your line. The `[Installer] Mansion '
      'Console Stage ... complete` line means that stage is fully built and its machinery has removed '
      'itself. **Paste the next file only after the "complete" line.** The line after it is the machine '
      'clearing itself away. Players in the game see the `[Installer] ...` line in chat.\n')
    w('| # | File | Chars | Reply to wait for | What it builds |')
    w('|---|---|---|---|---|')
    w('| 1 | `console_01.txt` | %d | `Block placed` | places the installer pad at %d %d %d |' % (len(lines[0]), px, py, pz))
    cost = CB.load_costs()
    for k, (p, _, (a, z)) in enumerate(st):
        stage = k + 2
        what = ', '.join(summ[k][:6]) + (' ...' if len(summ[k]) > 6 else '')
        work = sum(cost(c.text) for c in b.cmds[a:z])
        if stage == 2:
            what = 'clears the site down to Y 73 and lays the lawn at Y 72'
        if work >= 1.0:
            what += ' (**heavy**: big wall shells; the server pauses for a few seconds)'
        if stage == total:
            what += '; removes the pad; restores command-block output'
        w('| %d | `console_%02d.txt` | %d | `[Installer] %s` | %s |' % (stage, stage, len(p), CB.message(stage, total), what))
    w('')
    fz = freezes(tests)
    w('**Lag.** The heavy walls are split over several small stages, so the server never has to do all of them '
      'at once. %s Every other stage took about 1 s. Players on the server just see the game pause for a moment. '
      'Nothing runs between stages: the installer leaves no clock and no redstone loop behind.\n' % fz)
    # ------------------------------------------------------------ 4 problems
    w('## 4. If something goes wrong\n')
    w('| You see | Meaning | What to do |')
    w('|---|---|---|')
    w('| `Cannot place block outside of the world` (after console_01) | The pad\'s chunk is not loaded: no player is near it. | Stand at %d %d %d (step 2) and paste console_01 again. |' % (sx, sy, sz))
    w('| `Cannot summon the object out of the world` | Same: the pad\'s chunk is not loaded. | Stand at the spot, paste the same file again. |')
    w('| `Data tag parsing failed: ...` or `Unknown command` | The line was cut short or changed when it was copied. Nothing was built. | Copy the whole file again (every file is one line) and paste it again. See "Known limitations" if your console shortens long lines. |')
    w('| `Object successfully summoned` but no "complete" line after about 2 minutes | The installer did not run (for example command blocks are disabled, or the chunk unloaded). | Check `enable-command-block=true`, stand at the spot, run the **cleanup** below, then paste the same file again. |')
    w('| The server crashed or restarted during a stage | The stage stopped part-way. | Start the server, stand at the spot, run the **cleanup** below, paste `console_01.txt` again if the pad is gone (`testforblock %d %d %d bedrock` says whether it is there), then paste the stage that did not finish. |' % (px, py, pz))
    w('')
    w('**Repeating a stage is safe.** Every stage only places blocks, so running it twice gives the same result. '
      'Paintings, armor stands and the item frame clear their old copy before they are summoned, so they are '
      'never duplicated. **Never** go back and repeat stage 2 after later stages have run: it clears the site.\n')
    w('### Emergency stop and manual cleanup\n')
    w('Paste these into the console one at a time (no `/`). They only touch the installer area in the sky and the '
      'build site. They are safe to run at any time, even when nothing is left to clean:\n')
    w('```')
    for c in cleanup_commands():
        w(c)
    w('```\n')
    w('The first two remove the command minecarts and falling blocks of the installer. The `fill` removes the '
      'installer column **and the pad**; paste `console_01.txt` again before you continue with the next stage. '
      'The two gamerules put command-block logging back to normal (the installer turns them off during a stage '
      'and back on at its end). The last line removes dropped items from the site.\n')
    # ------------------------------------------------------------ 5 verify
    w('## 5. Check that it finished\n')
    w('After the final message, these console commands confirm it. The replies are the ones the test server gave:\n')
    ver = tests.get('mc189_flat', {}).get('verify', {})
    w('| Command | Reply when everything is finished |')
    w('|---|---|')
    notes = {0: 'the pad is gone', 1: 'no installer minecarts left', 2: 'no falling blocks left',
             3: 'front door, north leaf', 4: 'front door, south leaf'}
    import console_test as CT
    for i, c in enumerate(CT.VERIFY_COMMANDS):
        reply = '; '.join(ver.get(c, []))
        w('| `%s` | %s (%s) |' % (c, ('`%s`' % reply) if reply else '*no reply at all*', notes[i]))
    w('')
    w('In 1.8 a `testfor` whose selector matches nothing prints nothing. If an installer minecart or falling '
      'block were still there, it would answer `Found ...`; then run the cleanup commands in section 4.\n')
    w('Afterwards none of these should exist: the bedrock pad, command blocks, redstone blocks or activator rails '
      'at %d..%d %d..%d %d, command-block minecarts, falling blocks (`FallingSand`) and dropped items. The '
      'installer leaves no scaffolding and no clock. The only command block in the finished mansion is the '
      '"whirring machine" prop in Lord Ashgrove\'s laboratory (at %s, basement). Command-block chat output and '
      'admin-command logging are switched back on (the vanilla defaults).\n'
      % (px, px + 2, py, py + 3, pz, xyz(mw(35, -4, 12))))
    # ------------------------------------------------------------ 6 rooms
    w('## 6. Where things are (world coordinates)\n')
    w('Standing positions (your feet). The walk test reached every one of them on foot from the front lawn, '
      'and walked back out again.\n')
    w('| Room | X Y Z | Room | X Y Z |')
    w('|---|---|---|---|')
    pr = [(turn_words(n), mw(x, y, z)) for (n, x, y, z) in check.PROBES]
    half = (len(pr) + 1) // 2
    for i in range(half):
        a = pr[i]
        bb = pr[i + half] if i + half < len(pr) else ('', None)
        w('| %s | %s | %s | %s |' % (a[0], xyz(a[1]), bb[0], xyz(bb[1]) if bb[1] else ''))
    w('\nBasement feet level is Y 69 and the ground floor is Y 76. The upper floor is Y 84, the top floor Y 91, '
      'the attic about Y 97 and the roof walk Y 109. Useful facilities: kitchen (furnaces, crafting, cauldron, '
      'chests), pantry, storage hall and store room (chests), enchanting table and brewing stand, an anvil, '
      'beds in every bedroom, and chests throughout.\n')
    # ------------------------------------------------------------ 7 secrets
    w('## 7. Secret places (spoilers)\n')
    w(SECRETS_WORLD.format(**{k: xyz(mw(*v)) for k, v in SECRET_POS.items()}))
    # ------------------------------------------------------------ 8 tests
    w('## 8. How this edition was built and tested\n')
    w(TESTING.format(total=total, n=len(b.cmds), limit=CB.LIMIT, longest=max(len(t) for t in lines),
                     vd=CB.MIN_VIEW_DISTANCE, sx=sx, sy=sy, sz=sz))
    for key, label in (('mc189_flat', '1.8.9, superflat world with the lawn at Y 72'),
                       ('mc180_flat', '1.8.0, superflat world with the lawn at Y 72'),
                       ('mc189_terrain', '1.8.9, normal generated terrain (hills, trees, caves)')):
        t = tests.get(key)
        if not t:
            continue
        ok = sum(1 for r in t['results'] if r[1])
        bad = [r for r in t['results'] if not r[1]]
        secs = sum(x.get('secs', 0) for x in t['stages'])
        lag = max([int(__import__('re').search(r'(\d+)ms', l).group(1)) for x in t['stages'] for l in x.get('lag', [])]
                  or [0])
        w('**%s**: %d/%d checks passed%s. Install time %.0f s; the longest single freeze was %.1f s.\n'
          % (label, ok, len(t['results']), '' if not bad else ' (failed: %s)' % '; '.join(r[0] for r in bad),
             secs, lag / 1000.0))
        if key == 'mc189_flat':
            for r in t['results']:
                w('* %s %s' % ('PASS' if r[1] else '**FAIL**', r[0]))
            w('')
    tt = tests.get('mc189_terrain')
    note = ''
    if tt:
        ok = [r for r in tt['results'] if r[0].startswith('no water or lava')]
        if ok and ok[0][1]:
            note = ' (in the generated-terrain test, with hills up to Y 92 and water on the site, none did)'
    w(LIMITS.replace('{terrain_note}', note))
    return '\n'.join(L) + '\n'


def house_extent(b):
    import numpy as np
    import rotation as R
    from blockids import BLOCK_IDS as B
    from engine import SX0, SY0, SZ0
    F = R.rotated_frame(b)
    hi = np.argwhere(F.ids[:, 84 - R.OFF[1] - SY0:, :] != 0)            # upper storeys and roofs
    hx = hi[:, 0] + SX0 + R.OFF[0]
    hz = hi[:, 2] + SZ0 + R.OFF[2]
    front = [mw(30, 0, -8)[0]]          # lowest rise of the wide front steps (facades.portico)
    walls = hx[hx < -250]
    return int(walls.min()), int(hx.max()), int(hz.min()), int(hz.max()), int(max(front))


def freezes(tests):
    """Longest stage (paste -> "complete" line) per test world.  Vanilla prints "Can't keep up"
    at most once per 15 s, so the stage times are the better measure."""
    out = []
    for key, label in (('mc189_flat', 'flat test world'), ('mc189_terrain', 'hilly generated test world')):
        t = tests.get(key)
        if not t:
            continue
        secs, f = max((x.get('secs', 0), x['file']) for x in t['stages'])
        out.append('On the %s the longest stage took %.1f s from paste to "complete" (%s).' % (label, secs, f))
    return ' '.join(out) or 'The heaviest stages pause the server for a few seconds.'


def cleanup_commands():
    px, py, pz = CB.PAD
    x1, y1, z1, x2, y2, z2 = CB.BUILD_BOX
    return ['kill @e[type=MinecartCommandBlock,x=%d,y=%d,z=%d,dx=6,dy=100,dz=6]' % (px - 3, py - 2, pz - 3),
            'kill @e[type=FallingSand,x=%d,y=%d,z=%d,dx=6,dy=100,dz=6]' % (px - 3, py - 2, pz - 3),
            'fill %d %d %d %d %d %d air' % (px - 1, py, pz - 1, px + 3, py + 4, pz + 1),
            'gamerule commandBlockOutput true',
            'gamerule logAdminCommands true',
            'kill @e[type=Item,x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d]' % (x1, y1, z1, x2 - x1, y2 - y1, z2 - z1)]


SECRET_POS = {
    'lever': (10, 3, 30), 'bookcase': (8, 3, 34), 'journal': (2, 3, 36), 'stair': (15, 3, 38),
    'vault_door': (5, -4, 35), 'vault_lever': (4, -3, 36), 'hatch': (7, -4, 31), 'tunnel': (7, -10, 40),
    'hideout': (7, -10, 53), 'well': (7, 0, 54), 'wanderer': (26, 3, 13), 'cubby': (30, 3, 13),
    'lab_hatch': (30, 3, 12), 'lab': (30, -4, 9), 'tap': (57, -4, 24), 'barrel': (60, -4, 24),
    'stash': (64, -4, 24), 'wardrobe': (15, 18, 2), 'attic_room': (12, 24, 4),
    'attic_ladder': (40, 18, 33), 'cupola': (30, 36, 20),
}

SECRETS_WORLD = '''All the original secrets are here, turned with the house. The positions are world coordinates
(block positions, Y = the block itself). Every mechanism was operated by a player on the test server.

1. **The library bookcase door (north wing, ground floor).** Go to the librarian's desk in the
   two-storey library. A floor lever beside the desk is at {lever}. The lever is **ON** while
   the passage is closed; flip it **OFF**. A sticky piston pulls the bookcase at {bookcase} down
   into the floor. The top half of the doorway is a small "Kebab" painting over a wall sign, so you
   can walk straight through it. Flip the lever ON again to close the passage.
2. **Lord Ashgrove's secret study.** Behind the bookcase are a desk, a skull, and a chest at {journal}
   holding the *Journal of Lord Ashgrove*, a written book of clues to the other secrets.
3. **The hidden vault.** A narrow stair in the secret study, railed with fences and starting near
   {stair}, leads down into the foundations to a dusty antechamber. The iron vault door at
   {vault_door} opens with the lever beside it at {vault_lever} (there is one on the inside too).
   Inside, behind an obsidian shell: gold, iron, emerald and diamond blocks, and treasure chests.
4. **The escape tunnel.** A trapdoor in the vault floor at {hatch} opens onto a ladder down to a
   long tunnel (for example {tunnel}). It runs **west** under the rear lawn to a hidden bunk-room at
   {hideout} with a bed, supplies and a sign. From there a ladder climbs up to the **dry well** in
   the rear (west) garden at {well}. From outside, the well is also a secret way in.
5. **The Wanderer's door.** In the grand foyer, walk behind the central staircase, under the landing.
   On the **north** side hangs a tall "Wanderer" painting at {wanderer} that hides a doorway. Walk
   through it into a hidden cubby at {cubby}. A trapdoor in the cubby floor at {lab_hatch} leads down
   a ladder into **Lord Ashgrove's laboratory** at {lab}. It has a working lamp panel (flip the lever),
   repeater and comparator lines, note blocks, and a command block that "whirs" when you step on its
   pressure plate.
6. **The loose barrel (wine cellar, south side of the basement).** A floor lever "tap" stands between
   the racks at {tap}. Flip it OFF and the barrel in the barrel wall at {barrel} sinks into the floor.
   Walk through the small "Plant" painting above it into the **smuggler's stash**, dug outside the
   foundations at {stash}. It holds diamonds, emeralds, gold, a music disc and contraband.
7. **The wardrobe (top floor, north wing).** In the Old Bedroom, the tall wardrobe has a door at
   {wardrobe}. Inside, a ladder climbs through the ceiling into a **sealed room in the roof** at
   {attic_room}: a single chair facing a portrait, candles, dead flowers, and a chest with a
   golden apple and a music disc. There is no other way in.
8. **Up top.** A ladder in the top floor's south hall at {attic_ladder} leads into the big central attic
   (trunks, sheeted furniture, a dress form). From there a second ladder climbs into the glass
   cupola at {cupola} and out onto the roof walk.
'''

TESTING = '''The mansion was **not** rebuilt by hand. The same generator (`tools/`) that made the command-block
edition was changed:

* `tools/rotation.py` turns the whole design a quarter turn clockwise and moves it to the requested spot:
  world X = -225 - local Z, Y = 73 + local Y, world Z = 224 + local X. This puts the front-door plane on
  X = -251 and the house's mirror axis on Z = 267.0. Every coordinate of every `/fill`, `/setblock`,
  `/clone` (including the destination corner) and `/summon` is written out as an **absolute world
  coordinate**. None of the {n} build commands uses `~`.
* All directional metadata is turned as well: stairs, doors, trapdoors, torches, levers (wall, floor
  and ceiling), buttons, ladders, wall signs, banners, chests, furnaces, dispensers, droppers, hoppers,
  pistons, piston heads, repeaters, comparators, beds, fence gates, pumpkins, anvils, tripwire hooks,
  logs and hay (axis), quartz pillars, standing signs and banners, floor skulls (their `Rot` tag),
  vines, rails and huge mushrooms. Paintings and item frames get the turned `Facing`, and armor stands
  get their yaw +90 degrees. Each table was checked against the generator's own direction helpers
  (which the command-block edition had already proven on real servers), and four turns must give back
  the original value.
* `tools/console_build.py` packs the commands into {total} console lines of at most {limit} characters
  (the longest is {longest}). This is about half the old 32,700 and far below any hard limit. Each build
  line is a single `/summon` with absolute coordinates: a falling command block, redstone block and
  activator rail land on the pad, and a pile of command-block minecarts runs one build command each. This
  is the same 1.8 minecart method the command-block edition used and tested (groups of 6 carts, safe on
  1.8.0 too). The old 32,700-character pastes were **not** wrapped inside another command.
* Static checks (`tools/console_check.py`) replay the exact command text with an independent interpreter
  and compare the result with the turned design, block by block. They also run the original design checks
  on the turned model: supports for everything that hangs on something, fire safety, walking to all 87
  room probes and back again, and 0 dark spawnable spots indoors. Finally they check the position, the
  orientation and the installer's safety distances.
* Real servers (`tools/console_test.py`): vanilla server jars, a real player connection (a small headless
  1.8 client, `tools/mcbot.py`) standing at {sx} {sy} {sz} with `view-distance={vd}` and the default 60 s
  tick watchdog, and world spawn far away. Only that player keeps the site loaded. Every
  `console_NN.txt` was typed into the server console exactly as shipped, and the test waited for the
  documented reply each time. Afterwards the saved world was compared block by block with the design.
  The design checks were run again on the blocks **read back from the world**. The paintings, armor
  stands and item frame, and the removal of all installer blocks and entities, were checked. Then the
  player **clicked** every lever, door, hatch, gate, chest, furnace, crafting table, bed and so on.

The results of those runs:
'''

LIMITS = '''## 9. Known limitations

* **Console line length depends on your host.** Each line is one command of up to about 16,000 characters.
  The vanilla 1.8 server console reads lines of any length; that was tested. Your hosting dashboard's
  web console could **not** be tested, and some panels may limit how much you can paste at once. If your
  panel cuts long input short, the server answers `Data tag parsing failed` and **nothing** is built,
  so a cut line can never build half a stage. Pasting in the normal order, the first long line is
  `console_05.txt` (15,869 characters). If that one answers `Data tag parsing failed`, your panel
  shortens long input. In that case the fallback is the command-block edition
  (`commands/`, `MANSION.md`). Consoles that work through **RCON** only accept about 1,400 characters per
  command and cannot be used.
* **Tested on vanilla servers only** (1.8.9 and 1.8.0). Spigot and Paper 1.8 run the same vanilla commands,
  and the installer is kept within 4 blocks of where you stand so that Spigot's entity-activation range
  does not pause it. They were not tested.
* **Chunk loading needs a player.** 1.8 has no `/forceload`. Stay at the stand point with the server's
  view-distance at 6 or more until the final message.
* **Terrain.** The site is levelled at Y 72. Rock below Y 69 stays, so caves under the lawn stay as they
  are (the basement and tunnel have their own solid walls). Water or lava that touches the edge of the site
  can flow into it after the clearing{terrain_note}. On a steep hillside the land just outside the site
  is left as a cut face.
* **Game-made differences.** Grass that ends up under a wall slowly turns to dirt in vanilla, which is
  invisible. Redstone dust power levels and leaf "check decay" bits are set by the game. The attic armor
  stand settles half a block onto its slab floor.
* The rest of the known behaviour is the same as the command-block edition. For example, the secret
  bookcase and barrel doors are held closed by levers that are ON, as designed.
'''


def main():
    b, st, lines = write_files()
    plans = render_images(b)
    doc = render_doc(b, st, lines, plans)
    with open(os.path.join(ROOT, 'CONSOLE_INSTALL.md'), 'w') as fh:
        fh.write(doc)
    print('wrote %d console lines to %s, CONSOLE_INSTALL.md (%d chars), %d images'
          % (len(lines), OUTDIR, len(doc), len(plans) + 1))


if __name__ == '__main__':
    main()
