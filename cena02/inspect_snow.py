import bpy, sys, json, traceback
from mathutils import Vector
out = {}
try:
    D = bpy.data
    out['version'] = bpy.app.version_string
    out['scenes'] = [s.name for s in D.scenes]
    out['collections'] = {c.name: [o.name for o in c.objects][:40] for c in D.collections}
    out['objects'] = [(o.name, o.type, [round(x, 2) for x in o.dimensions], o.parent.name if o.parent else None, o.hide_viewport, o.hide_render) for o in D.objects]
    out['texts'] = [t.name for t in D.texts]
    arms = {}
    for o in D.objects:
        if o.type == 'ARMATURE':
            bones = o.data.bones
            arms[o.name] = dict(n=len(bones), roots=[b.name for b in bones if b.parent is None][:20],
                                deform=sum(1 for b in bones if b.use_deform), height=round(max(b.tail_local.z for b in bones), 2),
                                loc=[round(x, 2) for x in o.location], scale=[round(x, 2) for x in o.scale],
                                props=[k for k in o.keys()][:60], collections=[bc.name for bc in o.data.collections_all][:60])
    out['armatures'] = arms
    meshes = {}
    for o in D.objects:
        if o.type == 'MESH':
            sk = o.data.shape_keys
            meshes[o.name] = dict(verts=len(o.data.vertices), mats=[m.name if m else None for m in o.data.materials], nshape=len(sk.key_blocks) if sk else 0,
                                  mods=[(m.type, getattr(m, 'object', None).name if getattr(m, 'object', None) else None) for m in o.modifiers][:6],
                                  vgroups=len(o.vertex_groups))
    out['meshes'] = meshes
    out['actions'] = [(a.name, a.users) for a in D.actions][:20]
    out['images'] = [(i.name, i.filepath, i.source) for i in D.images][:40]
    out['render_engine'] = D.scenes[0].render.engine
    out['fps'] = D.scenes[0].render.fps
    out['unit_scale'] = D.scenes[0].unit_settings.scale_length
except Exception:
    out['err'] = traceback.format_exc()[-1500:]
json.dump(out, open(sys.argv[-1], 'w'), indent=1, default=str)
