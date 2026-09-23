"""Server-console edition: absolute placement, assembly and packing.

Installation is done entirely from the server console (no leading '/'):

  console_01.txt   setblock <PAD> bedrock            one block high in the sky, east of
                                                     the site: the landing pad
  console_02.txt   summon FallingSand <above PAD> {...}
  ...              each build paste is ONE /summon with absolute coordinates.  It drops a
                   command block + redstone block + activator rail onto the pad; the
                   command block summons a pile of command-block minecarts; each cart runs
                   one ABSOLUTE-coordinate build command.  The last carts remove themselves
                   and leave three command blocks that, one tick later, switch logging back
                   on, report the stage with /say (visible in the console and in chat) and
                   remove the whole column.  The last stage also removes the pad.

Nothing depends on where the console "is", on the player's position or facing, or on
`~` coordinates of the console.  The `~` coordinates that remain are only inside the
installer (relative to its own minecarts, which always sit on the rail above the pad).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine                          # noqa: E402
import rotation as R                   # noqa: E402
from engine import esc, nbt_needs_quotes   # noqa: E402

# ------------------------------------------------------------------ layout --
ENTRANCE = R.ENTRANCE                          # (-251, 73, 267): centre of the front doors, lawn feet level
LOCAL_BOX = (2, -11, 2, 84, 45, 84)            # everything the build writes (local coords, checked)
BUILD_BOX = R.box(*LOCAL_BOX)                  # world (x1,y1,z1,x2,y2,z2)
PAD = (-221, 124, 267)                         # landing pad (bedrock) for the installer
COLUMN = (PAD[0], PAD[1] + 1, PAD[2], PAD[0] + 2, PAD[1] + 3, PAD[2])   # stage cb, redstone, rail + cleanup blocks
STAND = (-225, 73, 267)                        # where the player waits (feet), just east of the site
MIN_VIEW_DISTANCE = 6                          # server.properties view-distance needed at STAND
LIMIT = 16000                                  # max characters per console paste (well below every limit)
COST_CAP = 4.0                                 # max measured server seconds of work per stage (console_costs.json)
SAY_NAME = 'Installer'


def assemble():
    import build
    engine.Build.xf = R
    try:
        b = build.assemble()
    finally:
        engine.Build.xf = None
    return b


# ------------------------------------------------------------------ packing --
G = 6   # carts per riding group (same proven 1.8.0-safe value as the legacy packer)


def _cart(cmd, inner):
    extra = ''
    if isinstance(cmd, tuple):
        cmd, extra = cmd
    c = '"%s"' % esc(cmd) if nbt_needs_quotes(cmd) else cmd
    body = 'id:MinecartCommandBlock,Command:%s%s' % (c, extra)
    if inner is None:
        return '{%s}' % body
    return '{%s,Riding:%s}' % (body, inner)


def pile_nbt(cmds):
    groups = [cmds[k:k + G] for k in range(0, len(cmds), G)]
    node = None
    for gi in range(len(groups) - 1, -1, -1):
        part = None
        for j, c in enumerate(groups[gi]):
            if j == 0:
                part = _cart(c, None if node is None else '{id:FallingSand,Riding:%s}' % node)
            else:
                part = _cart(c, part)
        node = part
    return node


def paste_for(cmds):
    node = pile_nbt(cmds)
    assert node.startswith('{id:MinecartCommandBlock,')
    inner = 'summon MinecartCommandBlock ~ ~1.6 ~ {' + node[len('{id:MinecartCommandBlock,'):]
    x, y, z = PAD
    # x/z without a '.' are block-centred by /summon (+0.5); y 1.5 above the pad like the
    # legacy "~ ~1 ~" from a command block (whose own position is its centre).
    return ('summon FallingSand %d %d.5 %d {Block:activator_rail,Time:1,Riding:{id:FallingSand,'
            'Block:redstone_block,Time:1,Riding:{id:FallingSand,Block:command_block,Time:1,'
            'TileEntityData:{Command:"%s",CustomName:%s}}}}' % (x, y + 1, z, esc(inner), SAY_NAME))


def setup_command():
    return 'setblock %d %d %d bedrock' % PAD


def message(stage, total):
    if stage == total:
        return 'Mansion Console Stage %d/%d complete. Mansion construction complete.' % (stage, total)
    return 'Mansion Console Stage %d/%d complete. Next: paste console_%02d.txt' % (stage, total, stage + 1)


# logging off first, so the second gamerule is already silent
HEADER = ['gamerule logAdminCommands false', 'gamerule commandBlockOutput false']


def footer(stage, total):
    """Carts at the end of every stage, then three command blocks that fire one tick later.

    Rail = (x, r, z).  The carts, still with logAdminCommands off (so the console stays
    quiet), remove dropped items, set up three command blocks around a new redstone block
    at (x+1, r-1, z) and kill every cart.  Placing that redstone block notifies its
    neighbours in the fixed vanilla order west, east, down, up, north, south, so the
    command blocks run next tick in the order EAST, DOWN, UP:
        east  (x+2, r-1): gamerule logAdminCommands true
        down  (x+1, r-2): say <stage message>          -> shows in the console and in chat
        up    (x+1, r  ): fill x..x+2, r-2..r air        -> removes the column, the three
                          command blocks and the redstone (final stage: from r-3 = the pad)
    """
    x1, y1, z1, x2, y2, z2 = BUILD_BOX
    final = stage == total
    out = ['kill @e[type=Item,x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d]' % (x1, y1, z1, x2 - x1, y2 - y1, z2 - z1),
           'kill @e[type=Item,r=6]']
    if final:
        out.append('gamerule commandBlockOutput true')
    clean = 'fill ~-1 ~-3 ~ ~1 ~ ~ air' if final else 'fill ~-1 ~-2 ~ ~1 ~ ~ air'
    for off, cmd in (('~2 ~-1 ~', 'gamerule logAdminCommands true'),
                     ('~1 ~-2 ~', 'say ' + message(stage, total)),
                     ('~1 ~ ~', clean)):
        out.append('setblock %s command_block 0 replace {Command:"%s",CustomName:%s}' % (off, esc(cmd), SAY_NAME))
    out.append('setblock ~1 ~-1 ~ redstone_block')
    out.append('kill @e[type=MinecartCommandBlock,r=1]')
    return out


def load_costs():
    """Measured seconds per command (console_profile.py); unknown commands count as 0."""
    import hashlib
    import json
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'console_costs.json')
    if not os.path.exists(p):
        return lambda text: 0.0
    costs = json.load(open(p))['costs']
    return lambda text: costs.get(hashlib.sha1(text.encode()).hexdigest()[:16], 0.0)


def pack(b, limit=LIMIT, cost_cap=COST_CAP):
    """-> list of (paste_text, body_commands, (first_cmd, end_cmd)) for the build stages.

    A stage ends when the next command would make the console line longer than `limit`
    characters, or would push the stage's measured server work above `cost_cap` seconds
    (a big hollow shell with its lighting updates takes 1-4 s; everything in one stage runs
    within a few ticks, so this bounds how long a stage can freeze the server)."""
    cost = load_costs()
    cmds = [c.text for c in b.cmds]
    sections = [c.section for c in b.cmds]
    # stage boundaries: greedy by size; the site clearing (the heaviest single job,
    # hundreds of thousands of blocks) gets a stage of its own.
    forced = {i for i in range(1, len(cmds)) if (sections[i - 1] == 'site') != (sections[i] == 'site')}
    spans, i = [], 0
    while i < len(cmds):
        cur = list(HEADER)
        j = i
        work = 0.0
        while j < len(cmds):
            if j > i and (j in forced or work + cost(cmds[j]) > cost_cap):
                break
            if max(len(paste_for(cur + [cmds[j]] + footer(t, t))) for t in (98, 99)) > limit:
                break
            cur.append(cmds[j])
            work += cost(cmds[j])
            j += 1
        if j == i:
            raise ValueError('single command too long: %r' % cmds[i][:200])
        spans.append((i, j))
        i = j
    total = len(spans) + 1                      # stage 1 = the setup command
    out = []
    for k, (a, z) in enumerate(spans):
        stage = k + 2
        body = HEADER + cmds[a:z] + footer(stage, total)
        p = paste_for(body)
        assert len(p) <= limit, len(p)
        assert all(32 <= ord(ch) < 127 for ch in p), 'non-printable character in stage %d' % stage
        out.append((p, body, (a, z)))
    return out


def all_pastes(b, limit=LIMIT):
    """Every console line in order: [setup, stage 2, ..., stage N]."""
    return [setup_command()] + [p for p, _, _ in pack(b, limit)]


if __name__ == '__main__':
    b = assemble()
    st = pack(b)
    print('build commands:', len(b.cmds), 'console lines:', len(st) + 1)
    print('sizes:', [len(p) for p, _, _ in st])
