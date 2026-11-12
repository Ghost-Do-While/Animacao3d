import bpy, sys, json
D = bpy.data; s = bpy.context.scene
out = {
    'versao': bpy.app.version_string, 'objetos': len(D.objects), 'frames': [s.frame_start, s.frame_end],
    'snow_presente': 'RIG-Snow' in D.objects, 'claudio_rig': 'RIG_Claudio' in D.objects, 'marcos_rig': 'RIG_Marcos' in D.objects, 'miguel_rig': 'RIG_Miguel' in D.objects,
    'cenas': [x.name for x in D.scenes], 'cameras': [m.name + ':' + (m.camera.name if m.camera else '-') for m in s.timeline_markers],
    'imagens_sequencia': [(i.name, i.filepath) for i in D.images if i.source == 'SEQUENCE'],
    'texto': [t.name for t in D.texts],
}
json.dump(out, open(sys.argv[-1], 'w'), indent=1)
