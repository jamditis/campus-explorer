# oh: Schmitt ESE entrance (og) toward the confirmed Schmitt family (env-team photos schmitt_01-03): red-brown door frame,
# warm-lit vestibule instead of a black hole, 2 vertical bronze wall sconces flanking the door (style from photo, positions UNVERIFIED).
# Object-level material slots only (og data untouched). REVERT=1 undoes.
import bpy, os, sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
fr=bpy.data.objects['OG_Schmitt_E_entrance_storefront_frame']; ve=bpy.data.objects['OG_Schmitt_E_entrance_vestibule_dark']
la=bpy.data.objects['OG_Schmitt_E_entrance_landing']; gl=bpy.data.objects['OG_Schmitt_E_entrance_glass']
COL=bpy.data.collections['OH_Schmitt_cams_20261031oh']
for n in ('OH_Schmitt_sconce_L','OH_Schmitt_sconce_R'):
    o=bpy.data.objects.get(n)
    if o: me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
for ob in (fr,ve,gl):
    for s in ob.material_slots:
        if s.link=='OBJECT': s.material=None; s.link='DATA'
for n in ('OH_Schmitt_vestibule_warm_lit_UNVERIFIED','OH_Schmitt_sconce_bronze_glow','OH_Schmitt_door_glass_clear_UNVERIFIED'):
    m=bpy.data.materials.get(n)
    if m and REV: bpy.data.materials.remove(m)
if not REV:
    red=bpy.data.materials['OH_Schmitt_win_frame_red_brown']
    for s in fr.material_slots: s.link='OBJECT'; s.material=red
    vm=bpy.data.materials.get('OH_Schmitt_vestibule_warm_lit_UNVERIFIED') or bpy.data.materials.new('OH_Schmitt_vestibule_warm_lit_UNVERIFIED')
    vm.use_nodes=True; p=vm.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(0.30,0.24,0.18,1)
    p.inputs['Emission Color'].default_value=(1.0,0.72,0.45,1); p.inputs['Emission Strength'].default_value=0.22; p.inputs['Roughness'].default_value=0.7
    for s in ve.material_slots: s.link='OBJECT'; s.material=vm
    gm=bpy.data.materials.get('OH_Schmitt_door_glass_clear_UNVERIFIED') or bpy.data.materials.new('OH_Schmitt_door_glass_clear_UNVERIFIED')
    gm.use_nodes=True; p=gm.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(0.85,0.9,0.9,1)
    p.inputs['Transmission Weight'].default_value=1.0; p.inputs['Roughness'].default_value=0.03; p.inputs['IOR'].default_value=1.5
    for s in gl.material_slots: s.link='OBJECT'; s.material=gm
    sm=bpy.data.materials.get('OH_Schmitt_sconce_bronze_glow') or bpy.data.materials.new('OH_Schmitt_sconce_bronze_glow')
    sm.use_nodes=True; p=sm.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(0.9,0.75,0.5,1)
    p.inputs['Emission Color'].default_value=(1.0,0.78,0.5,1); p.inputs['Emission Strength'].default_value=4.0
    # frame local axes: longest horizontal = along facade, shortest = through wall
    M=fr.matrix_world; bb=[M@Vector(c) for c in fr.bound_box]; cen=sum(bb,Vector())/8
    lb=[la.matrix_world@v.co for v in la.data.vertices]; lc=sum(lb,Vector())/len(lb)
    fv=[M@v.co for v in fr.data.vertices]
    out=Vector(((lc-cen).x,(lc-cen).y,0)).normalized(); along=Vector((-out.y,out.x,0))
    lw=max(v.dot(along) for v in fv)-min(v.dot(along) for v in fv)
    front=max(v.dot(out) for v in fv); cen=cen+out*(front-cen.dot(out)); depth=0.0; zb=min(v.z for v in fv)
    for side,n in ((1,'OH_Schmitt_sconce_R'),(-1,'OH_Schmitt_sconce_L')):
        bpy.ops.mesh.primitive_cube_add(size=1)
        o=bpy.context.active_object; o.name=n; o.data.name=n
        for c in o.users_collection: c.objects.unlink(o)
        COL.objects.link(o)
        p=cen+along*side*(lw/2+0.55)+out*(depth/2+0.02); p.z=zb+2.15
        o.location=p; o.scale=(0.12,0.14,0.62)
        o.rotation_euler=(0,0,Vector((along.x,along.y,0)).to_track_quat('X','Z').to_euler().z)
        o.data.materials.append(sm)
    print('sconces at',[tuple(round(c,2) for c in bpy.data.objects[n].location) for n in ('OH_Schmitt_sconce_L','OH_Schmitt_sconce_R')],'out',tuple(round(c,2) for c in out))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
