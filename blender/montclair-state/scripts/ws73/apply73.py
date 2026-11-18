# ws73: College Ave curbs in the RHD/Kasser corridor (x -252..-193): (1) tone curb + gutter pan to sunlit weathered concrete,
# (2) curb back made a near-vertical 4 cm-batter face down to ground-5cm (was a 27 cm pale back slope = "wide pale band"),
# (3) terrain clamp ribbon behind both curbs so grass meets the curb back below the curb top (kills stepped notches at the bend x -205..-199)
import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
dn=lambda t,x,y:(t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0])
X0,X1,YMIN=-252.0,-193.0,-95.0
# --- (1) tone
def lum(c): return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
for mn,tgt in (('WS27_curb_concrete_UNVERIFIED',0.36),('WS27_gutter_pan_concrete_UNVERIFIED',0.26)):
    m=bpy.data.materials[mn]; cr=[n for n in m.node_tree.nodes if n.type=='VALTORGB'][0].color_ramp
    cur=[tuple(e.color) for e in cr.elements]; av=sum(lum(c) for c in cur)/len(cur)
    print('W73 ramp',mn,[tuple(round(v,3) for v in c[:3]) for c in cur],'avg',round(av,3))
    if av>tgt and not m.get('ws73_toned'):
        f=tgt/av
        for e in cr.elements: e.color=(e.color[0]*f,e.color[1]*f,e.color[2]*f,1)
        m['ws73_toned']=1; print('W73 toned',mn,'x',round(f,3))
# --- (2) curb back face
T0=bvh('Terrain_LiDAR_DTM_1m')
ribbon=[]
for cn in ('WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED'):
    o=bpy.data.objects[cn]; me=o.data; V=me.vertices; n=0
    rows=len(V)//6
    for r in range(rows):
        v=[V[6*r+k] for k in range(6)]
        if not (X0<v[0].co.x<X1 and v[0].co.y>YMIN): continue
        d=Vector((v[5].co.x-v[4].co.x,v[5].co.y-v[4].co.y,0))
        if d.length<1e-4: continue
        d.normalize()
        if not o.get('ws73_back'):
            bx=v[4].co.x+d.x*0.04; by=v[4].co.y+d.y*0.04
            h=dn(T0,bx+d.x*0.3,by+d.y*0.3); gz=h.z if h else v[5].co.z
            v[5].co.x=bx; v[5].co.y=by; v[5].co.z=min(gz-0.05,v[4].co.z-0.16); n+=1
        ribbon.append((cn,r,v[0].co.copy(),v[4].co.copy(),d.copy()))
    if not o.get('ws73_back'): o['ws73_back']=1
    me.update(); print('W73 back rows',cn[:28],n)
# --- (3) terrain clamp helper ribbon (hidden): front edge -> back -> 1.6 m out blending to the (pre-clamp) terrain
name='WS73_curb_back_clamp_helper_hidden'
old=bpy.data.objects.get(name)
if old: bpy.data.objects.remove(old)
me=bpy.data.meshes.new(name); bm=bmesh.new(); prev={}
for cn,r,f0,b4,d in ribbon:
    pts=[(f0.x-d.x*0.3,f0.y-d.y*0.3,f0.z-0.06),(f0.x,f0.y,f0.z-0.05),(b4.x,b4.y,b4.z-0.04)]
    for s in (0.4,0.8,1.2,1.6):
        x=b4.x+d.x*s; y=b4.y+d.y*s; h=dn(T0,x,y); tz=h.z if h else b4.z
        w=s/1.6; z=(b4.z-0.04)*(1-w)+max(tz,b4.z-0.04)*w if tz>b4.z-0.04 else tz
        pts.append((x,y,z))
    row=[bm.verts.new(p) for p in pts]
    if (cn,r-1) in prev:
        p=prev[(cn,r-1)]
        for k in range(len(row)-1): bm.faces.new((p[k],row[k],row[k+1],p[k+1]))
    prev[(cn,r)]=row
bm.to_mesh(me); bm.free()
hc=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(hc); hc.hide_render=True; hc.hide_viewport=True; hc.display_type='WIRE'
G='WS73_curb_back_terrain_clamp'
ng=bpy.data.node_groups.get(G) or bpy.data.node_groups.new(G,'GeometryNodeTree')
ng.nodes.clear()
if not ng.interface.items_tree:
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=hc; oi.transform_space='RELATIVE'
pos=N.new('GeometryNodeInputPosition')
up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; up.inputs[1].default_value=(0,0,50); L.new(pos.outputs[0],up.inputs[0])
rc=N.new('GeometryNodeRaycast'); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=100
L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(up.outputs[0],rc.inputs['Source Position'])
sp=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sp.inputs[0])
sp2=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp2.inputs[0])
mn=N.new('ShaderNodeMath'); mn.operation='MINIMUM'; L.new(sp2.outputs['Z'],mn.inputs[0]); L.new(sp.outputs['Z'],mn.inputs[1])
cb=N.new('ShaderNodeCombineXYZ'); L.new(sp2.outputs['X'],cb.inputs[0]); L.new(sp2.outputs['Y'],cb.inputs[1]); L.new(mn.outputs[0],cb.inputs[2])
st=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],st.inputs['Geometry']); L.new(rc.outputs['Is Hit'],st.inputs['Selection']); L.new(cb.outputs[0],st.inputs['Position'])
L.new(st.outputs[0],go.inputs[0])
TG=['Terrain_LiDAR_DTM_1m']+[o.name for o in bpy.data.objects if o.name.startswith(('WS70_gap_strip_grass_berms','WS60_terrain_edge_apron'))]
for n in TG:
    o=bpy.data.objects[n]
    if G not in o.modifiers: md=o.modifiers.new(G,'NODES'); md.node_group=ng
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
# --- check: ground vs curb top along each row, 5..60 cm behind the curb back
tot=0
for n in TG:
    T=bvh(n); bad=0; c=0; mx=-9
    for cn,r,f0,b4,d in ribbon:
        for s in (0.0,0.05,0.2,0.4):
            x=b4.x+d.x*s; y=b4.y+d.y*s; h=dn(T,x,y)
            if h: c+=1; mx=max(mx,h.z-b4.z)
            if h and h.z>b4.z-0.01: bad+=1
    tot+=bad; print('W73 check',n[:30],'above curbtop',bad,'/',c,'max',round(mx,3))
# under the curb top itself (between front and back)
T=bvh('Terrain_LiDAR_DTM_1m'); bad=0
for cn,r,f0,b4,d in ribbon:
    for t in (0.3,0.6,0.9):
        p=f0.lerp(b4,t); h=dn(T,p.x,p.y)
        if h and h.z>p.z-0.01: bad+=1
print('W73 under-curb terrain above',bad,'/',len(ribbon)*3); tot+=bad
print('W73 total',tot,flush=True)
if os.environ.get('SAVE')=='1' and tot<20: bpy.ops.wm.save_mainfile(); print('W73 SAVED',flush=True)
