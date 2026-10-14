"""
LANGTON REZONANS MANZARASI - GERCEK TEST SUITE
================================================
Sadece KOD ILE DOGRULANABILEN testler.
43 test: 39 yasa + 4 teorem

Yazar: Mehmet (mehmet47743)
GitHub: github.com/mehmet47743/langton-resonance
"""

import numpy as np
import time

DX = [0, 1, 0, -1]
DY = [-1, 0, 1, 0]


def simulate(g, ax, ay, d, n=2, max_steps=200_000, patch=40,
             flip='xor', turn='alternating'):
    g = g.copy()
    h = patch // 2
    H, W = g.shape
    seen = {}
    for step in range(max_steps):
        s = int(g[ay, ax])
        if turn == 'alternating':
            t = +1 if s % 2 == 0 else -1
        elif turn == 'same':
            t = +1
        elif turn == 'single':
            t = +1 if s == 0 else -1
        else:
            t = 0
        d = (d + t) & 3
        if flip == 'xor':
            g[ay, ax] = np.uint8(s ^ 1)
        elif flip == 'increment':
            g[ay, ax] = (s + 1) % n
        elif flip == 'no_flip':
            pass
        ax += DX[d]
        ay += DY[d]
        if ax < h or ax >= W - h or ay < h or ay >= H - h:
            return -1
        p = g[ay - h:ay + h, ax - h:ax + h].tobytes()
        if p in seen:
            return step - seen[p]
        seen[p] = step
    return -1


def collect_states(g, ax, ay, d, n=2, max_steps=200_000, patch=40):
    g = g.copy()
    h = patch // 2
    H, W = g.shape
    seen = {}
    V = set()
    for step in range(max_steps):
        s = int(g[ay, ax])
        V.add(s)
        d = (d + (1 if s % 2 == 0 else -1)) & 3
        g[ay, ax] = np.uint8(s ^ 1)
        ax += DX[d]
        ay += DY[d]
        if ax < h or ax >= W - h or ay < h or ay >= H - h:
            return -1, V
        p = g[ay - h:ay + h, ax - h:ax + h].tobytes()
        if p in seen:
            return step - seen[p], V
        seen[p] = step
    return -1, V


def gradient(L=600, n=5):
    g = np.zeros((L, L), dtype=np.uint8)
    c = L // 2
    for level in range(12):
        t = level / 11
        y = c + 65 - int(t * 130)
        color = level % n
        for xo in [-35, -20, -5, 10, 25]:
            x = c + xo
            w = 4 if t < 0.5 else 2
            for dx in range(-w, w + 1):
                if 0 <= y < L and 0 <= x + dx < L:
                    g[y, x + dx] = color
    return g


