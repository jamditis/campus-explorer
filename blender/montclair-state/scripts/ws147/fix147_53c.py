# #53 second cut: leaf cards are large; remove T_RedMaple_L1_0158 leaf faces with ANY vertex below ground+2.6 m (limb-up). Shared mesh (60 users) -> same lowest cards go on all instances (harmless limb-up).
import bpy, bmesh
o=bpy.data.objects['T_RedMaple_L1_0158']; mw=o.matrix_world
li=[i for i,s in enumerate(o.material_slots) if s.material and s.material.name.startswith('Leaf')]
ZC=129.9+2.6
bm=bmesh.new(); bm.from_mesh(o.data)
dl=[f for f in bm.faces if f.material_index in li and min((mw@v.co).z for v in f.verts)<ZC]
tot=sum(1 for f in bm.faces if f.material_index in li)
bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update()
print("FIX53C_LEAF_FACES_DEL",len(dl),"of",tot)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state_ws147c.blend',copy=True); print("SAVED_WS147C")
