"""Exterior: site preparation, structural shell, floors, roofs, facade details."""
from mansion_base import *   # noqa: F401,F403
from mansion_base import MB, T, ID, MI, BOTH, AXIS
from engine import stairs, trapdoor, torch, wallmount, N, S, E, W
import roofs

# Main volumes (outer wall lines, inclusive): (x1, x2, z1, z2)
WING = (0, 17, 0, 40)          # west wing; east wing is its mirror (44..61)
CENTRAL = (17, 44, 3, 36)
PAV = (23, 38, 0, 3)
TOWER = (-1, 7, -1, 7)          # NW tower; NE is mirror (54..62)
REAR = (23, 38, 36, 43)
SITE = (-10, 72, -24, 58)


def site(b):
    b.section = 'site'
    x1, x2, z1, z2 = SITE
    b.F(x1, 0, z1, x2, 45, z2, 'air')           # clears hills/trees up to the spire tops
    b.F(x1, -4, z1, x2, -2, z2, 'dirt')
    b.F(x1, -1, z1, x2, -1, z2, 'grass')


def basement_box(b):
    b.section = 'basement shell'
    # tower foundations (solid), then the hollow basement box
    for t in BOTH:
        b.tF(t, -1, -5, -1, 7, 1, 7, *WALL)
    b.F(0, -5, 0, 61, 1, 40, *WALL, mode='hollow')
    # basement ceiling (under F1) : spruce planks
    b.F(1, 1, 1, 60, 1, 39, *SPRUCE_PLANK)
    # rough cobblestone course at ground level outside + plinth
    for t in BOTH:
        b.tF(t, -1, 0, -1, 7, 0, -1, 'cobblestone')
        b.tF(t, -1, 0, -1, -1, 0, 7, 'cobblestone')


def shell(b):
    b.section = 'shell'
    for t in BOTH:
        b.tF(t, 0, 2, 0, 17, 23, 40, *WALL, mode='hollow')
    b.F(17, 2, 3, 44, 23, 36, *WALL, mode='hollow')
    b.F(23, 2, 0, 38, 23, 3, *WALL, mode='hollow')
    b.F(23, 2, 36, 38, 9, 43, *WALL, mode='hollow')
    # base course of cobblestone at y=0 all round the basement box (visible plinth)
    b.F(0, 0, 0, 61, 0, 0, 'cobblestone')
    b.F(0, 0, 40, 61, 0, 40, 'cobblestone')
    b.F(0, 0, 0, 0, 0, 40, 'cobblestone')
    b.F(61, 0, 0, 61, 0, 40, 'cobblestone')
    # upper floors of wings + central block are half-timbered plaster
    for t in BOTH:
        b.tF(t, 0, 10, 0, 17, 23, 40, *PLASTER, mode='replace', rblock='stonebrick')
    b.F(18, 10, 3, 43, 23, 36, *PLASTER, mode='replace', rblock='stonebrick')
    # towers (stone, taller) - built after so their walls cut through the wings
    for t in BOTH:
        top = 36 if not t.m else 30
        b.tF(t, -1, 2, -1, 7, top, 7, *WALL, mode='hollow')


def floors(b):
    """Ceiling (spruce) + floor (oak) layers for F2, F3 and attic floor."""
    b.section = 'floors'
    regions = [(1, 16, 1, 39), (45, 60, 1, 39), (18, 43, 4, 35), (24, 37, 1, 3)]
    for (x1, x2, z1, z2) in regions:
        b.F(x1, F1_CEIL, z1, x2, F1_CEIL, z2, *SPRUCE_PLANK)
        b.F(x1, F2, z1, x2, F2, z2, *OAK_PLANK)
        b.F(x1, F2_CEIL, z1, x2, F2_CEIL, z2, *SPRUCE_PLANK)
        b.F(x1, F3, z1, x2, F3, z2, *OAK_PLANK)
        # bottom-half slabs: look like a normal ceiling from below, and the attic
        # above becomes spawn-proof (mobs cannot spawn on bottom slabs)
        b.F(x1, F3_CEIL, z1, x2, F3_CEIL, z2, 'wooden_slab', 1)
    for t in BOTH:
        # tower rooms (7x7) : F2, F3, F4 floors
        for yc, yf in ((F1_CEIL, F2), (F2_CEIL, F3), (F3_CEIL, EAVE)):
            b.tF(t, 0, yc, 0, 6, yc, 6, *SPRUCE_PLANK)
            b.tF(t, 0, yf, 0, 6, yf, 6, *OAK_PLANK)
    # NW tower observatory floor
    b.F(0, 30, 0, 6, 30, 6, *DO_PLANK)
    # rear garden room ceiling
    b.F(24, F1_CEIL, 37, 37, F1_CEIL, 42, *SPRUCE_PLANK)


def roofs_all(b):
    b.section = 'roofs'
    for t in BOTH:
        x1, x2 = t.xs(-1, 18)
        # main wing roof (ridge N-S) behind the tower
        roofs.gable_z(b, x1, x2, 7, 41, EAVE, gable_walls=[8, 40], wall_blk=PLASTER)
        # front sub-gable beside the tower
        s1, s2 = t.xs(7, 18)
        roofs.gable_z(b, s1, s2, -1, 9, EAVE, gable_walls=[0], wall_blk=PLASTER)
    # central hipped roof with a widow's-walk deck
    top, deck = roofs.hip(b, 16, 45, 2, 37, EAVE, flat_at=11)
    b.deck = deck
    # pavilion front gable (ridge N-S)
    roofs.gable_z(b, 22, 39, -1, 12, EAVE, gable_walls=[0], wall_blk=WALL)
    # tower tops
    for t in BOTH:
        if not t.m:
            # NW tower: observatory level then spire
            roofs.spire(b, -2, 8, -2, 8, 37)
        else:
            a, c = t.xs(-2, 8)
            roofs.spire(b, a, c, -2, 8, 31)
