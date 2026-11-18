# ot (Oct 31 2026 ~9:40 PM ET): os 'Next' follow-ups, ALL UNVERIFIED.
# (A) base course lifted from tar-dark toward mid-grey cast concrete (new material OT_..., OS material kept with a fake user for REVERT).
# (B) base-course bands re-seated on the LiDAR DTM: every band vertex z = DTM(x,y) + (-0.22 bottom | +0.42 top) instead of skirt-bottom-based
#     grade, so neighbouring segment ends meet at the same height (softens the stepped joints at CELS corners); original z kept in point attr ot_z0.
# (C) 'Calcia under-canopy black' was not a canopy: the 4 km context skirt (Context_skirt_3DEP_ortho_4km) overlaps the LiDAR DTM in a strip
#     y~220-248 (and a few edge cells) and floats up to ~9.7 m above it, so its underside read as a black roof. A removable GN modifier
#     (OT_skirt_under_LiDAR) pushes any skirt point that has the DTM below it to at most DTM-0.30 m. Skirt mesh data NOT edited.
# REVERT=1 undoes all three.
import bpy, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CB='OR_skirt_base_course_20261031or'; OSM='OS_skirt_base_course_dark_dirt_UNVERIFIED'; NMAT='OT_skirt_base_course_midgrey_dirt_UNVERIFIED'
GN='OT_context_skirt_under_LiDAR'; MOD='OT_skirt_under_LiDAR'
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
# ---- undo
m=sk.modifiers.get(MOD)
if m: sk.modifiers.remove(m)
g=bpy.data.node_groups.get(GN)
if g: bpy.data.node_groups.remove(g)
om=bpy.data.materials[OSM]
nrest=0
for ob in bpy.data.collections[CB].objects:
    me=ob.data
    for i,mm in enumerate(me.materials):
        if mm and mm.name==NMAT: me.materials[i]=om
    a=me.attributes.get('ot_z0')
    if a:
        for v,d in zip(me.vertices,a.data): v.co.z=d.value
        me.attributes.remove(me.attributes['ot_z0']); me.update(); nrest+=1
mm=bpy.data.materials.get(NMAT)
if mm: bpy.data.materials.remove(mm)
KEY='ot_orig_z'; nback=0
for o in bpy.data.objects:
    if KEY in o: o.location.z=o[KEY]; del o[KEY]; nback+=1
for on in ('Footpaths_OSM','Roads_OSM'):
    o=bpy.data.objects[on]; mm2=o.modifiers.get('OT_follow_skirt_edge')
    if mm2: o.modifiers.remove(mm2)
    if 'UNVERIFIED_ot' in o: del o['UNVERIFIED_ot']
g2=bpy.data.node_groups.get('OT_follow_skirt_edge')
if g2: bpy.data.node_groups.remove(g2)
if 'UNVERIFIED_ot' in sk: del sk['UNVERIFIED_ot']
print('restored bands',nrest,'objects',nback)
if REV:
    om.use_fake_user=False
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
# ---- (A)
om.use_fake_user=True
nm=om.copy(); nm.name=NMAT; nt=nm.node_tree
cr=[n for n in nt.nodes if n.type=='VALTORGB'][0]; els=sorted(cr.color_ramp.elements,key=lambda e:e.position)
# or_h 0..1 spans DTM-0.22..DTM+0.42 after (B): grade line at 0.344
els[0].position=0.30; els[0].color=(0.075,0.064,0.05,1)     # soil at/below grade
els[1].position=0.43; els[1].color=(0.13,0.122,0.108,1)     # splash zone +6 cm
els[2].position=0.64; els[2].color=(0.23,0.225,0.212,1)     # mid-grey cast concrete from ~+19 cm
for n in nt.nodes:
    if n.type=='MIX' and n.blend_type=='MULTIPLY' and not n.inputs['Factor'].is_linked: pass
nb=0
for ob in bpy.data.collections[CB].objects:
    me=ob.data
    for i,x in enumerate(me.materials):
        if x and x.name==OSM: me.materials[i]=nm; nb+=1
