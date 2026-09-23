"""Pack an ordered list of commands into Minecraft 1.8.x one-command pastes.

Paste format (every stage):

    summon FallingSand ~ ~1 ~ {Block:activator_rail,Time:1,Riding:{
        id:FallingSand,Block:redstone_block,Time:1,Riding:{
        id:FallingSand,Block:command_block,Time:1,
        TileEntityData:{Command:"summon MinecartCommandBlock ~ ~1.6 ~ {PILE}"}}}}

Landing column above the player's command block (P at y=0):
    y+1 stage command block (runs the pile summon when the redstone lands)
    y+2 redstone block
    y+3 powered activator rail   <- all minecarts execute here

PILE = groups of up to G command minecarts riding each other, groups
separated by a Block-less FallingSand that dies on its first tick.  Every
group therefore lands on the rail independently; this was verified to run
every command exactly once, in order, at identical coordinates, on
1.8.0 (where stacked carts ride 0.15 blocks higher per level) and on
1.8.1 - 1.8.9 (where they ride at the same height).

Execution order: groups in string order; inside a group the bottom
(innermost) cart first.  The last command of every pile kills the carts; the
two commands before it drop a self-destructing command block that removes
the landing column one tick later.
"""
from engine import esc, nbt_needs_quotes

G = 6                 # carts per riding group (1.8.0 safe: 0.0625+0.15*5 < 1)
LIMIT = 32700   # 1.8 MC|AdvCdm payload = text + 17 bytes <= 32767, so text <= 32750


def _cart(cmd, inner):
    c = '"%s"' % esc(cmd) if nbt_needs_quotes(cmd) else cmd
    if inner is None:
        return '{id:MinecartCommandBlock,Command:%s}' % c
    return '{id:MinecartCommandBlock,Command:%s,Riding:%s}' % (c, inner)


def pile_nbt(cmds):
    groups = [cmds[k:k + G] for k in range(0, len(cmds), G)]
    node = None
    for gi in range(len(groups) - 1, -1, -1):
        g = groups[gi]
        part = None
        for j, c in enumerate(g):
            if j == 0:
                inner = None if node is None else '{id:FallingSand,Riding:%s}' % node
                part = _cart(c, inner)
            else:
                part = _cart(c, part)
        node = part
    return node


def paste_for(cmds):
    node = pile_nbt(cmds)
    assert node.startswith('{id:MinecartCommandBlock,')
    x = 'summon MinecartCommandBlock ~ ~1.6 ~ {' + node[len('{id:MinecartCommandBlock,'):]
    return ('summon FallingSand ~ ~1 ~ {Block:activator_rail,Time:1,Riding:{id:FallingSand,'
            'Block:redstone_block,Time:1,Riding:{id:FallingSand,Block:command_block,Time:1,'
            'TileEntityData:{Command:"%s"}}}}' % esc(x))


def footer(stage, total, final, message):
    """Commands appended to every stage (after the build commands)."""
    out = []
    out.append('kill @e[type=Item,r=150]')
    if final:
        out.append('gamerule commandBlockOutput true')
    out.append('tellraw @a %s' % message)
    # self-destructing cleanup block: removes stage cb, redstone, rail (and on the
    # final stage the player's command block too) one tick after the carts die.
    # The cleanup block sits at (1,1,0); the column is x 0..1, y 1..3 (0..3 on the
    # final stage, which also removes the player's command block at y=0).
    clean = 'fill ~-1 ~-1 ~ ~ ~2 ~ air' if final else 'fill ~-1 ~ ~ ~ ~2 ~ air'
    out.append('setblock ~1 ~-2 ~ command_block 0 replace {Command:%s}' % clean)
    out.append('setblock ~1 ~-1 ~ redstone_block')
    out.append('kill @e[type=MinecartCommandBlock,r=1]')
    return out


HEADER = ['gamerule commandBlockOutput false']


def pack(cmds, messages):
    """Greedy packing.  `messages(stage, total, final)` -> tellraw JSON."""
    stages = []
    i = 0
    # first pass with a provisional total so footer lengths are realistic
    while i < len(cmds):
        cur = list(HEADER)
        j = i
        while j < len(cmds):
            if max(len(paste_for(cur + [cmds[j]] + footer(99, 99, fin, messages(99, 99, fin))))
                   for fin in (False, True)) > LIMIT:
                break
            cur.append(cmds[j])
            j += 1
        if j == i:
            raise ValueError('single command too long: %r' % cmds[i][:200])
        stages.append((i, j))
        i = j
    total = len(stages)
    pastes = []
    for k, (a, b) in enumerate(stages):
        final = k == total - 1
        body = list(HEADER) + cmds[a:b] + footer(k + 1, total, final, messages(k + 1, total, final))
        p = paste_for(body)
        assert len(p) <= LIMIT, len(p)
        assert all(ord(ch) < 128 for ch in p), 'non-ASCII character in paste %d' % (k + 1)
        pastes.append((p, body))
    return pastes
