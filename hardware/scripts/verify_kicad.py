import sexpdata, json, sys, re, html
from sexpdata import Symbol
fn = sys.argv[1]
tree = sexpdata.loads(open(fn, encoding="utf-8").read())
def key(x): return x[0].value() if isinstance(x, list) and x and isinstance(x[0], Symbol) else None
def find(lst, k): return [x for x in lst if key(x) == k]
def one(lst, k): r = find(lst, k); return r[0] if r else None
libs = {}
for sym in one(tree, "lib_symbols")[1:]:
    name = sym[1]; pins = {}
    for sub in find(sym, "symbol"):
        for p in find(sub, "pin"):
            at = one(p, "at"); num = one(p, "number")[1]
            pins[num] = (float(at[1]), float(at[2]))
    libs[name] = pins
R = lambda v: round(v, 2)
parent = {}
def fnd(a):
    while parent.setdefault(a, a) != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
def uni(a, b): parent[fnd(a)] = fnd(b)
pinpts = {}
for s in find(tree, "symbol"):
    lib = one(s, "lib_id")[1]; at = one(s, "at"); X, Y, rot = float(at[1]), float(at[2]), int(at[3])
    assert rot == 0
    ref = [p[2] for p in find(s, "property") if p[1] == "Reference"][0]
    for num, (px, py) in libs[lib].items():
        pt = ("P", R(X + px), R(Y - py))
        pinpts[f"{ref}.{num}"] = pt
        uni(("pin", ref, num), pt)
for w in find(tree, "wire"):
    a, b = one(w, "pts")[1:3]
    uni(("P", R(float(a[1])), R(float(a[2]))), ("P", R(float(b[1])), R(float(b[2]))))
for l in find(tree, "label"):
    at = one(l, "at"); uni(("P", R(float(at[1])), R(float(at[2]))), ("NET", l[1]))
ncpts = {("P", R(float(one(n, "at")[1])), R(float(one(n, "at")[2]))) for n in find(tree, "no_connect")}
# duplicate pin locations would short parts together
from collections import Counter
dup = [k for k, c in Counter(pinpts.values()).items() if c > 1]
groups = {}
for k in list(parent):
    if k[0] == "pin": groups.setdefault(fnd(k), []).append(f"{k[1]}.{k[2]}")
names = {}
for k in list(parent):
    if k[0] == "NET": names.setdefault(fnd(k), set()).add(k[1])
got = {}
unnamed = []
for root, members in groups.items():
    nm = names.get(root)
    if not nm:
        unnamed.append(members); continue
    assert len(nm) == 1, ("merged nets", nm)
    got[next(iter(nm))] = sorted(members)
want = {k: sorted(v) for k, v in json.load(open(fn + ".intended.json"))["nets"].items()}
bad = [n for n in set(want) | set(got) if want.get(n) != got.get(n)]
nc_unnamed = [m for m in unnamed if not (len(m) == 1 and pinpts[m[0]] in ncpts)]
print("duplicate pin locations:", dup)
print("nets intended", len(want), "found", len(got), "mismatches:", bad)
print("pins with no net and no no-connect flag:", nc_unnamed)
print("single-pin nets:", [n for n, v in got.items() if len(v) < 2])