print('BASE_SWAPPED',nb)
# ---- (B)
dg=bpy.context.evaluated_depsgraph_get()
e=ter.evaluated_get(dg); tm=e.to_mesh(); mw=ter.matrix_world
bt=BVHTree.FromPolygons([mw@v.co for v in tm.vertices],[p.vertices[:] for p in tm.polygons]); e.to_mesh_clear()
moved=0; miss=0; dz=[]
for ob in bpy.data.collections[CB].objects:
    me=ob.data; W=ob.matrix_world; Wi=W.inverted()
    z0=[v.co.z for v in me.vertices]
    a=me.attributes.new('ot_z0','FLOAT','POINT')
    for d,z in zip(a.data,z0): d.value=z
    oh=me.attributes['or_h'].data
    for v,h in zip(me.vertices,oh):
        w=W@v.co; hit=bt.ray_cast(Vector((w.x,w.y,w.z+60)),Vector((0,0,-1)),200)
        if hit[0] is None: miss+=1; continue
        nz=hit[0].z+(0.42 if h.value>0.5 else -0.22)
        l=Wi@Vector((w.x,w.y,nz)); dz.append(l.z-v.co.z); v.co.z=l.z; moved+=1
    me.update()
dz.sort(); print('BANDS moved',moved,'miss',miss,'dz min/med/max',round(dz[0],2),round(dz[len(dz)//2],2),round(dz[-1],2))
# ---- (C) v2: subdivide x2; skirt faces whose corners all have DTM below are deleted; straddling faces pushed to <= DTM-0.30;
#           points just outside the DTM edge ease down toward the nearest DTM edge height over 30 m (no cliff at the edge)
g=bpy.data.node_groups.new(GN,'GeometryNodeTree')
g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=g.nodes; L=g.links.new
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
sub=N.new('GeometryNodeSubdivideMesh'); sub.inputs['Level'].default_value=2
oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=ter; oi.transform_space='RELATIVE'
pos=N.new('GeometryNodeInputPosition')
up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; up.inputs[1].default_value=(0,0,150)
rc=N.new('GeometryNodeRaycast'); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=400
px=N.new('GeometryNodeProximity'); px.target_element='EDGES' if hasattr(px,'target_element') else px.target_element
sp=N.new('ShaderNodeSeparateXYZ'); sh=N.new('ShaderNodeSeparateXYZ'); sn=N.new('ShaderNodeSeparateXYZ')
mxz=N.new('GeometryNodeSwitch'); mxz.input_type='FLOAT'      # hit ? hitZ : nearestZ
t=N.new('ShaderNodeMath'); t.operation='SUBTRACT'; t.inputs[1].default_value=0.30
d=N.new('ShaderNodeMath'); d.operation='SUBTRACT'
mn=N.new('ShaderNodeMath'); mn.operation='MINIMUM'; mn.inputs[1].default_value=0.0
ws=N.new('ShaderNodeMapRange'); ws.interpolation_type='SMOOTHSTEP'; ws.inputs['From Min'].default_value=0.0; ws.inputs['From Max'].default_value=30.0; ws.inputs['To Min'].default_value=1.0; ws.inputs['To Max'].default_value=0.0
wsw=N.new('GeometryNodeSwitch'); wsw.input_type='FLOAT'; wsw.inputs['True'].default_value=1.0
hm=N.new('ShaderNodeMath'); hm.operation='MULTIPLY'
cv=N.new('ShaderNodeCombineXYZ'); setp=N.new('GeometryNodeSetPosition')
cap=N.new('GeometryNodeCaptureAttribute'); cap.domain='POINT'
try:
    cap.capture_items.new('BOOLEAN','hit'); 
except Exception: cap.data_type='BOOLEAN'
dl=N.new('GeometryNodeDeleteGeometry'); dl.domain='FACE'
L(gi.outputs[0],sub.inputs['Mesh']); L(sub.outputs[0],cap.inputs[0])
L(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L(oi.outputs['Geometry'],px.inputs[0])
L(pos.outputs[0],up.inputs[0]); L(up.outputs[0],rc.inputs['Source Position'])
L(rc.outputs['Is Hit'],cap.inputs[1])
L(cap.outputs[0],setp.inputs['Geometry']); L(setp.outputs[0],dl.inputs['Geometry']); L(cap.outputs[1],dl.inputs['Selection']); L(dl.outputs[0],go.inputs[0])
L(pos.outputs[0],sp.inputs[0]); L(rc.outputs['Hit Position'],sh.inputs[0]); L(px.outputs['Position'],sn.inputs[0])
L(rc.outputs['Is Hit'],mxz.inputs['Switch']); L(sh.outputs['Z'],mxz.inputs['True']); L(sn.outputs['Z'],mxz.inputs['False'])
L(mxz.outputs[0],t.inputs[0]); L(t.outputs[0],d.inputs[0]); L(sp.outputs['Z'],d.inputs[1]); L(d.outputs[0],mn.inputs[0])
L(px.outputs['Distance'],ws.inputs['Value']); L(rc.outputs['Is Hit'],wsw.inputs['Switch']); L(ws.outputs['Result'],wsw.inputs['False'])
L(mn.outputs[0],hm.inputs[0]); L(wsw.outputs[0],hm.inputs[1])
L(hm.outputs[0],cv.inputs['Z']); L(cv.outputs[0],setp.inputs['Offset'])
m=sk.modifiers.new(MOD,'NODES'); m.node_group=g
sk['UNVERIFIED_ot']='ot: skirt pushed under the LiDAR DTM where they overlap (GN modifier OT_skirt_under_LiDAR); mesh unedited'
# ---- (D) objects that stood on the old floating skirt over the DTM (bottom within 1.2 m of the old skirt surface, >0.4 m above the DTM)
bs0=BVHTree.FromPolygons([sk.matrix_world@v.co for v in sk.data.vertices],[p.vertices[:] for p in sk.data.polygons])
def bottom(o):
    if o.type=='MESH':
        return min((o.matrix_world@Vector(c)).z for c in o.bound_box)
    if o.type=='EMPTY' and o.instance_collection:
        zs=[(o.matrix_world@ (ob.matrix_world@Vector(c))).z for ob in o.instance_collection.all_objects if ob.type=='MESH' for c in ob.bound_box]
        return min(zs) if zs else None
    return None
dropped=[]
for o in list(bpy.context.scene.objects):
    if o.parent or o.name.startswith(('Context_skirt','Terrain_','BD_','MID_','OO_skirt','OR_','Footpaths','Roads','Curbs')): continue
    if o.type not in ('MESH','EMPTY'): continue
    t=o.matrix_world.translation
    hs=bs0.ray_cast(Vector((t.x,t.y,t.z+300)),Vector((0,0,-1)),900); ht=bt.ray_cast(Vector((t.x,t.y,t.z+300)),Vector((0,0,-1)),900)
    if not (hs[0] and ht[0]) or hs[0].z<ht[0].z+0.4: continue
    b=bottom(o)
    if b is None or abs(b-hs[0].z)>1.2 or b<ht[0].z+0.4: continue
    o['ot_orig_z']=o.location.z; o.location.z+= (ht[0].z+0.0)-b - 0.05; dropped.append((o.name,round(ht[0].z-b,1)))
print('DROPPED',len(dropped),dropped[:20])
# ---- (E) walks/roads just outside the DTM edge follow the eased skirt (+5 cm) within 30 m of the DTM, fading out by 40 m
g2=bpy.data.node_groups.new('OT_follow_skirt_edge','GeometryNodeTree')
g2.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); g2.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=g2.nodes; L=g2.links.new
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
o1=N.new('GeometryNodeObjectInfo'); o1.inputs['Object'].default_value=ter; o1.transform_space='RELATIVE'
o2=N.new('GeometryNodeObjectInfo'); o2.inputs['Object'].default_value=sk; o2.transform_space='RELATIVE'
pos=N.new('GeometryNodeInputPosition'); up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; up.inputs[1].default_value=(0,0,150)
r1=N.new('GeometryNodeRaycast'); r1.inputs['Ray Direction'].default_value=(0,0,-1); r1.inputs['Ray Length'].default_value=400
r2=N.new('GeometryNodeRaycast'); r2.inputs['Ray Direction'].default_value=(0,0,-1); r2.inputs['Ray Length'].default_value=400
px=N.new('GeometryNodeProximity')
sp=N.new('ShaderNodeSeparateXYZ'); s2=N.new('ShaderNodeSeparateXYZ')
dz=N.new('ShaderNodeMath'); dz.operation='SUBTRACT'; a5=N.new('ShaderNodeMath'); a5.operation='ADD'; a5.inputs[1].default_value=0.05
wf=N.new('ShaderNodeMapRange'); wf.inputs['From Min'].default_value=30.0; wf.inputs['From Max'].default_value=40.0; wf.inputs['To Min'].default_value=1.0; wf.inputs['To Max'].default_value=0.0
nh=N.new('FunctionNodeBooleanMath'); nh.operation='NOT'
a1=N.new('ShaderNodeMath'); a1.operation='MULTIPLY'; a2=N.new('ShaderNodeMath'); a2.operation='MULTIPLY'; a3=N.new('ShaderNodeMath'); a3.operation='MULTIPLY'
cv=N.new('ShaderNodeCombineXYZ'); setp=N.new('GeometryNodeSetPosition')
L(gi.outputs[0],setp.inputs['Geometry']); L(setp.outputs[0],go.inputs[0])
L(o1.outputs['Geometry'],r1.inputs['Target Geometry']); L(o2.outputs['Geometry'],r2.inputs['Target Geometry']); L(o1.outputs['Geometry'],px.inputs[0])
L(pos.outputs[0],up.inputs[0]); L(up.outputs[0],r1.inputs['Source Position']); L(up.outputs[0],r2.inputs['Source Position'])
L(pos.outputs[0],sp.inputs[0]); L(r2.outputs['Hit Position'],s2.inputs[0])
L(s2.outputs['Z'],a5.inputs[0]); L(a5.outputs[0],dz.inputs[0]); L(sp.outputs['Z'],dz.inputs[1])
L(px.outputs['Distance'],wf.inputs['Value']); L(r1.outputs['Is Hit'],nh.inputs[0])
L(dz.outputs[0],a1.inputs[0]); L(wf.outputs['Result'],a1.inputs[1]); L(a1.outputs[0],a2.inputs[0]); L(nh.outputs[0],a2.inputs[1]); L(a2.outputs[0],a3.inputs[0]); L(r2.outputs['Is Hit'],a3.inputs[1])
L(a3.outputs[0],cv.inputs['Z']); L(cv.outputs[0],setp.inputs['Offset'])
for on in ('Footpaths_OSM','Roads_OSM'):
    o=bpy.data.objects[on]; mo=o.modifiers.new('OT_follow_skirt_edge','NODES'); mo.node_group=g2
    o['UNVERIFIED_ot']='ot: outside the DTM edge, within 30-40 m, follows the eased context skirt +5 cm (GN OT_follow_skirt_edge)'
# check: skirt above DTM after
dg=bpy.context.evaluated_depsgraph_get(); e=sk.evaluated_get(dg); me=e.to_mesh(); W=sk.matrix_world
bs=BVHTree.FromPolygons([W@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
cnt=ab=0; worst=[]
for x in range(-248,246,4):
    for y in range(-248,248,4):
        hs=bs.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); ht=bt.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
        if hs[0] and ht[0]:
            cnt+=1
            if hs[0].z>ht[0].z-0.02: ab+=1; worst.append((round(hs[0].z-ht[0].z,2),x,y))
worst.sort(reverse=True); print('SKIRT overlap cells',cnt,'still above',ab,worst[:8])
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
