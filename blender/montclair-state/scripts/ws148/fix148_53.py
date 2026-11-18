# UNIFY #53: the orange shapes / yellow wedge in WS143_CAM_eye_forecourt_from_N_aisle are Leaf_TulipPoplar cards
# (and a bare limb) of T_RedMaple_L1_0158 hanging 1.0-1.7 m above its base, 1.2-2 m in front of the lens (ws148 partial-scene
# ray probe: 150/2304 rays on leaf face 2984 at local z 1.41). Design: campus trees over walks/aisles are crown-raised to
# >= 8 ft (2.4 m) clearance (ANSI A300 pruning practice / municipal sidewalk codes), so limb up the shared LOD1 mesh:
# delete leaf cards with centre z < 2.4 m and outer branch bark (radial > 0.8 m from the trunk axis) below 2.4 m.
import bpy, bmesh
t=bpy.data.objects['T_RedMaple_L1_0158']; me=t.data
users=[o.name for o in bpy.data.objects if o.data==me]
leaf={i for i,s in enumerate(t.material_slots) if s.material and 'Leaf' in s.material.name}
bm=bmesh.new(); bm.from_mesh(me)
kl=[f for f in bm.faces if f.material_index in leaf and f.calc_center_median().z<2.4]
kb=[f for f in bm.faces if f.material_index not in leaf and f.calc_center_median().z<2.4 and f.calc_center_median().xy.length>0.8]
bmesh.ops.delete(bm,geom=kl+kb,context='FACES'); bm.to_mesh(me); bm.free(); me.update()
print("FIX53 mesh",me.name,"users",len(users),"leaf_del",len(kl),"bark_del",len(kb))
