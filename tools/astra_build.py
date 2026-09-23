"""Astra-only stage packer; reuses the proven 1.8 console installer geometry."""
import hashlib
import json
from pathlib import Path

import console_build as CB
from engine import esc

ROOT = Path(__file__).resolve().parents[1]
COSTS = ROOT / 'tools/astra_costs.json'
LIMIT = 15000
COST_CAP = 3.0


def key(text):
    return hashlib.sha256(text.encode()).hexdigest()


def message(stage, total):
    tail = 'Astra refurbishment complete.' if stage == total else 'Next: paste astra_%02d.txt' % (stage+1)
    return 'Astra Stage %d/%d complete. %s' % (stage,total,tail)


def footer(stage,total):
    # Unlike the base builder, do not kill dropped items across an occupied estate.
    clean = 'fill ~-1 ~-3 ~ ~1 ~ ~ air' if stage == total else 'fill ~-1 ~-2 ~ ~1 ~ ~ air'
    cmds = ['kill @e[type=Item,r=6]']
    if stage == total:
        cmds.append('gamerule commandBlockOutput true')
    for off,cmd in (('~2 ~-1 ~','gamerule logAdminCommands true'),
                    ('~1 ~-2 ~','say '+message(stage,total)),('~1 ~ ~',clean)):
        cmds.append('setblock %s command_block 0 replace {Command:"%s",CustomName:Astra}' % (off,esc(cmd)))
    return cmds + ['setblock ~1 ~-1 ~ redstone_block','kill @e[type=MinecartCommandBlock,r=1]']


def pack(b, require_costs=True):
    cmds = b.cmds[b.astra_start:]
    costs = json.loads(COSTS.read_text())['costs'] if COSTS.exists() else {}
    missing = [c.text for c in cmds if key(c.text) not in costs]
    if require_costs and missing:
        raise ValueError('%d unprofiled Astra commands; run astra_test.py SERVER flat --profile' % len(missing))
    spans = []
    i = 0
    while i < len(cmds):
        j,work = i,0
        while j < len(cmds):
            cost = costs.get(key(cmds[j].text),0.05)
            body = CB.HEADER + [c.text for c in cmds[i:j+1]] + footer(999,999)
            if j > i and (work+cost > COST_CAP or len(CB.paste_for(body)) > LIMIT):
                break
            if len(CB.paste_for(body)) > LIMIT or cost > COST_CAP:
                raise ValueError('Single Astra command exceeds stage budget: '+cmds[j].text)
            work += cost
            j += 1
        spans.append((i,j,work))
        i = j
    total = len(spans)+1
    out = [(CB.setup_command(), [], 0.0)]
    for k,(a,z,work) in enumerate(spans,2):
        commands = [c.text for c in cmds[a:z]]
        text = CB.paste_for(CB.HEADER+commands+footer(k,total))
        assert len(text)<=LIMIT
        out.append((text,commands,work))
    return out


def cleanup_commands():
    x,y,z = CB.PAD
    return ['kill @e[type=MinecartCommandBlock,x=%d,y=%d,z=%d,r=6]' % (x,y+3,z),
            'kill @e[type=FallingSand,x=%d,y=%d,z=%d,r=6]' % (x,y+3,z),
            'fill %d %d %d %d %d %d air' % (x,y,z,x+2,y+3,z),
            'gamerule commandBlockOutput true','gamerule logAdminCommands true']
