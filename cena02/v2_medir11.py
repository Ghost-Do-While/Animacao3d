import bpy
r = bpy.data.objects["RIG-Victoria"]; pb = r.pose.bones
ctl = [b.name for b in pb if not b.name.startswith(("DEF", "ORG", "MCH", "STR", "DSP", "ROOT", "TGT", "AIM", "CTR", "MSTR", "CEN", "IK", "FK", "PRP")) and any(k in b.name for k in ("Lip", "Jaw", "Mouth", "Eyebrow", "Eyelid", "Cheek", "Brow", "Tongue", "Teeth"))]
print("CTL", len(ctl), ctl[:60])
print("JAW", [b.name for b in pb if "Jaw" in b.name][:20])
print("MODES", {b.name: b.rotation_mode for b in pb if b.name in ("Jaw", "Lip_Bot", "Eyelid_Upper.L")})
