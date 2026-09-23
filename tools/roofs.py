"""Roof prism helpers (hollow, stepped 1:1 roofs built from stair rings)."""
from engine import stairs, N, S, E, W


def gable_z(b, x1, x2, z1, z2, y0, mat='dark_oak_stairs', eave_mat='stone_brick_stairs',
            gable_walls=None, wall_blk=None, cap=('stone_slab', 5), layers=None):
    """Gable roof, ridge along Z.  x1..x2 / z1..z2 include the overhang.

    gable_walls: list of z positions where the triangular end wall is filled
    (only between the stairs, one block inside the roof edge).
    """
    width = x2 - x1 + 1
    n = (width + 1) // 2 if layers is None else layers
    for k in range(n):
        y = y0 + k
        a, c = x1 + k, x2 - k
        if a > c:
            break
        m = eave_mat if (k == 0 and eave_mat) else mat
        if a == c:
            b.F(a, y, z1, a, y, z2, *cap)
            break
        b.F(a, y, z1, a, y, z2, m, stairs(E))
        b.F(c, y, z1, c, y, z2, m, stairs(W))
        if gable_walls and wall_blk and c - a >= 2:
            for gz in gable_walls:
                b.F(a + 1, y, gz, c - 1, y, gz, *wall_blk)
    top = y0 + n - 1
    if cap and width % 2 == 0:
        mid = x1 + width // 2 - 1
        b.F(mid, top + 1, z1, mid + 1, top + 1, z2, *cap)
    return top


def gable_x(b, x1, x2, z1, z2, y0, mat='dark_oak_stairs', eave_mat='stone_brick_stairs',
            gable_walls=None, wall_blk=None, cap=('stone_slab', 5), layers=None):
    """Gable roof, ridge along X.  gable_walls = list of x positions for end walls."""
    width = z2 - z1 + 1
    n = (width + 1) // 2 if layers is None else layers
    for k in range(n):
        y = y0 + k
        a, c = z1 + k, z2 - k
        if a > c:
            break
        m = eave_mat if (k == 0 and eave_mat) else mat
        if a == c:
            b.F(x1, y, a, x2, y, a, *cap)
            break
        b.F(x1, y, a, x2, y, a, m, stairs(S))
        b.F(x1, y, c, x2, y, c, m, stairs(N))
        if gable_walls and wall_blk and c - a >= 2:
            for gx in gable_walls:
                b.F(gx, y, a + 1, gx, y, c - 1, *wall_blk)
    top = y0 + n - 1
    if cap and width % 2 == 0:
        mid = z1 + width // 2 - 1
        b.F(x1, top + 1, mid, x2, top + 1, mid + 1, *cap)
    return top


def hip(b, x1, x2, z1, z2, y0, mat='dark_oak_stairs', eave_mat='stone_brick_stairs',
        flat_at=None, flat_blk=('wooden_slab', 5), max_layers=None):
    """Hipped roof: stair rings shrinking by one each layer.

    If flat_at (a layer index) is given the roof stops there with a flat deck.
    Returns (top_y, deck box or None).
    """
    k = 0
    while True:
        y = y0 + k
        ax, cx, az, cz = x1 + k, x2 - k, z1 + k, z2 - k
        if ax > cx or az > cz:
            return y - 1, None
        if flat_at is not None and k == flat_at:
            b.F(ax, y, az, cx, y, cz, *flat_blk)
            return y, (ax, az, cx, cz)
        if max_layers is not None and k >= max_layers:
            return y - 1, None
        m = eave_mat if (k == 0 and eave_mat) else mat
        if ax == cx or az == cz:
            b.F(ax, y, az, cx, y, cz, 'stone_slab', 5)
            return y, None
        b.F(ax, y, az, cx, y, az, m, stairs(S))
        b.F(ax, y, cz, cx, y, cz, m, stairs(N))
        if cz - az >= 2:
            b.F(ax, y, az + 1, ax, y, cz - 1, m, stairs(E))
            b.F(cx, y, az + 1, cx, y, cz - 1, m, stairs(W))
        k += 1


def spire(b, x1, x2, z1, z2, y0, mat='dark_oak_stairs', body=('planks', 5), steep=True):
    """Square spire: rings of (full block, stairs) giving a 2:1 pitch."""
    k = 0
    y = y0
    while True:
        ax, cx, az, cz = x1 + k, x2 - k, z1 + k, z2 - k
        if ax > cx or az > cz:
            return y
        if ax == cx and az == cz:
            return y
        if steep and k > 0:
            b.F(ax, y, az, cx, y, cz, *body)
            y += 1
        b.F(ax, y, az, cx, y, az, mat, stairs(S))
        b.F(ax, y, cz, cx, y, cz, mat, stairs(N))
        if cz - az >= 2:
            b.F(ax, y, az + 1, ax, y, cz - 1, mat, stairs(E))
            b.F(cx, y, az + 1, cx, y, cz - 1, mat, stairs(W))
        y += 1
        k += 1