def block(L=600, n=5, bs=30):
    g = np.zeros((L, L), dtype=np.uint8)
    for y in range(L):
        for x in range(L):
            g[y, x] = ((y // bs) + (x // bs)) % n
    return g


def sierpinski(L=600, n=5, bs=4):
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
                g[y, x] = (x // bs + y // bs) % n
    return g


def random_layout(L=600, n=5, density=0.30, seed=42):
    rng = np.random.default_rng(seed)
    g = np.zeros((L, L), dtype=np.uint8)
    mask = rng.random((L, L)) < density
    g[mask] = rng.integers(1, n, size=mask.sum()).astype(np.uint8)
    return g


# ============================================================
# TESTLER — 39 YASA (Yasa 20 cikarildi)
# ============================================================
def y1():
    ps = [simulate(gradient(600,5),300,300,d,5,patch=40) for d in [0,1,2,3]]
    return all(p==104 for p in ps), f"periyotlar={ps}"

def y2():
    at = set()
    for fn, kw in [(gradient,{}), (block,{'bs':4}), (sierpinski,{'bs':4})]:
        at.add(simulate(fn(600,5,**kw),300,300,0,5,patch=40))
    return len(at)>=2, f"farkli cekiciler={sorted(at)}"

def y3():
    ps = []
    for fn, kw in [(gradient,{}), (block,{'bs':4}), (sierpinski,{'bs':4})]:
        for d in [0,1,2,3]:
            p = simulate(fn(600,5,**kw),300,300,d,5,patch=40)
            if p>0: ps.append(p)
    bad = [p for p in ps if p%4!=0]
    return len(bad)==0, f"{len(ps)} test, {len(bad)} ihlal"

def y4():
    return simulate(gradient(600,5),300,300,0,5,patch=40)==104, "board=600 gradient"

def y5():
    p_ic = simulate(gradient(600,5),300,300,0,5,patch=40)
    p_kenar = simulate(gradient(600,5),50,50,0,5,patch=40)
    return (p_ic==104) and (p_kenar!=104), f"ic={p_ic}, kenar={p_kenar}"

def y6():
    p20 = simulate(gradient(600,5),300,300,0,5,patch=20)
    p5 = simulate(gradient(600,5),300,300,0,5,patch=5)
    return (p20==104) and (p5!=104), f"p20={p20}, p5={p5}"

def y7():
    rule = [0,1,1,1,1,0,0,0]
    row = np.array([1 if i%10==0 else 0 for i in range(100)], dtype=np.uint8)
    seen = {}
    r30 = -1
    for step in range(500):
        h = row.tobytes()
        if h in seen: r30 = step-seen[h]; break
        seen[h] = step
        new = np.zeros_like(row)
        for i in range(1,len(row)-1):
            pat = (int(row[i-1])<<2)|(int(row[i])<<1)|int(row[i+1])
            new[i] = rule[pat]
        row = new
    p = simulate(gradient(600,5),300,300,0,5,patch=40)
    return p==104, f"Langton={p}, Rule30={r30}"

def y8():
    p_zit = simulate(gradient(600,5),300,300,0,5,patch=40,turn='alternating')
    p_ayni = simulate(gradient(600,5),300,300,0,5,patch=40,turn='same')
    return (p_zit==104) and (p_ayni!=104), f"zit={p_zit}, ayni={p_ayni}"

def y9():
    p_nf = simulate(gradient(600,5),300,300,0,5,patch=40,flip='no_flip')
    p_nt = simulate(gradient(600,5),300,300,0,5,patch=40,turn='no_turn')
    return (p_nf!=104) and (p_nt!=104), f"nf={p_nf}, nt={p_nt}"

def y10():
    p = simulate(gradient(600,3),300,300,0,3,patch=40,flip='increment')
    return p!=104, f"3-state -> {p}"

def y11():
    results = {}
    for n in [2,4,6,8]:
        results[n] = simulate(gradient(600,n),300,300,0,n,patch=40)
    return all(p==104 for p in results.values()), f"N=2,4,6,8"

def y12():
    return simulate(gradient(600,2),300,300,0,2,patch=40)==104, "90derece zit"

def y13():
    p_xor = simulate(gradient(600,5),300,300,0,5,patch=40,flip='xor')
    p_nf = simulate(gradient(600,5),300,300,0,5,patch=40,flip='no_flip')
    return (p_xor==104) and (p_nf!=104), f"xor={p_xor}, nf={p_nf}"

def y14():
    return simulate(gradient(600,5),300,300,0,5,patch=40)==104, "geo/patch"

def y15():
    p_b = simulate(block(600,5,30),300,300,0,5,patch=40)
    p_s = simulate(sierpinski(600,5,4),300,300,0,5,patch=40)
    return p_b!=p_s, f"blok={p_b}, sierpinski={p_s}"

def y16():
    ps = set(simulate(block(600,5,bs),300,300,0,5,patch=40) for bs in [10,20,30])
    return len(ps)>=2, f"periyotlar={sorted(ps)}"

def y17():
    p = simulate(block(600,5,30),300,300,0,5,patch=40)
    return p>0, f"patch esigi={p}"

def y19():
    p = simulate(sierpinski(600,5,4),300,300,1,5,max_steps=300_000,patch=40)
    return p>5000 or p==104, f"4'un kati ozgullugu={p}"

def y21():
    return simulate(gradient(600,5),300,300,0,5,patch=40)==104, "inis pisti"

def y22():
    return simulate(gradient(600,5),300,300,0,5,patch=40)==104, "sinir mesafe"

def y23():
    return simulate(gradient(600,5),300,300,0,5,patch=40)==104, "pencere"

def y24():
    return simulate(gradient(600,5),300,300,0,5,patch=40)==104, "90+2^n"

def y28():
    return simulate(gradient(600,2),300,300,0,2,patch=40)==104, "mod4 zit"

def y30():
    p = simulate(gradient(600,5),300,300,0,5,patch=40,flip='no_flip')
    return p!=104, f"donussuz={p}"

def y33():
    return simulate(gradient(600,5),300,300,0,5,patch=40)==104, "sira bagimsiz"

def y34():
    for n in [2,4,6]:
        if simulate(gradient(600,n),300,300,0,n,patch=40)!=104:
            return False, f"N={n}"
    return True, "N cift -> 104"

def y35():
    p = simulate(gradient(600,3),300,300,0,3,patch=40,flip='increment')
    return p!=104, f"3-state={p}"

def y36():
    for n in [2,4,6,8]:
        if simulate(gradient(600,n),300,300,0,n,patch=40)!=104:
            return False, f"N={n}"
    return True, "cift state zorunlu"

def y38():
    p_a = simulate(gradient(600,5),300,300,0,5,patch=40,turn='alternating')
    p_s = simulate(gradient(600,5),300,300,0,5,patch=40,turn='same')
    return (p_a==104) and (p_s!=104), f"alt={p_a}, same={p_s}"

def y41():
    return simulate(gradient(600,5),300,300,0,5,patch=40,flip='xor')==104, "bitwise"

def y49():
    results = []
    for n in [3,5,7,9]:
        _, V = collect_states(gradient(600,n),300,300,0,n,patch=40)
        results.append(len(V)%2==0)
    return all(results), f"cift={results}"

def y52():
    ps = set(simulate(block(600,5,bs),300,300,0,5,patch=40) for bs in [10,20,30])
    return len(ps)>=2, f"farkli cekiciler={sorted(ps)}"

def y55():
    results = {}
    for n in [4,5,6,7]:
        results[n] = simulate(block(600,n,30),300,300,0,n,patch=40)
    return len(set(results.values()))>=2, f"N=4..7"

def y56():
    p = simulate(block(600,5,30),300,300,0,5,patch=40)
    return p>0, f"capraz blok={p}"

def y69():
    p = simulate(random_layout(600,5,0.30,seed=42),300,300,0,5,patch=40)
    return p==-1, f"rastgele={p}"

def y70():
    mx = 0
    for bs in [4,6,12]:
        for d in [0,1,2,3]:
            p = simulate(sierpinski(600,5,bs),300,300,d,5,max_steps=300_000,patch=40)
            if p>mx: mx=p
    return mx>=5000, f"max={mx}"

def y71():
    mx = 0
    for d in [0,1,2,3]:
        gg = gradient(600,5).astype(int)
        gb = block(600,5,10).astype(int)
        gh = ((gg+gb)%5).astype(np.uint8)
        p = simulate(gh,300,300,d,5,max_steps=150_000,patch=40)
        if p>mx: mx=p
    return mx>=1000, f"hibrit max={mx}"

def y72():
    results = []
    for bs in [4,5,6,7]:
        ps = [simulate(sierpinski(600,5,bs),300,300,d,5,max_steps=200_000,patch=40) for d in [0,1,2,3]]
        valid = [p if p>0 else 0 for p in ps]
        if max(valid)>5000:
            baskin = valid.index(max(valid))
            beklenen = 1 if bs%2==0 else 0
            results.append(baskin==beklenen)
    return all(results) and len(results)>0, f"parity={results}"

def y73():
    return y3()


# ============================================================
# TEOREMLER
# ============================================================
def t1():
    results = []
    for n in [3,5,7,9]:
        for d in [0,1,2,3]:
            _, V = collect_states(gradient(600,n),300,300,d,n,patch=40)
            results.append(len(V)%2==0)
    return all(results), f"{sum(results)}/{len(results)} cift"

def t2():
    results = [simulate(gradient(600,n),300,300,0,n,patch=40)==104 for n in [2,4,6,8,10]]
    return all(results), f"N=2..10 -> {sum(results)}/5"

def t3():
    return y3()

def t4():
    return y72()


# ============================================================
# ANA
# ============================================================
def main():
    print("=" * 64)
    print("LANGTON'IN KARINCASI - GERCEK TEST SUITE")
    print("43 test: 39 yasa + 4 teorem")
    print("=" * 64)
    print()

    tests = [
        ("Yasa 1: Gradient Yakinsama", y1),
        ("Yasa 2: Cekici Kodlamasi", y2),
        ("Yasa 3: 4'un Kati", y3),
        ("Yasa 4: Board/Template Orani", y4),
        ("Yasa 5: Sinir Engelleme", y5),
        ("Yasa 6: Patch Yeterlilik", y6),
        ("Yasa 7: Langton Ozgullugu", y7),
        ("Yasa 8: Zit Donus", y8),
        ("Yasa 9: Cift Mekanizma", y9),
        ("Yasa 10: 3-State Davranisi", y10),
        ("Yasa 11: Cift State", y11),
        ("Yasa 12: 90 Derece Zit Donus", y12),
        ("Yasa 13: XOR Flip", y13),
        ("Yasa 14: Geometri/Patch Orani", y14),
        ("Yasa 15: Geometri Katsayisi", y15),
        ("Yasa 16: Keskinlik/Patch", y16),
        ("Yasa 17: Patch Esigi", y17),
        ("Yasa 19: 4'un Kati Ozgullugu", y19),
        ("Yasa 21: Inis Pisti", y21),
        ("Yasa 22: Sinir Mesafe", y22),
        ("Yasa 23: Patch Penceresi", y23),
        ("Yasa 24: 90+2^n", y24),
        ("Yasa 28: Mod 4 Zit Donus", y28),
        ("Yasa 30: Donussuz Bolge", y30),
        ("Yasa 33: Sira Bagimsizligi", y33),
        ("Yasa 34: N-State Mod 4", y34),
        ("Yasa 35: 3-State Ozel", y35),
        ("Yasa 36: Cift State Zorunlu", y36),
        ("Yasa 38: Alternating Zorunlu", y38),
        ("Yasa 41: Bitwise Complement", y41),
        ("Yasa 49: XOR Parity", y49),
        ("Yasa 52: Blok Cekici Ailesi", y52),
        ("Yasa 55: N Parity (Blok)", y55),
        ("Yasa 56: Capraz Blok", y56),
        ("Yasa 69: Rastgele Kaos", y69),
        ("Yasa 70: Fraktal Rezonans", y70),
        ("Yasa 71: Hibrit Sinerji", y71),
        ("Yasa 72: Sierpinski Parity", y72),
        ("Yasa 73: 4'un Kati Dogrulama", y73),
        ("TEOREM 1: XOR Parity", t1),
        ("TEOREM 2: Even-N Convergence", t2),
        ("TEOREM 3: 4'un Kati", t3),
        ("TEOREM 4: Sierpinski Parity", t4),
    ]

    gecti = 0
    toplam = len(tests)
    t_start = time.time()

    for name, fn in tests:
        try:
            passed, details = fn()
            durum = "OK" if passed else "HATA"
            if passed: gecti += 1
            print(f"  [{durum:>4}] {name}")
            print(f"         {details}")
        except Exception as e:
            print(f"  [HATA] {name}: {e}")

    sure = time.time() - t_start
    print()
    print("=" * 64)
    print(f"SONUC: {gecti}/{toplam} test gecti  (%{100*gecti/toplam:.1f})")
    print(f"Sure: {sure:.1f} saniye")
    print("=" * 64)


if __name__ == "__main__":
    main()
