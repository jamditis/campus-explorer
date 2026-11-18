# oo (Oct 31 2026): re-drape the floating/sunken Footpaths_OSM walk network onto the LiDAR DTM OUTSIDE the Schmitt entrance zone.
# Evidence: data/om/osm_walk_float_classes.txt + data/oo/float_map.txt (147 of 405 16 m cells off by >0.25 m; north of y~112 the walks float
# up to ~8 m over a flat DTM; east edge x~160-176 they sit up to ~12 m under it). Non-destructive: a GN modifier on Footpaths_OSM
# (subdivide x2 -> raycast to Terrain_LiDAR_DTM_1m -> lower/raise to DTM+5 cm), weight 0 where |float|<0.06 m (full ramp by 0.15 m; v2 after the 0.25 m version left kinks)
# and inside 24 m of the Schmitt entrance (10.6,141.1) where the raised walk waits on Joe's grade answer (ramp 24->34 m).
# Site furniture standing at the old walk height is moved by the same amount (object location only). OSM mesh data NOT edited.
# REVERT=1 removes the modifier + node group and restores the furniture locations from the stored custom props.
import bpy, bmesh, os, sys, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
GN='OO_walk_redrape_to_LiDAR'; MOD='OO_redrape_LiDAR'; KEY='oo_orig_z'
C=Vector((10.6,141.1)); R0,R1=24.0,34.0; F0,F1=0.06,0.15; OFF=0.05
fp=bpy.data.objects['Footpaths_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
m=fp.modifiers.get(MOD)
if m: fp.modifiers.remove(m)
g=bpy.data.node_groups.get(GN)
if g: bpy.data.node_groups.remove(g)
nback=0
for o in bpy.data.objects:
    if KEY in o:
        o.location.z=o[KEY]; del o[KEY]; nback+=1
print('restored furniture',nback)
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
# --- node group
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
sp=N.new('ShaderNodeSeparateXYZ'); sh=N.new('ShaderNodeSeparateXYZ')
f=N.new('ShaderNodeMath'); f.operation='SUBTRACT'          # f = z - tz
fa=N.new('ShaderNodeMath'); fa.operation='ABSOLUTE'
wf=N.new('ShaderNodeMapRange'); wf.interpolation_type='SMOOTHSTEP'; wf.inputs['From Min'].default_value=F0; wf.inputs['From Max'].default_value=F1
d2=N.new('ShaderNodeVectorMath'); d2.operation='DISTANCE'; d2.inputs[1].default_value=(C.x,C.y,0)
flat=N.new('ShaderNodeCombineXYZ')
wr=N.new('ShaderNodeMapRange'); wr.interpolation_type='SMOOTHSTEP'; wr.inputs['From Min'].default_value=R0; wr.inputs['From Max'].default_value=R1
w=N.new('ShaderNodeMath'); w.operation='MULTIPLY'
wh=N.new('ShaderNodeMath'); wh.operation='MULTIPLY'
dd=N.new('ShaderNodeMath'); dd.operation='SUBTRACT'; dd.inputs[1].default_value=OFF   # f - OFF
od=N.new('ShaderNodeMath'); od.operation='MULTIPLY'
ng=N.new('ShaderNodeMath'); ng.operation='MULTIPLY'; ng.inputs[1].default_value=-1
cv=N.new('ShaderNodeCombineXYZ')
setp=N.new('GeometryNodeSetPosition')
L(gi.outputs[0],sub.inputs['Mesh']); L(sub.outputs[0],setp.inputs['Geometry']); L(setp.outputs[0],go.inputs[0])
L(oi.outputs['Geometry'],rc.inputs['Target Geometry'])
L(pos.outputs[0],up.inputs[0]); L(up.outputs[0],rc.inputs['Source Position'])
L(pos.outputs[0],sp.inputs[0]); L(rc.outputs['Hit Position'],sh.inputs[0])
L(sp.outputs['Z'],f.inputs[0]); L(sh.outputs['Z'],f.inputs[1])
L(f.outputs[0],fa.inputs[0]); L(fa.outputs[0],wf.inputs['Value'])
L(sp.outputs['X'],flat.inputs['X']); L(sp.outputs['Y'],flat.inputs['Y']); L(flat.outputs[0],d2.inputs[0])
L(d2.outputs['Value'],wr.inputs['Value'])
L(wf.outputs['Result'],w.inputs[0]); L(wr.outputs['Result'],w.inputs[1])
L(w.outputs[0],wh.inputs[0]); L(rc.outputs['Is Hit'],wh.inputs[1])
L(f.outputs[0],dd.inputs[0]); L(dd.outputs[0],od.inputs[0]); L(wh.outputs[0],od.inputs[1])
L(od.outputs[0],ng.inputs[0]); L(ng.outputs[0],cv.inputs['Z']); L(cv.outputs[0],setp.inputs['Offset'])
mod=fp.modifiers.new(MOD,'NODES'); mod.node_group=g
fp['UNVERIFIED_oo']='oo: walks outside the Schmitt entrance zone re-draped to LiDAR DTM +5 cm (GN modifier); real grading unverified'
# --- furniture: same formula at the object base
dg=bpy.context.evaluated_depsgraph_get(); te=ter.evaluated_get(dg); bt=bmesh.new(); bt.from_mesh(te.to_mesh()); bt.transform(ter.matrix_world); tree=BVHTree.FromBMesh(bt)
bw=bmesh.new(); bw.from_mesh(fp.data); wt=BVHTree.FromBMesh(bw)
def tz(x,y):
    h=tree.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] else None
def smooth(a,b,x):
    t=min(1,max(0,(x-a)/(b-a))); return t*t*(3-2*t)
moved=[]
for o in bpy.data.objects:
    if o.parent or o.library or o.type not in ('MESH','EMPTY','CURVE'): continue
    cn=[c.name for c in o.users_collection]
    if not any(('Site_furniture' in c) for c in cn) and not o.name.startswith(('Lamp_','Bench_','Bin_','Bollard_')): continue
    p=o.matrix_world.translation; t=tz(p.x,p.y)
    if t is None: continue
    # walk z near the base (within 3 m horizontally)
    loc,nrm,idx,dist=wt.find_nearest(Vector((p.x,p.y,p.z)),3.0)
    if loc is None or abs(loc.z-p.z)>0.6: continue
    wtz=tz(loc.x,loc.y)
    if wtz is None: continue
    fw=loc.z-wtz
    W=smooth(F0,F1,abs(fw))*smooth(R0,R1,(Vector((loc.x,loc.y))-C).length)
    dz=-W*(fw-OFF)
    if abs(dz)<0.03: continue
    o[KEY]=o.location.z; o.location.z+=dz; moved.append((o.name,round(dz,2)))
print('moved furniture',len(moved),moved)
print('GN built', GN)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
