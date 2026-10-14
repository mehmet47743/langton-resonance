"""
LANGTON'IN KARINCASI - REZONANS MANZARASI
==========================================
Yazar: Mehmet
Tarih: 14.10.2026
75 ampirik yasa, 4 teorem.
En yuksek rekor: 176696 (Sierpinski bs=12, B=500)
"""

import numpy as np

DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]


def simulate(grid, ax, ay, d, n_states=2, max_steps=300_000, patch=40):
    """Langton simulasyonu. XOR flip + alternating turn."""
    grid = grid.copy()
    h = patch // 2
    H, W = grid.shape
    seen = {}
    for step in range(max_steps):
        state = int(grid[ay, ax])
        turn = +1 if state % 2 == 0 else -1
        d = (d + turn) & 3
        grid[ay, ax] = np.uint8(state ^ 1)
        ax += DX[d]
        ay += DY[d]
        if ax < h or ax >= W - h or ay < h or ay >= H - h:
            return ('oob', -1)
        p = grid[ay - h:ay + h, ax - h:ax + h].tobytes()
        if p in seen:
            return ('cycle', step - seen[p])
        seen[p] = step
    return ('timeout', -1)


def make_gradient(L=600, c=300, n_states=5):
    g = np.zeros((L, L), dtype=np.uint8)
    n_levels = n_states * 3
    for level in range(n_levels):
        t = level / max(1, n_levels - 1)
        y = c + 55 - int(t * 110)
        color = level % n_states
        for x_off in [-30, -10, 10, 30]:
            x = c + x_off
            w = 4 if t < 0.5 else 2
            for dx in range(-w, w + 1):
                if 0 <= y < L and 0 <= x + dx < L:
                    g[y, x + dx] = color
    return g


def make_sierpinski(L=600, n_states=5, bs=4):
    g = np.zeros((L, L), dtype=np.uint8)
    for y in range(L):
        for x in range(L):
            xx, yy = x, y
            hole = False
            while xx > 0 or yy > 0:
                if (xx % 3 == 1) and (yy % 3 == 1):
                    hole = True
                    break
                xx //= 3
                yy //= 3
            if not hole:
                g[y, x] = (x // bs + y // bs) % n_states
    return g


if __name__ == "__main__":
    print("LANGTON REZONANS MANZARASI")
    print("=" * 50)
    g = make_sierpinski(500, 5, 12)
    t, p = simulate(g, 250, 250, 1, n_states=5, max_steps=300_000)
    print(f"Rekor test: {t}, periyot={p}")
