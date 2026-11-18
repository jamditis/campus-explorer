# UNIFY #53 (ws147): source found by ray probe on the loaded main (pass147.out): every probe ray from
# WS143_CAM_eye_forecourt_from_N_aisle hit Leaf_TulipPoplar cards of T_RedMaple_L1_0158 at z ~131.7, i.e. ~1.8 m over the N aisle
# (ground ~129.9) 2 m from the camera. The "flat orange patches / yellow wedge on the lawn" were low autumn leaf cards seen edge-on,
# not a ground object (so pre-existing in ws141). A tree over a drive/walk is limbed up for clearance (>= ~2.5 m over walks, more over
# drives): remove this tree's leaf faces whose highest vertex is below ground+2.6 m. Bark untouched. Clearance value UNVERIFIED.
import bpy, bmesh
o=bpy.data.objects['T_RedMaple_L1_0158']; mw=o.matrix_world
li=[i for i,s in enumerate(o.material_slots) if s.material and s.material.name.startswith('Leaf')]
G=129.9; ZC=G+2.6
bm=bmesh.new(); bm.from_mesh(o.data)
dl=[f for f in bm.faces if f.material_index in li and max((mw@v.co).z for v in f.verts)<ZC]
tot=sum(1 for f in bm.faces if f.material_index in li)
bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update()
print("FIX53_LEAF_FACES_DEL",len(dl),"of",tot,"ZC",ZC, "mods",[m.type for m in o.modifiers], "users",o.data.users)
