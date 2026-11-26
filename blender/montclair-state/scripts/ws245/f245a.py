# ws245 W62b: (1) E pad NE corner — ground still up to 1.11 m over fse_stand_under_pad at (-219.7,120.3): the f244a strips are
#   per-edge rectangles, so every CONVEX corner of the field/pad outline left a wedge with no hold-under target; ground
#   vertices in that wedge stayed on the bank and their faces rose over the pad corner. Fix: corner fans at every convex
#   boundary vertex (flat, same 1.5 m margin).
# (2) the pale faceted near-vertical bank N of the east stand: the 1.5 m flat margin ended in a step straight up to the LiDAR
#   bank. Fix: on the east-bank edges only (edge midpoints x > -236, y > 95), add a SLOPED ring outside the margin, 6 m wide,
#   rising 0.45 m per m (~24 deg, a mowable graded bank; UNVERIFIED design). The GN only LOWERS ground within 3 m over the
#   target, so ground below the ring is untouched and paving never moves. Trees standing on the lowered band are lowered
#   with the ground (estimate from the base DTM; printed).
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TG=['fs_turf','fr_stand_under_pad','fse_stand_under_pad','fr_front_walkway','fse_front_walkway','fst_front_walkway','fr_stand_entry_steps','fse_stand_entry_steps','fst_stand_entry_steps']
o=bpy.data.objects['WS243_stands_pitch_holdunder_target']
bm=bmesh.new()
for n in TG:
    s=bpy.data.objects[n]; t=bmesh.new(); t.from_mesh(s.data); t.transform(s.matrix_world)
    me=bpy.data.meshes.new('tmp245'); t.to_mesh(me); t.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
# top faces only: the stand pads are closed slabs (side faces), so their top outline edges were never 'boundary' and the
# f244a margin was never built along the pads (east pad NE corner).
bm.normal_update()
dead=[f for f in bm.faces if f.normal.z<0.5]
print('F245A dropped non-top faces',len(dead),flush=True)
bmesh.ops.delete(bm,geom=dead,context='FACES')
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
bv=BVHTree.FromBMesh(bm)
def over(p):
    h=bv.ray_cast(p+Vector((0,0,0.01)),Vector((0,0,-1)),40); return h[0] is not None
W=1.5; F=6.0; SL=0.45
def inR(p): return (p.x>-236 and p.y>119.5) or (p.x>-222 and p.y>95)
B=[e for e in bm.edges if e.is_boundary and len(e.link_faces)==1]
E=[]; VN={}
for e in B:
    a,b=e.verts[0],e.verts[1]; c=e.link_faces[0].calc_center_median()
    d=b.co-a.co; d.z=0
    if d.length<1e-4: continue
    n=Vector((d.y,-d.x,0)).normalized(); m=(a.co+b.co)/2
    if n.dot(Vector((m.x-c.x,m.y-c.y,0)))<0: n=-n
    E.append((a.co.copy(),b.co.copy(),n)); VN.setdefault(a.index,[]).append(n); VN.setdefault(b.index,[]).append(n)
strips=[]; fans=[]; ring=[]; skip=0
for a,b,n in E:
    q=[(a+b)/2+n*(W*0.5),a+n*W*0.9+(b-a)*0.05,b+n*W*0.9-(b-a)*0.05]
    # long edges (the turf sides are single 100 m+ edges) are cut into <=2 m pieces for the region test
    L=(b-a).length; K=max(1,int(L/2.0+0.999)); up=Vector((0,0,SL*F))
    for i in range(K):
        a1=a.lerp(b,i/K); b1=a.lerp(b,(i+1)/K)
        if inR((a1+b1)/2): ring.append([a1+n*(W-0.25),b1+n*(W-0.25),b1+n*(W+F)+up,a1+n*(W+F)+up])
    if any(over(x) for x in q): skip+=1; continue
    strips.append([a,b,b+n*W,a+n*W])
fskip=0
for vi,ns in VN.items():
    if len(ns)!=2: continue
    n1,n2=ns
    if n1.dot(n2)>0.985: continue
    nb=(n1+n2)
    if nb.length<1e-3: continue
    nb.normalize(); v=bm.verts[vi].co.copy()
    # convex corner only: the bisector point must lie outside both strips (i.e. not over the base target)
    if over(v+nb*W*0.7) or over(v+nb*0.3): fskip+=1; continue
    fans.append([v,v+n1*W,v+nb*W*1.05,v+n2*W])
    if inR(v):
        up=Vector((0,0,SL*F))
        ring.append([v+n1*W,v+n1*(W+F)+up,v+nb*(W+F)*1.02+up,v+nb*W*1.05])
        ring.append([v+nb*W*1.05,v+nb*(W+F)*1.02+up,v+n2*(W+F)+up,v+n2*W])
for P in strips+fans:
    try: bm.faces.new([bm.verts.new(x) for x in P])
    except ValueError: pass
