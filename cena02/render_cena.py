# Renderiza a cena principal (Scene) em Blender de FUNDO, 1 frame por processo (a Radeon integrada derruba o Blender com varios frames),
# com retomada e deteccao de frame preto/curto. Espera o render do telejornal terminar (RAM/GPU nao aguentam dois ao mesmo tempo).
# grava em render/cena02_frames/f_0001.png ...  Frames "prontos": 1-242 (Snow ainda no carro).
# Uso: python -u cena02/render_cena.py [--aguardar-pid PID] [--inicio 1 --fim 242]
import subprocess, os, sys, time, datetime, threading, ctypes, argparse

ap = argparse.ArgumentParser()
ap.add_argument("--aguardar-pid", type=int, default=0)
ap.add_argument("--inicio", type=int, default=1); ap.add_argument("--fim", type=int, default=242)
args = ap.parse_args()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND = os.path.join(ROOT, "cena02_v2.blend")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUT = os.path.join(ROOT, "render", "cena02_frames")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(OUT, "render_log.txt")
TIMEOUT_S = 15 * 60      # vigia por frame (normal: 4-7 min)
MIN_BYTES = 60_000      # PNG 1080p normal tem centenas de KB; preto/vazio fica bem abaixo

def log(msg):
    line = f"[{datetime.datetime.now():%d/%m %H:%M:%S}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf8") as f: f.write(line + "\n")

def keep_awake():      # mantem o Windows acordado enquanto este processo viver (nao altera configuracoes)
    k = ctypes.windll.kernel32
    k.SetThreadExecutionState(0x80000001)
    while True: time.sleep(60)
threading.Thread(target=keep_awake, daemon=True).start()

def pid_vivo(pid):
    out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
    return str(pid) in out

def done(n):
    p = os.path.join(OUT, f"f_{n:04d}.png")
    return os.path.exists(p) and os.path.getsize(p) > MIN_BYTES

if args.aguardar_pid:
    log(f"aguardando o render do telejornal (PID {args.aguardar_pid}) terminar...")
    while pid_vivo(args.aguardar_pid): time.sleep(30)
    log("telejornal terminou; iniciando a cena principal")

todos = list(range(args.inicio, args.fim + 1))
chave = todos[::24]                                   # primeiro um frame a cada 24 (para conferir cedo), depois o resto
ordem = chave + [n for n in todos if n not in chave]
t0 = time.time()
for passada in range(1, 4):
    faltam = [n for n in ordem if not done(n)]
    if not faltam: break
    log(f"passada {passada}: faltam {len(faltam)} frames")
    for n in faltam:
        t1 = time.time()
        p = os.path.join(OUT, f"f_{n:04d}.png")
        if os.path.exists(p) and os.path.getsize(p) <= MIN_BYTES: os.remove(p)
        proc = subprocess.Popen([BLENDER, "-b", BLEND, "-S", "Scene", "-o", os.path.join(OUT, "f_####"), "-F", "PNG", "-f", str(n)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            rc = proc.wait(timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:      # vigia: Blender congelado -> encerra e segue (o frame volta na proxima passada)
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
            rc = "TRAVADO > %d min, encerrado" % (TIMEOUT_S // 60)
        log(f"frame {n}: {'ok' if done(n) else 'FALHOU/preto (codigo %s)' % rc} em {time.time() - t1:.0f}s")
faltam = [n for n in todos if not done(n)]
log(f"FIM: {len(todos) - len(faltam)}/{len(todos)} frames em {(time.time() - t0) / 3600:.1f} h; faltando: {faltam}")
