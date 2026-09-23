"""Additive refurbishment of the frozen console design, in mansion coordinates.

Every write is a one-cell, old-material-filtered fill. Inventories, mechanisms,
lights, furniture and openings are never bulk-filled or replayed from the base.
"""
import copy
from collections import Counter

import console_build as CB
import rotation as R
from blockids import BLOCK_IDS as B, ID_NAMES
from engine import stairs, N, S, E, W
from mansion_base import X0, Z0, BOTH
from mansion_base import MB


class Decorator:
    def __init__(self, b):
        self.b = b
        self.edits = []

    def put(self, x, y, z, name, meta=0, allow=('air',)):
        old, om = self.b.G(x, y, z)
        if ID_NAMES[old] not in allow or (old, om) == (B[name], meta):
            return False
        assert (x + X0, y, z + Z0) not in self.b.te
        self.b.F(x, y, z, x, y, z, name, meta,
                 mode='replace', rblock=ID_NAMES[old], rmeta=om)
        self.edits.append((x, y, z, ID_NAMES[old], om, name, meta, self.b.section))
        return True

    def line(self, x1, y1, z1, x2, y2, z2, name, meta=0, allow=('air',)):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.put(x, y, z, name, meta, allow)


def roof(d):
    d.b.section = 'stone-edged gables and roof cresting'
    # Trace the existing roof pitch. No new roof volume or attic intrusion.
    for t in BOTH:
        for z in (-1, 41):
            left, right = ((7, 18) if z == -1 else (-1, 18))
            for k in range((right - left + 1) // 2):
                for x, high in ((left + k, E), (right - k, W)):
                    d.put(t.x(x), 24 + k, z, 'stone_brick_stairs', stairs(t.d(high)),
                          ('dark_oak_stairs',))
        # The long ridges get restrained iron cresting, anchored in full stone.
        for z in (10, 20, 29, 39):
            for x in (8, 9):
                d.put(t.x(x), 34, z, 'double_stone_slab', 5, ('stone_slab',))
                d.put(t.x(x), 35, z, 'iron_bars')
        for z in range(11, 39):
            d.put(t.x(8), 34, z, 'double_stone_slab', 5, ('stone_slab',))
            d.put(t.x(8), 35, z, 'iron_bars')
        # Side dormer bargeboards and pale faces.
        for z0 in (15, 30):
            for k in (0, 1):
                for z, high in ((z0 + k, S), (z0 + 5 - k, N)):
                    d.put(t.x(-1), 28 + k, z, 'stone_brick_stairs', stairs(high),
                          ('dark_oak_stairs',))
    for k in range(9):
        for x, high in ((22 + k, E), (39 - k, W)):
            d.put(x, 24 + k, -1, 'stone_brick_stairs', stairs(high), ('dark_oak_stairs',))
    # Smaller spire finial; the tall observatory stays within the original Y118 limit.
    for x, y in ((3, 45), (58, 39)):
        d.put(x, y, 3, 'cobblestone_wall')
    for x in (29, 32):
        for z in (18, 21):
            d.put(x, 39, z, 'stone_brick_stairs', stairs(S if z == 18 else N),
                  ('dark_oak_stairs',))


def facades(d):
    d.b.section = 'pale tower panels and recessed facade stonework'
    for t in BOTH:
        # Stone bands and chiseled quoins remain; warm panels echo the reference.
        for y in range(3, 30):
            if y in (8, 9, 15, 16, 22, 23):
                continue
            for a in range(0, 7):
                d.put(t.x(a), y, -1, 'sandstone', 2, ('stonebrick',))
                d.put(t.x(-1), y, a, 'sandstone', 2, ('stonebrick',))
        for y in (3, 10, 17, 24):
            for a in (0, 6):
                d.put(t.x(a), y, -2, 'stone_brick_stairs', stairs(S, True))
        # Stone framing beneath the front sub-gable, not over its glass.
        for x in (8, 17):
            d.line(t.x(x), 24, 0, t.x(x), 26, 0, 'log2', 1,
                   ('stained_hardened_clay',))
        # Planters: only two selected bays per side, leaving chimney and secrets alone.
        for z in (12, 32):
            for zz in (z, z + 1):
                d.put(t.x(-1), 9, zz, 'wooden_slab', 13)
                d.put(t.x(-1), 10, zz, 'leaves', 4)
        for x in (10, 14):
            for xx in (x, x + 1):
                d.put(t.x(xx), 16, -1, 'stone_brick_stairs', stairs(S, True))
                d.put(t.x(xx), 17, -1, 'leaves', 4)
        # Rear attic gables: visible timber kingpost and crossbeam.
        for y in range(24, 32):
            for x in (6, 11):
                d.put(t.x(x), y, 40, 'log2', 1, ('stained_hardened_clay',))
        d.line(t.x(3), 25, 40, t.x(14), 25, 40, 'log2', 5,
               ('stained_hardened_clay',))
    for x1, x2 in ((24, 27), (34, 37)):
        d.line(x1, 10, 0, x2, 22, 0, 'sandstone', 2, ('stonebrick',))
    # Surround the rose window with pale masonry; leave its colored glass intact.
    d.line(27, 24, 0, 34, 30, 0, 'sandstone', 2, ('stonebrick',))
    d.b.section = 'entrance and balcony stone accents'
    for x in (24, 28, 33, 37):
        for side in (-1, 1):
            d.put(x + side, 8, -5, 'quartz_stairs', stairs(E if side < 0 else W, True))
    # Permanent, nonflammable lamp caps over existing porch light positions.
    for x in (30, 31):
        d.put(x, 8, -3, 'stone_slab', 15)


def grounds(d):
    d.b.section = 'connected stone garden walks'
    def path(x1, z1, x2, z2):
        for x in range(x1, x2 + 1):
            for z in range(z1, z2 + 1):
                # Only exposed lawn/gravel: never change well, crops or foundations.
                if d.b.G(x, 0, z)[0] != 0:
                    continue
                edge = x in (x1, x2) or z in (z1, z2)
                d.put(x, -1, z, 'stonebrick' if edge else 'stone', 0 if edge else 6,
                      ('grass', 'gravel'))
    path(20, -21, 41, -9)
    path(28, -24, 33, -20)
    path(-4, -10, 23, -8)
    path(38, -10, 65, -8)
    path(-4, -8, -2, 48)
    path(63, -8, 65, 28)
    path(62, 28, 63, 47)
    path(-4, 46, 19, 48)
    path(42, 46, 63, 48)
    path(28, 50, 33, 57)
    d.b.section = 'parterre planting and clipped garden borders'
    # Replace the loud solid flower carpets with white/pink borders and red centers.
    for x1, x2 in ((2, 16), (45, 59)):
        for x in range(x1 + 1, x2):
            for z in range(-18, -12):
                col = 8 if x in (x1 + 1, x2 - 1) or z in (-18, -13) else (4 if (x + z) % 3 else 0)
                d.put(x, 0, z, 'red_flower', col, ('red_flower', 'yellow_flower'))
    for x1, x2 in ((20, 27), (34, 41)):
        for x in range(x1 + 1, x2):
            for z in range(51, 57):
                d.put(x, 0, z, 'red_flower', 8 if (x + z) % 3 else 4, ('red_flower',))
    for x in (-5, 66):
        for z in range(-7, 44):
            if 29 <= z <= 41 and x == 66:
                continue  # kitchen garden
            if d.b.G(x, -1, z)[0] == B['grass']:
                d.put(x, 0, z, 'leaves', 4)
    # Small foundation beds stop below the windows and outside the front steps.
    for x1, x2 in ((0, 16), (45, 61)):
        for x in range(x1, x2 + 1):
            for z in (-4, -3):
                if d.b.G(x, -1, z)[0] == B['grass']:
                    d.put(x, 0, z, 'leaves' if z == -3 else 'red_flower', 4 if z == -3 else 8)
    d.b.section = 'capped estate lamps and fountain masonry'
    for x, z, h in ((22,-21,2),(39,-21,2),(22,-10,2),(39,-10,2),
                    (27,-23,3),(34,-23,3),(19,47,2),(42,47,2)):
        d.put(x, 0, z, 'stonebrick', 3, ('dark_oak_fence',))
        d.put(x, h + 1, z, 'stone_slab', 5)
    for x in (26, 35):
        for z in (-18, -13):
            d.put(x, 0, z, 'stonebrick', 3, ('stonebrick',))
    # Tie the gazebo into the same dark roof / pale stone estate palette.
    for x in range(51, 60):
        for z in range(46, 55):
            for y in (3, 4, 5):
                d.put(x, y, z, 'wooden_slab', 5, ('wooden_slab',))


# Explicit room footprints. These surface treatments keep all furnishings and air.
# name, x1,z1,x2,z2, floor y, ceiling y, wood accent, rug accent
ROOMS = [
    ('study',8,1,16,9,2,9,5,13), ('map room',0,0,6,6,2,9,5,11),
    ('salon',23,20,38,35,2,9,5,13), ('dining',45,16,60,29,2,9,5,14),
    ('drawing room',45,1,53,9,2,9,5,6), ('breakfast nook',55,0,61,6,2,9,5,4),
    ('library',1,16,16,33,2,16,5,13), ('conservatory',24,37,37,42,2,9,2,13),
    ('blue guest room',8,1,16,9,10,16,5,11), ('tower sitting room',0,0,6,6,10,16,5,11),
    ('scholar room',1,36,16,39,10,16,5,13), ('lounge',23,20,38,25,10,16,5,14),
    ('master bedroom',25,27,36,35,10,16,5,11), ('master bath',18,27,23,35,10,16,2,3),
    ('closet',38,27,43,35,10,16,5,6), ('rose guest room',45,1,53,9,10,16,5,6),
    ('tower reading room',55,0,61,6,10,16,5,13), ('green guest room',50,16,60,29,10,16,5,13),
    ('billiards',45,31,60,39,10,16,5,13),
    ('portrait gallery',18,4,43,8,17,23,5,14), ('music room',23,10,38,28,17,23,5,11),
    ('trophy room',23,30,38,35,17,23,5,14), ('old bedroom',8,1,16,9,17,23,5,12),
    ('nursery',1,16,16,24,17,23,2,3), ('lumber room',1,26,16,33,17,23,5,12),
    ('governess room',45,1,53,9,17,23,5,6), ('servants rooms',45,16,60,29,17,23,5,12),
    ('laundry',45,31,60,39,17,23,2,3), ('observatory',0,0,6,6,30,36,5,11),
]


def interiors(d):
    for name, x1,z1,x2,z2, yf,yc, wood,rug in ROOMS:
        d.b.section = 'interior: ' + name
        for x in range(x1, x2 + 1):
            for z in range(z1, z2 + 1):
                edge = x in (x1, x2) or z in (z1, z2)
                # Marquetry border and four inset corners, with no change in collision.
                if edge:
                    d.put(x,yf,z,'planks',wood,('planks',))
                elif x in (x1+1,x2-1) and z in (z1+1,z2-1):
                    d.put(x,yf,z,'planks',2,('planks',))
                # Coffered ceilings retain all original glowstone and slab heights.
                if edge or ((x-x1) % 5 == 0) or ((z-z1) % 5 == 0):
                    old, meta = d.b.G(x,yc,z)
                    if old == B['planks']:
                        d.put(x,yc,z,'planks',wood,('planks',))
                    elif old == B['wooden_slab']:
                        d.put(x,yc,z,'wooden_slab',(meta & 8) | wood,('wooden_slab',))
                # Sparse woven motifs within existing floor rugs only.
                if (x-x1) % 4 == 2 and (z-z1) % 4 == 2:
                    d.put(x,yf+1,z,'carpet',4 if rug in (11,13,14) else 0,('carpet',))
    d.b.section = 'hall runners and landing inlays'
    for y in (3,11,18):
        for t in BOTH:
            for z in range(5,35,5):
                for x in (19,20):
                    d.put(t.x(x),y,z,'carpet',4,('carpet',))
            for x in range(9,16,3):
                d.put(t.x(x),y,12,'carpet',0,('carpet',))
    d.b.section = 'basement workshop and storage aisle stone inlays'
    for x1,z1,x2,z2 in ((18,18,43,28),(45,31,60,39),(1,1,16,13),(1,16,16,26)):
        for x in range(x1,x2+1):
            for z in range(z1,z2+1):
                if x in (x1,x2) or z in (z1,z2):
                    d.put(x,-5,z,'stone',6,('stonebrick','cobblestone'))
                elif (x-x1)%5==2 and (z-z1)%5==2:
                    d.put(x,-5,z,'stonebrick',3,('stonebrick','cobblestone'))
    # A bright, flush work surface border guides the player to the existing 20-furnace bank.
    for x in range(46,56):
        d.put(x,-5,37,'stone',6,('stonebrick',))
    d.b.section = 'foyer threshold and stair landing detailing'
    for x in (24,37):
        for z in range(4,18):
            d.put(x,2,z,'stone',6,('quartz_block','stained_hardened_clay'))
    for x in (28,33):
        for z in (13,17):
            d.put(x,7,z,'carpet',4,('carpet',))


def assemble():
    b = CB.assemble()
    base = copy.deepcopy(b)
    b.xf = R
    start = len(b.cmds)
    d = Decorator(b)
    roof(d)
    facades(d)
    grounds(d)
    interiors(d)
    # Coalesce collinear writes with identical preconditions. Last edit wins in
    # the model; each emitted fill still tests the ORIGINAL decorative material.
    cells = {}
    for x,y,z,old,om,new,nm,section in d.edits:
        key = (x,y,z)
        if key in cells:
            old,om = cells[key][:2]
        cells[key] = (old,om,new,nm,section)
    groups = {}
    for (x,y,z),(old,om,new,nm,section) in cells.items():
        groups.setdefault((section,y,old,om,new,nm), set()).add((x,z))
    patch = MB(terrain=False)
    patch.xf = R
    for (section,y,old,om,new,nm),points in groups.items():
        if (old,om) == (new,nm):
            continue
        while points:
            x,z = min(points)
            # Choose the larger of an X-first and Z-first filled rectangle.
            candidates = []
            for axis in (0,1):
                xe,ze = x,z
                if axis == 0:
                    while (xe+1,z) in points: xe += 1
                    while all((xx,ze+1) in points for xx in range(x,xe+1)): ze += 1
                else:
                    while (x,ze+1) in points: ze += 1
                    while all((xe+1,zz) in points for zz in range(z,ze+1)): xe += 1
                candidates.append(((xe-x+1)*(ze-z+1),xe,ze))
            _,xe,ze = max(candidates)
            patch.section = section
            patch.F(x,y,z,xe,y,ze,new,nm,mode='replace',rblock=old,rmeta=om)
            points.difference_update((xx,zz) for xx in range(x,xe+1) for zz in range(z,ze+1))
    b.cmds = base.cmds + patch.cmds
    b.astra_start = start
    b.astra_edits = d.edits
    print('Astra: %d conditional block edits in %d sections' %
          (len(d.edits),len(Counter(e[-1] for e in d.edits))))
    return base, b
