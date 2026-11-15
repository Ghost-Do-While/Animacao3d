# Reduz as texturas do Snow (Blender Studio, CC-BY) para MAXPX px e as grava em snow_tex/ no projeto.
# Motivo: Radeon integrada (512 MB) -> frame preto com Snow+Rex+Vincent. Rodar com -S Scene.
import bpy, os
MAXPX = int(os.environ.get("MAXPX", "1024"))
base = os.path.dirname(bpy.data.filepath)
dest_dir = os.path.join(base, "snow_tex"); os.makedirs(dest_dir, exist_ok=True)

def shrink_save(src_path, dst_path, px):
    im = bpy.data.images.load(src_path)
    w, h = im.size
    if max(w, h) > px:
        s = px / max(w, h); im.scale(max(1, int(w * s)), max(1, int(h * s)))
    im.filepath_raw = dst_path; im.file_format = 'PNG'; im.save()
    bpy.data.images.remove(im)

done = 0
for img in list(bpy.data.images):
    fp = bpy.path.abspath(img.filepath) if img.filepath else ""
    if "Snow_v4.2" not in fp: continue
    name = os.path.basename(fp)
    if img.source == 'TILED' or "<UDIM>" in fp:
        for t in img.tiles:
            sp = fp.replace("<UDIM>", str(t.number)); dp = os.path.join(dest_dir, name.replace("<UDIM>", str(t.number)))
            if os.path.exists(sp): shrink_save(sp, dp, MAXPX); done += 1
        newp = os.path.join(dest_dir, name)
    else:
        newp = os.path.join(dest_dir, name)
        if os.path.exists(fp): shrink_save(fp, newp, MAXPX); done += 1
    img.filepath = bpy.path.relpath(newp); img.reload()
print("SNOWTEX files", done, "dir", dest_dir)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
