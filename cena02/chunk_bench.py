# Compara o render com o chunk loader LIGADO e DESLIGADO: tempo, memoria de pico e numero de objetos visiveis.
# Uso: blender -b cena02_v2.blend -S Scene --python cena02/chunk_bench.py -- SAIDA PCT FRAME on|off
import bpy, sys, os, time, json, ctypes
from ctypes import wintypes
a = sys.argv[sys.argv.index("--") + 1:]
out, pct, frame, mode = a[0], int(a[1]), int(a[2]), a[3]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chunk_loader
sc = bpy.context.scene; sc.render.resolution_percentage = pct
sc["chunk_enabled"] = 1 if mode == "on" else 0
sc.frame_set(frame)
chunk_loader.install()
stats = chunk_loader.apply(sc)
def peak_mb():
    class C(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [(n, ctypes.c_size_t) for n in ("PeakWorkingSetSize", "WorkingSetSize", "QPP", "QP", "QPN", "QN", "Pagefile", "PeakPagefile")]
    c = C(); c.cb = ctypes.sizeof(C)
    ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(c), c.cb)
    return c.PeakWorkingSetSize / 1048576
sc.render.filepath = os.path.join(out, f"bench_{frame}_{mode}.png")
t0 = time.time(); bpy.ops.render.render(write_still=True); dt = time.time() - t0
vis = sum(1 for o in sc.objects if o.type in ('MESH', 'CURVE', 'FONT') and not o.hide_render)
print("BENCH", json.dumps({"frame": frame, "mode": mode, "camera": sc.camera.name, "render_s": round(dt, 1), "pico_MB": round(peak_mb()), "objetos_visiveis": vis, "chunk": stats}))
