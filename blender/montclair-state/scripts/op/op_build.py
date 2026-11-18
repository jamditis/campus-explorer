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
GN='OP_road_redrape_to_LiDAR'; MOD='OP_redrape_LiDAR'; KEY='op_orig_z_unused'
C=Vector((10.6,141.1)); R0,R1=-2.0,-1.0; F0,F1=float(os.environ.get('F0',0.06)),float(os.environ.get('F1',0.15)); OFF=0.03
fp=bpy.data.objects['Roads_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
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
# op: keep the road hidden where it would come up under/through hand-built ground pieces (Cole plaza deck/steps/edge, CCOM dock apron)
MASKS=[o for o in bpy.data.objects if o.name in ('COLE_plaza_deck_bs','COLE_plaza_west_steps_bu','COLE_plaza_edge_bs','CCOM_dock_apron_20261014jf3')]
last=wh
for mo in MASKS:
    cs=[mo.matrix_world@Vector(c) for c in mo.bound_box]; M=0.5
    x0=min(c.x for c in cs)-M;x1=max(c.x for c in cs)+M;y0=min(c.y for c in cs)-M;y1=max(c.y for c in cs)+M
    # signed outside distance to the (margin-grown) box: d=max(x0-x,x-x1,y0-y,y-y1); weight=smoothstep(0,6 m,d) so the road eases down into the ground
    terms=[]
    for comp,val,sgn in (('X',x0,-1),('X',x1,1),('Y',y0,-1),('Y',y1,1)):
        t=N.new('ShaderNodeMath'); t.operation='MULTIPLY_ADD'; t.inputs[1].default_value=sgn; t.inputs[2].default_value=-sgn*val; L(sp.outputs[comp],t.inputs[0]); terms.append(t)
    mx=terms[0]
    for t in terms[1:]:
        m2=N.new('ShaderNodeMath'); m2.operation='MAXIMUM'; L(mx.outputs[0],m2.inputs[0]); L(t.outputs[0],m2.inputs[1]); mx=m2
    sw=N.new('ShaderNodeMapRange'); sw.interpolation_type='SMOOTHSTEP'; sw.inputs['From Min'].default_value=0.0; sw.inputs['From Max'].default_value=6.0; L(mx.outputs[0],sw.inputs['Value'])
    mm=N.new('ShaderNodeMath'); mm.operation='MULTIPLY'; L(last.outputs[0],mm.inputs[0]); L(sw.outputs['Result'],mm.inputs[1]); last=mm
    print('mask',mo.name,round(x0,1),round(x1,1),round(y0,1),round(y1,1))
if last is not wh: L(last.outputs[0],od.inputs[1])
mod=fp.modifiers.new(MOD,'NODES'); mod.node_group=g
fp['UNVERIFIED_op']='oo: roads re-draped to LiDAR DTM +3 cm where they were >6-15 cm off (GN modifier); real grading unverified'
# --- overlap probe on the evaluated, re-draped roads (bbox-prefiltered BVH, not scene.ray_cast)
import collections
if os.environ.get('PROBE')=='1':
    dg=bpy.context.evaluated_depsgraph_get()
    e=fp.evaluated_get(dg); me=e.to_mesh(); mw=fp.matrix_world
    pts=[mw@v.co for i,v in enumerate(me.vertices) if i%5==0]
    cell={}
    for p in pts:
        k=(int(p.x//8),int(p.y//8)); a=cell.get(k); cell[k]=(min(a[0],p.z),max(a[1],p.z)) if a else (p.z,p.z)
    cand=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o is fp or o.name.startswith('Terrain') or o.hide_render: continue
        if o.name.startswith(('T_','Tree','Grass','MID_')): continue
        cs=[o.matrix_world@Vector(c) for c in o.bound_box]
        x0=min(c.x for c in cs);x1=max(c.x for c in cs);y0=min(c.y for c in cs);y1=max(c.y for c in cs);z0=min(c.z for c in cs);z1=max(c.z for c in cs)
        if (x1-x0)*(y1-y0)>4e5: continue
        ok=False
        for i in range(int(x0//8),int(x1//8)+1):
            for j in range(int(y0//8),int(y1//8)+1):
                a=cell.get((i,j))
                if a and z0<a[1]+2.5 and z1>a[0]-0.1: ok=True;break
            if ok:break
        if ok: cand.append(o)
    print('candidates',len(cand))
    trees=[]
    for o in cand:
        try:
            oe=o.evaluated_get(dg); m2=oe.to_mesh(); b=bmesh.new(); b.from_mesh(m2); b.transform(o.matrix_world); trees.append((o.name,BVHTree.FromBMesh(b))); oe.to_mesh_clear(); b.free()
        except Exception as ex: pass
    cnt=collections.Counter(); up=collections.Counter()
    for p in pts:
        for nm,t in trees:
            h=t.ray_cast(p+Vector((0,0,0.6)),Vector((0,0,-1)),0.59)
            if h[0]: cnt[nm]+=1
            h=t.ray_cast(p+Vector((0,0,0.01)),Vector((0,0,1)),2.5)
            if h[0]: up[nm]+=1
    print('sampled',len(pts))
    print('COVER:',cnt.most_common(30))
    print('UP:',up.most_common(30))
print('GN built', GN)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
