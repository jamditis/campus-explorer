# ws72: SW Kasser / RHD SE core sidewalk landing x -255.5..-243 between College Ave north curb back and the building feet (Joe 10:18 PM Nov 10: road meets sidewalk, no lawn gap)
import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
OB=lambda p:[o.name for o in bpy.data.objects if o.name.startswith(p)][0]
CL=bvh('WS27_CollegeAve_curb_left_UNVERIFIED'); GS=bvh('WS69_CollegeAve_gap_strip_curbs_UNVERIFIED')
WALLS=[bvh('Alexander Kasser Theater walls'),bvh('bx_rhd_se_core_skin')]
W71=bvh('WS71_Kasser_S_sidewalk_ortho2020_UNVERIFIED_width')
dn=lambda t,x,y:(t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0])
X0,X1=-255.5,-243.0; rows=[]; x=X0
while x<=X1+1e-6:
    cy=None; cz=None
    for t in (CL,GS):
        for i in range(200):
            y=-56+i*0.05
            h=dn(t,x,y)
            if h and (cy is None or y>cy): cy=y; cz=h.z
    rows.append([x,cy,cz,None]); x+=0.5
# fill gaps by interpolation
idx=[i for i,r in enumerate(rows) if r[1] is not None]
for i,r in enumerate(rows):
    if r[1] is None:
        a=max([j for j in idx if j<i],default=None); b=min([j for j in idx if j>i],default=None)
        a=a if a is not None else b; b=b if b is not None else a; f=0 if a==b else (i-a)/(b-a)
        r[1]=rows[a][1]+(rows[b][1]-rows[a][1])*f; r[2]=rows[a][2]+(rows[b][2]-rows[a][2])*f
for r in rows:
    x,cy,cz,_=r; yn=None
    for t in WALLS:
        h=t.ray_cast(Vector((x,cy,cz+1.5)),Vector((0,1,0)),12)[0]
        if h and (yn is None or h.y<yn): yn=h.y
    r[3]=(yn-0.03) if yn else cy+5.5
    r[1]=cy+0.03
for j in (1,2,3):
    vals=[r[j] for r in rows]; out=[]
    for i in range(len(vals)):
        w=vals[max(0,i-3):i+4]; out.append(sum(w)/len(w))
    for r,v in zip(rows,out): r[j]=v
for r in rows: r[2]+=0.01
# match ws71 walk west end height exactly at x=-243
h=dn(W71,-242.9,rows[-1][1]+0.2)
if h:
    d=h.z-(rows[-1][2]+0.015*0.2)
    for i,r in enumerate(rows): r[2]+=d*max(0,(i-(len(rows)-9))/8)
    print('W72 join ws71 delta',round(d,3))
# ws72 fix2: ramp the west end down to the SE-core crosswalk landing (LF ramp fill) / door landing so there is no ~20 cm step
LFt=bvh(OB('LF_rhd_se_curb_ramp_fill'))
h=dn(LFt,-255.8,(rows[0][1]+rows[0][3])/2-1.0)
LZ=(h.z+0.005) if h else 125.14  # probe ws72: LF top 125.02-125.17, RHD door landing <=125.1
if True:
    d=LZ-rows[0][2]
    for i,r in enumerate(rows): r[2]+=d*max(0,(8-i)/8)
    print('W72 west ramp delta',round(d,3))
for r in rows: print('W72 row',[round(v,2) for v in r])
XF=0.015
def mk(name,ext,mat):
    old=bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old)
    me=bpy.data.meshes.new(name); bm=bmesh.new(); top=[];bot=[]
    for (x,y0,cz,y1) in rows:
        ra=[];rb=[]
        for f in (0,0.25,0.5,0.75,1):
            ye=y0+(y1+ext-y0)*f; z=cz+XF*(min(ye,y1)-y0)
            ra.append(bm.verts.new((x,ye,z))); rb.append(bm.verts.new((x,ye,z-0.25)))
        top.append(ra); bot.append(rb)
    K=len(top[0])-1
    for i in range(len(top)-1):
        for k in range(K): bm.faces.new((top[i][k],top[i+1][k],top[i+1][k+1],top[i][k+1]))
        for k in (0,K): bm.faces.new((top[i][k],bot[i][k],bot[i+1][k],top[i+1][k]))
    for e in (0,len(top)-1): bm.faces.new(tuple(top[e])+tuple(reversed(bot[e])))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    uv=me.uv_layers.new(name='UVMap')
    for l in me.loops: c=me.vertices[l.vertex_index].co; uv.data[l.index].uv=(c.x/2.0,c.y/2.0)
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o); me.materials.append(bpy.data.materials[mat]); return o
name='WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width'
w=mk(name,0.0,'Kasser_apron_concrete_cm')
hc=mk('WS72_cut_helper_hidden',1.6,'Kasser_apron_concrete_cm'); hc.hide_render=True; hc.hide_viewport=True; hc.display_type='WIRE'
# GN cut: push ground-type surfaces 6 cm under the slab
ng=bpy.data.node_groups.get('WS72_KasserSW_walk_cut') or bpy.data.node_groups.new('WS72_KasserSW_walk_cut','GeometryNodeTree')
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
sub=N.new('ShaderNodeMath'); sub.operation='SUBTRACT'; sub.inputs[1].default_value=0.06; L.new(sp.outputs['Z'],sub.inputs[0])
sp2=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp2.inputs[0])
mn=N.new('ShaderNodeMath'); mn.operation='MINIMUM'; L.new(sp2.outputs['Z'],mn.inputs[0]); L.new(sub.outputs[0],mn.inputs[1])
cb=N.new('ShaderNodeCombineXYZ'); L.new(sp2.outputs['X'],cb.inputs[0]); L.new(sp2.outputs['Y'],cb.inputs[1]); L.new(mn.outputs[0],cb.inputs[2])
st=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],st.inputs['Geometry']); L.new(rc.outputs['Is Hit'],st.inputs['Selection']); L.new(cb.outputs[0],st.inputs['Position'])
L.new(st.outputs[0],go.inputs[0])
TG=['Terrain_LiDAR_DTM_1m',OB('WS68_RHD_ground_northDTM'),'WS70_gap_strip_grass_berms','WS60_terrain_edge_apron_LiDAR_to_skirt']
for n in TG:
    o=bpy.data.objects[n]
    if 'WS72_KasserSW_walk_cut' not in o.modifiers:
        md=o.modifiers.new('WS72_KasserSW_walk_cut','NODES'); md.node_group=ng
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
Wt=bvh(name); tot=0
for n in TG:
    T=bvh(n); bad=0; c=0; mx=-9
    for (x,y0,cz,y1) in rows:
        for k in range(1,10):
            y=y0+(y1-y0)*k/10; h=dn(T,x,y); s=dn(Wt,x,y)
            if h and s:
                c+=1; mx=max(mx,h.z-s.z)
                if h.z>s.z-0.005: bad+=1
    tot+=bad; print('W72 check',n[:30],'above',bad,'/',c,'max',round(mx,3))
print('W72 total above',tot)
if os.environ.get('SAVE')=='1' and tot<15: bpy.ops.wm.save_mainfile(); print('W72 SAVED',flush=True)
