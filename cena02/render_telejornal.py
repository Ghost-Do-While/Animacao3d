# Renderiza o telejornal (SCN_Telejornal, 103 frames) com a Victoria em Blender de FUNDO, em lotes pequenos e com retomada.
# - grava em render/telejornal_victoria/tv_0001.png ... (NAO sobrescreve render/telejornal, que a TV do apartamento usa)
# - se o Blender cair (driver da GPU), repete so os frames que faltam (ate 4 passadas)
# Uso: python -u cena02/render_telejornal.py            (retoma de onde parou)
import subprocess, os, sys, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND = os.path.join(ROOT, "cena02_v2.blend")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUT = os.path.join(ROOT, "render", "telejornal_victoria")
FRAMES = range(1, 104)
CHUNK = 6
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(OUT, "render_log.txt")

def log(msg):
    line = f"[{datetime.datetime.now():%H:%M:%S}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf8") as f: f.write(line + "\n")

def done(n):
    p = os.path.join(OUT, f"tv_{n:04d}.png")
    return os.path.exists(p) and os.path.getsize(p) > 1000

def runs(missing):
    """agrupa frames faltantes em trechos consecutivos de no maximo CHUNK"""
    out, cur = [], []
    for n in missing:
        if cur and (n != cur[-1] + 1 or len(cur) >= CHUNK): out.append((cur[0], cur[-1])); cur = []
        cur.append(n)
    if cur: out.append((cur[0], cur[-1]))
    return out

t0 = time.time()
for passada in range(1, 5):
    missing = [n for n in FRAMES if not done(n)]
    if not missing: break
    log(f"passada {passada}: faltam {len(missing)} frames")
    for a, b in runs(missing):
        t1 = time.time()
        cmd = [BLENDER, "-b", BLEND, "-S", "SCN_Telejornal", "-o", os.path.join(OUT, "tv_####"), "-F", "PNG", "-s", str(a), "-e", str(b), "-a"]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        ok = all(done(n) for n in range(a, b + 1))
        log(f"frames {a}-{b}: {'ok' if ok else 'FALHOU (codigo %s)' % r.returncode} em {time.time() - t1:.0f}s")
missing = [n for n in FRAMES if not done(n)]
log(f"FIM: {len(FRAMES) - len(missing)}/{len(FRAMES)} frames em {(time.time() - t0) / 60:.1f} min; faltando: {missing}")
