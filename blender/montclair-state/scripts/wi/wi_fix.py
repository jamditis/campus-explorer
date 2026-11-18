"""wi: Bohn W-door pad/walk concrete match + expansion joint.
- pad material TJ_door_frame (door-frame paint!) -> walk concrete QT_walk_concrete_joints_UNVERIFIED
- walk 1132693523 trimmed so it stops at the pad W edge (was lying 3 cm proud on the pad for 1.2 m)
- 3 cm dark sealant expansion joint between walk end and pad
"""
import bpy, bmesh, json, os
ROOT='/workspace/nj-scenes/montclair-state'; os.chdir(ROOT)
SAVE=os.environ.get('SAVE')=='1'
pad=bpy.data.objects['WG_Bohn_W_door_landing_slab_UNVERIFIED']
walk=bpy.data.objects['WD_walk_1132693523_UNVERIFIED']
qt=bpy.data.materials['QT_walk_concrete_joints_UNVERIFIED']
rep={}
rep['pad_old_mat']=pad.data.materials[0].name
pb=pad.data.materials[0].node_tree.nodes['Principled BSDF']
rep['pad_old_color']=list(pb.inputs['Base Color'].default_value)
pad.data.materials[0]=qt
pad['wi_obj']=1; pad['wi_old_mat']=rep['pad_old_mat']
PADX=213.9; PADTOP=134.46
END=213.88; ENDZ=134.465
assert abs(walk.location.length)<1e-6
bm=bmesh.new(); bm.from_mesh(walk.data)
dele=[v for v in bm.verts if v.co.x>213.95]
rep['walk_deleted']=len(dele)
bmesh.ops.delete(bm,geom=dele,context='VERTS')
moved=0
for v in bm.verts:
    if v.co.x>213.6:
        v.co.x=END; v.co.z=ENDZ; moved+=1
rep['walk_moved']=moved
ys=[v.co.y for v in bm.verts if abs(v.co.x-END)<1e-4]
rep['end_y']=[min(ys),max(ys)]
bm.to_mesh(walk.data); bm.free(); walk.data.update()
walk['wi_obj']=1
# joint
y0,y1=rep['end_y']
m=bpy.data.materials.get('WI_expansion_joint_sealant_UNVERIFIED') or bpy.data.materials.new('WI_expansion_joint_sealant_UNVERIFIED')
m.use_nodes=True
b=m.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(0.035,0.033,0.03,1); b.inputs['Roughness'].default_value=0.75
me=bpy.data.meshes.new('WI_joint')
bm=bmesh.new()
x0,x1,z0,z1=213.875,213.905,134.30,134.462
vv=[bm.verts.new((x,y,z)) for x in (x0,x1) for y in (y0-0.01,y1+0.01) for z in (z0,z1)]
bmesh.ops.convex_hull(bm,input=vv)
bm.to_mesh(me); bm.free()
me.materials.append(m)
j=bpy.data.objects.new('WI_Bohn_W_door_expansion_joint_UNVERIFIED',me)
col=bpy.data.collections.get('WG_Bohn_W_door_landing_UNVERIFIED')
(col or bpy.context.scene.collection).objects.link(j)
j['wi_obj']=1
j.visible_shadow=False
rep['joint']=[x0,x1,y0,y1,z0,z1]
rep['nobj']=len(bpy.data.objects)
json.dump(rep,open('data/wi/fix_report.json','w'),indent=1)
print('REP',rep)
if SAVE:
    bpy.ops.wm.save_mainfile(compress=True)
    print('SAVED')
