"""Assemble the full mansion build, pack it into pastes and render previews."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mansion_base import MB, X0, Z0          # noqa: E402
import exterior                              # noqa: E402
import facades                               # noqa: E402
import interior_f1 as f1                     # noqa: E402
import interior_f2 as f2                     # noqa: E402
import interior_f3 as f3                     # noqa: E402
import basement                              # noqa: E402
import landscape                             # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'out')


def assemble():
    b = MB()
    exterior.site(b)
    exterior.basement_box(b)
    exterior.shell(b)
    exterior.floors(b)
    exterior.roofs_all(b)
    facades.wing_sides(b)
    facades.wing_fronts(b)
    facades.wing_rears(b)
    facades.central_faces(b)
    facades.pavilion(b)
    facades.portico(b)
    facades.rear_room(b)
    facades.towers(b)
    facades.dormers(b)
    facades.roof_deck(b)
    facades.central_chimneys(b)
    # ---- basement (before F1: the secret-study stair is cut into it) ----
    basement.structure(b)
    # ---- floor 1 ----
    f1.partitions(b)
    f1.foyer(b)
    f1.salon(b)
    f1.halls(b)
    f1.study(b)
    f1.corridors(b)
    f1.library(b)
    f1.library_secret_door(b)
    f1.secret_study(b)
    f1.east_front(b)
    f1.dining(b)
    f1.kitchen(b)
    f1.back_stairs(b)
    f1.doors(b)
    f1.lights(b)
    f1.foyer_late(b)
    basement.late(b)
    # ---- floor 2 ----
    f2.partitions(b)
    f2.west_rooms(b)
    f2.central_rooms(b)
    f2.master_suite(b)
    f2.east_rooms(b)
    f2.doors(b)
    # ---- floor 3 + towers ----
    f3.partitions(b)
    f3.west_stair(b)
    f3.central(b)
    f3.west_wing(b)
    f3.tower_west(b)
    f3.east_wing(b)
    f3.doors(b)
    f3.secret_attic(b)
    f3.central_attic(b)
    light_pass(b, 'B', -10, 0, box=(X0 - 1, -10, Z0 - 1, X0 + 68, 0, Z0 + 57))
    light_pass(b, 'F1', 3, 8)
    light_pass(b, 'F2', 11, 15)
    light_pass(b, 'F3', 18, 35, max_new=110)
    finish(b)
    landscape.all_(b)
    return b


def light_pass(b, name, y1, y2, box=None, max_new=80):
    """Automatic hidden/decorative lighting for any remaining dark spawnable spots."""
    import validate as V
    b.section = 'auto lighting ' + name

    def place(kind, pos, meta):
        x, y, z = pos
        if kind == 'glow':
            b.setblock(x, y, z, 'glowstone')
        else:
            b.setblock(x, y, z, 'torch', meta)
    box = box or (X0 - 1, y1, Z0 - 1, X0 + 62, y2, Z0 + 43)
    added = V.auto_light(b, box, place, max_new=max_new)
    import collections
    print('  light pass %s: %s' % (name, dict(collections.Counter(k for k, p in added))))
    return added


def finish(b):
    """Things that must be placed last: water, fire, hanging entities."""
    b.section = 'finishing: water, fire, paintings'
    for (x1, y1, z1, x2, y2, z2) in b.water:
        b.F(x1, y1, z1, x2, y2, z2, 'water')
    for (x, y, z) in b.fires:
        b.S(x, y, z, 'fire')
    for p in b.late_paintings:
        b.P(*p)
    for f in b.late_frames:
        b.FRAME(*f)


def render_views(b, tag='preview'):
    import render
    from engine import SX0, SY0, SZ0
    os.makedirs(OUT, exist_ok=True)
    # crop to mansion + yard
    x1, x2 = X0 - 12 - SX0, X0 + 74 - SX0
    z1, z2 = Z0 - 26 - SZ0, Z0 + 60 - SZ0
    y1, y2 = -1 - SY0, 55 - SY0
    ids = b.ids[x1:x2, y1:y2, z1:z2]
    me = b.meta[x1:x2, y1:y2, z1:z2]
    render.iso(ids, me, os.path.join(OUT, tag + '_nw.png'), scale=5, view='NW')
    render.iso(ids, me, os.path.join(OUT, tag + '_se.png'), scale=5, view='SE')
    for side in 'NSWE':
        render.elevation(ids, me, os.path.join(OUT, tag + '_elev_%s.png' % side), side=side, scale=6)


if __name__ == '__main__':
    b = assemble()
    print('commands:', len(b.cmds), 'chars:', sum(len(c.text) for c in b.cmds))
    render_views(b)


def render_plans(b, levels=None, tag='plan'):
    import render
    from engine import SX0, SY0, SZ0
    os.makedirs(OUT, exist_ok=True)
    x1, x2 = X0 - 3 - SX0, X0 + 64 - SX0
    z1, z2 = Z0 - 9 - SZ0, Z0 + 46 - SZ0
    levels = levels or {'B': -5, 'F1': 2, 'F2': 10, 'F3': 17, 'ATTIC': 23}
    for name, yf in levels.items():
        ya, yb = yf - SY0, yf + 1 - SY0
        ids = b.ids[x1:x2, :, z1:z2]
        me = b.meta[x1:x2, :, z1:z2]
        render.plan(ids, me, (ya, yb), os.path.join(OUT, '%s_%s.png' % (tag, name)), scale=10,
                    grid=(X0 - 3, Z0 - 9))
