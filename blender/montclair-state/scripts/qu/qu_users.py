import bpy
m=bpy.data.materials['QP_Richardson_glass_bronze_dark_UNVERIFIED']
print('GLASS users',[o.name for o in bpy.data.objects if any(s.material==m for s in o.material_slots)])
P=m.node_tree.nodes['Principled BSDF']; print({k:(tuple(P.inputs[k].default_value) if hasattr(P.inputs[k].default_value,'__len__') else P.inputs[k].default_value) for k in ['Base Color','Metallic','Roughness','Transmission Weight','Alpha']})
for n in ['QP_CAM_eye_richardson_from_SE','QP_CAM_eye_richardson_from_W','QP_CAM_oblique_richardson_from_S','QQ_CAM_closeup_richardson_SW_entrance']:
    o=bpy.data.objects.get(n); print(n, o and tuple(round(c,2) for c in o.location), o and tuple(round(c,2) for c in o.rotation_euler), o and o.data.lens)
exec(open('scripts/qt/qt_sig.py').read())
