# ws150 review fixes on ws150a:
# (1) UNIFY #53 still open after the shared-mesh 2.4 m limb-up: T_RedMaple_L1_0158 stands ~1 m below the N drive aisle (Roads_OSM
#     ~129.4) so its road-side crown still hangs 1.3 m above the aisle edge / in front of the eye camera (full-scene ray probe ws150:
#     162/288 rays on Leaf_TulipPoplar at world z 131.69, 1.9 m from the lens). Design: crown over a drive aisle is raised to vehicle
#     clearance 13.5 ft ~ 4.1 m (common municipal street-tree standard), so give 0158 its own mesh copy and remove leaf cards / outer
#     bark on the aisle side (toward the camera, >0.5 m out from the trunk) below world z 129.4+4.1. Other side of crown untouched.
# (2) UNIFY #54 follow-up: Lot 9 asphalt material is an ortho-2020 drape; where the deleted Footpaths slabs used to cover it the
#     drape shows the old lawn/walk as a green patch. Give the E apron strip (and the WS148 patch) plain 'Asphalt' (= Skyline Way).
import bpy, bmesh
from mathutils import Vector
t=bpy.data.objects['T_RedMaple_L1_0158']
me=t.data.copy(); me.name='Tree_TulipPoplar_LOD1_aisle_raised_T0158_ws150'; t.data=me
mw=t.matrix_world; base=mw.translation.copy(); cam=Vector((-64.5,-160.0)); dirv=(cam-base.xy).normalized()
ZC=129.4+4.1
leaf={i for i,s in enumerate(t.material_slots) if s.material and 'Leaf' in s.material.name}
bm=bmesh.new(); bm.from_mesh(me); kill=[]
for f in bm.faces:
    c=mw@f.calc_center_median(); off=(c.xy-base.xy).dot(dirv)
    if c.z<ZC and off>0.5 and (f.material_index in leaf or (c.xy-base.xy).length>0.8): kill.append(f)
bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(me); bm.free(); me.update()
print("FIX150_53 base",tuple(round(v,2) for v in base),"killed",len(kill),"left",len(me.polygons))
A=bpy.data.materials['Asphalt']
def setmat(o,pred):
    ms=o.data.materials
    if A.name not in [m.name for m in ms if m]: ms.append(A)
    ai=[i for i,m in enumerate(ms) if m and m.name==A.name][0]; n=0
    for p in o.data.polygons:
        c=o.matrix_world@p.center
        if pred(c): p.material_index=ai; n+=1
    print("FIX150_54MAT",o.name[:40],n)
lot=[o for o in bpy.data.objects if o.name.startswith('WS142_Lot9_asphalt')][0]
setmat(lot,lambda c:c.x>-69.3 and -191.0<c.y<-178.5)
for o in bpy.data.objects:
    if o.name.startswith('WS148_Lot9_E_apron'): setmat(o,lambda c:True)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state_ws150b.blend',copy=True)
print("SAVED_WS150B")
