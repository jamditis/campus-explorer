# nk background prep: small reusable door-hardware + downlight kit (assets/door_hardware_kit_nk.blend), marked as assets. Sizes typical, UNVERIFIED.
import bpy, bmesh, mathutils
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
def mat(name,c,r,metal=0.0,emit=0.0,trans=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=c; p.inputs['Roughness'].default_value=r; p.inputs['Metallic'].default_value=metal
    if emit: p.inputs['Emission Color'].default_value=c; p.inputs['Emission Strength'].default_value=emit
    if trans: p.inputs['Transmission Weight'].default_value=trans
    return m
alu=mat('KIT_satin_aluminium',(0.55,0.55,0.56,1),0.35,0.9); ss=mat('KIT_satin_stainless',(0.62,0.62,0.63,1),0.3,1.0)
lens=mat('KIT_downlight_lens_warm',(1,0.85,0.66,1),0.4,emit=12); glass=mat('KIT_door_glass_satin',(0.95,0.95,0.94,1),0.11,trans=1.0)
blk=mat('KIT_sensor_black',(0.02,0.02,0.02,1),0.5)
def box(name,dx,dy,dz,m,off=(0,0,0)):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0)
    for v in bm.verts: v.co=mathutils.Vector((v.co.x*dx+off[0],v.co.y*dy+off[1],v.co.z*dz+off[2]))
    bm.to_mesh(me); bm.free(); me.materials.append(m); return me
def obj(name,meshes):
    bm=bmesh.new()
    for me in meshes: bm.from_mesh(me)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for mm in meshes:
        for m in mm.materials:
            if m.name not in [x.name for x in me.materials]: me.materials.append(m)
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o); o.asset_mark(); o.asset_data.description=name+' (nk kit, typical size, UNVERIFIED)'
    return o
obj('KIT_door_closer_surface_arm',[box('b',0.28,0.058,0.07,alu),box('a',0.45,0.02,0.02,alu,(0.12,0,0.06))])
obj('KIT_butt_hinge_4in',[box('h',0.024,0.014,0.11,ss)])
me=bpy.data.meshes.new('c'); bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=24,radius1=0.10,radius2=0.10,depth=0.012); bm.to_mesh(me); bm.free(); me.materials.append(alu)
obj('KIT_downlight_can_trim_200mm',[me])
obj('KIT_door_motion_sensor',[box('s',0.22,0.06,0.05,blk)])
obj('KIT_door_leaf_glass_single_pane',[box('g',0.86,0.02,2.26,glass)])
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/assets/door_hardware_kit_nk.blend'); print('KIT SAVED',len(bpy.data.objects))