bm.to_mesh(o.data); o.data.update()
import ctypes
# ray cast from 30 m BELOW, upward: the FIRST hit is the LOWEST ring surface where ring quads of neighbouring edges overlap
# (a downward ray took the highest one, so the pad's north ring held the turf-side bank up).
def hold(obj,target,off,name):
    ng=bpy.data.node_groups.new(name,'GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=target
    pos=N.new('GeometryNodeInputPosition'); up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; up.inputs[1].default_value=(0,0,-30); L.new(pos.outputs[0],up.inputs[0])
    rc=N.new('GeometryNodeRaycast'); L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(up.outputs[0],rc.inputs['Source Position'])
    rc.inputs['Ray Direction'].default_value=(0,0,1); rc.inputs['Ray Length'].default_value=60
    sh=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sh.inputs[0]); sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
    tz=N.new('ShaderNodeMath'); tz.operation='SUBTRACT'; tz.inputs[1].default_value=off; L.new(sh.outputs['Z'],tz.inputs[0])
    cmp=N.new('ShaderNodeMath'); cmp.operation='GREATER_THAN'; L.new(sp.outputs['Z'],cmp.inputs[0]); L.new(tz.outputs[0],cmp.inputs[1])
    dz=N.new('ShaderNodeMath'); dz.operation='SUBTRACT'; L.new(tz.outputs[0],dz.inputs[0]); L.new(sp.outputs['Z'],dz.inputs[1])
    near=N.new('ShaderNodeMath'); near.operation='GREATER_THAN'; L.new(dz.outputs[0],near.inputs[0]); near.inputs[1].default_value=-3.0
    a1=N.new('FunctionNodeBooleanMath'); a1.operation='AND'; L.new(rc.outputs['Is Hit'],a1.inputs[0]); L.new(cmp.outputs[0],a1.inputs[1])
    a2=N.new('FunctionNodeBooleanMath'); a2.operation='AND'; L.new(a1.outputs[0],a2.inputs[0]); L.new(near.outputs[0],a2.inputs[1])
    cx=N.new('ShaderNodeCombineXYZ'); L.new(sp.outputs['X'],cx.inputs['X']); L.new(sp.outputs['Y'],cx.inputs['Y']); L.new(tz.outputs[0],cx.inputs['Z'])
    st=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],st.inputs['Geometry']); L.new(a2.outputs[0],st.inputs['Selection']); L.new(cx.outputs[0],st.inputs['Position'])
    L.new(st.outputs[0],go.inputs[0])
    m=obj.modifiers.new(name,'NODES'); m.node_group=ng; m.show_viewport=False
    v=ctypes.c_int.from_address(m.as_pointer()+20); v.value=v.value|1

print('F245A target rebuilt: strips',len(strips),'skipped',skip,'corner fans',len(fans),'fan skipped',fskip,'ring quads',len(ring),flush=True)
# sloped ring: SEPARATE hidden target with its own lower-only GN on every ground stack, so the result is the MIN of the
# flat hold-under and the graded bank (a ring quad over the lower turf/pad can never hold ground up there).
rb2=bmesh.new()
for P in ring:
    rb2.faces.new([rb2.verts.new(x) for x in P])
rme=bpy.data.meshes.get('WS245_E_bank_grade_target') or bpy.data.meshes.new('WS245_E_bank_grade_target')
rb2.to_mesh(rme); rb2.free()
ro=bpy.data.objects.get('WS245_E_bank_grade_target_UNVERIFIED')
if ro is None:
    ro=bpy.data.objects.new('WS245_E_bank_grade_target_UNVERIFIED',rme); ro.hide_render=True; ro.display_type='WIRE'
    o.users_collection[0].objects.link(ro)
print('F245A sloped ring quads',len(ring),flush=True)
GN=[g for g in bpy.data.objects if g.type=='MESH' and any(m.name=='WS243_terrain_hold_under_stands_pitch' or (m.type=='NODES' and m.node_group and m.node_group.name.startswith('WS243_under_stands_pitch')) for m in g.modifiers)]
for g in GN:
    if 'WS245_E_bank_terrain_grade' in g.modifiers: continue
    hold(g,ro,0.06,'WS245_E_bank_terrain_grade'); print('F245A bank-grade GN on',g.name[:40],flush=True)
# lower trees standing on the lowered ring band (base-DTM estimate)
nb2=bmesh.new()
for P in ring:
    nb2.faces.new([nb2.verts.new(x) for x in P])
rb=BVHTree.FromBMesh(nb2); nb2.free()
dtm=bpy.data.objects.get('Terrain_LiDAR_DTM_1m')
tb=BVHTree.FromPolygons([dtm.matrix_world@v.co for v in dtm.data.vertices],[p.vertices[:] for p in dtm.data.polygons]) if dtm else None
mv=0
for t in bpy.data.objects:
    if t.type not in ('MESH','EMPTY') or t.parent is not None: continue
    p=t.matrix_world.translation
    if not inR(p) or not (-245<p.x<-180 and 90<p.y<200): continue
    if 'tree' not in t.name.lower() and 'shrub' not in t.name.lower(): continue
    h=rb.ray_cast(Vector((p.x,p.y,p.z+40)),Vector((0,0,-1)),90)
    g=tb.ray_cast(Vector((p.x,p.y,p.z+40)),Vector((0,0,-1)),90) if tb else (None,)
    if h[0] is None or g[0] is None: continue
    dz=g[0].z-(h[0].z-0.06)
    if 0.02<dz<3.0 and abs(p.z-g[0].z)<1.0:
        t.location.z-=dz; mv+=1; print('F245A tree lowered',t.name[:40],round(dz,2),flush=True)
print('F245A trees lowered',mv,flush=True)
