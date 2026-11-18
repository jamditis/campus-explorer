import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
W=bvh('Alexander Kasser Theater walls'); C=bvh('WS27_CollegeAve_curb_left_UNVERIFIED'); T=bvh('Terrain_LiDAR_DTM_1m')
dn=lambda t,x,y:(t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0])
X0,X1=-243.0,-214.5; rows=[]
x=X0
while x<=X1+1e-6:
    cy=None
    for i in range(400):
        y=-70+i*0.05
        if dn(C,x,y): cy=y
    cz=dn(C,x,cy).z
    hw=W.ray_cast(Vector((x,cy,cz+1.5)),Vector((0,1,0)),40)[0]
    rows.append([x,cy+0.03,cz,hw.y-0.03]); x+=0.5
# smooth curb top / edges along x
def sm(i,k=4): return lambda r:None
import statistics
for j in (1,2,3):
    vals=[r[j] for r in rows]; out=[]
    for i in range(len(vals)):
        w=vals[max(0,i-3):i+4]; out.append(sum(w)/len(w))
    for r,v in zip(rows,out): r[j]=v
S=[0.015]*len(rows)
for r in rows: r[2]+=0.01
BED=0.9
def build(name,mat,ya,yb,thick=0.25,lift=0.0):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); top=[];bot=[]
    for (x,y0,cz,y1),s in zip(rows,S):
        ra=[];rb=[]
        for f in (0,0.5,1):
            ye=ya(y0,y1)+(yb(y0,y1)-ya(y0,y1))*f; z=cz+s*(ye-y0)+lift
            ra.append(bm.verts.new((x,ye,z))); rb.append(bm.verts.new((x,ye,z-thick)))
        top.append(ra); bot.append(rb)
    for i in range(len(top)-1):
        for k in range(2):
            bm.faces.new((top[i][k],top[i+1][k],top[i+1][k+1],top[i][k+1]))
        for k in (0,2):
            a,b=(top,bot)
            bm.faces.new((top[i][k],bot[i][k],bot[i+1][k],top[i+1][k]))
    for e,k in ((0,0),(len(top)-1,0)):
        bm.faces.new((top[e][0],top[e][1],top[e][2],bot[e][2],bot[e][1],bot[e][0]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(me); bm.free()
    uv=me.uv_layers.new(name='UVMap')
    for l in me.loops: c=me.vertices[l.vertex_index].co; uv.data[l.index].uv=(c.x/2.0,c.y/2.0)
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o)
    me.materials.append(bpy.data.materials[mat]); 
    for p in me.polygons: p.use_smooth=False
    return o
w=build('WS71_Kasser_S_sidewalk_ortho2020_UNVERIFIED_width','Kasser_apron_concrete_cm',lambda a,b:a,lambda a,b:b-BED)
b=build('WS71_Kasser_S_wallfoot_mulch_bed_UNVERIFIED','Mulch_bed',lambda a,b:b-BED,lambda a,b:b,lift=-0.03)

# GN on terrain: push terrain under the walk+bed footprint below the slab
T_o=bpy.data.objects['Terrain_LiDAR_DTM_1m']
ng=bpy.data.node_groups.new('WS71_KasserS_walk_terrain_cut','GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
oi1=N.new('GeometryNodeObjectInfo'); oi1.inputs['Object'].default_value=w; oi1.transform_space='RELATIVE'
oi2=N.new('GeometryNodeObjectInfo'); oi2.inputs['Object'].default_value=b; oi2.transform_space='RELATIVE'
jg=N.new('GeometryNodeJoinGeometry'); L.new(oi1.outputs['Geometry'],jg.inputs[0]); L.new(oi2.outputs['Geometry'],jg.inputs[0])
pos=N.new('GeometryNodeInputPosition')
up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; up.inputs[1].default_value=(0,0,50); L.new(pos.outputs[0],up.inputs[0])
rc=N.new('GeometryNodeRaycast'); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=100
L.new(jg.outputs[0],rc.inputs['Target Geometry']); L.new(up.outputs[0],rc.inputs['Source Position'])
sp=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sp.inputs[0])
sub=N.new('ShaderNodeMath'); sub.operation='SUBTRACT'; sub.inputs[1].default_value=0.06; L.new(sp.outputs['Z'],sub.inputs[0])
sp2=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp2.inputs[0])
mn=N.new('ShaderNodeMath'); mn.operation='MINIMUM'; L.new(sp2.outputs['Z'],mn.inputs[0]); L.new(sub.outputs[0],mn.inputs[1])
cb=N.new('ShaderNodeCombineXYZ'); L.new(sp2.outputs['X'],cb.inputs[0]); L.new(sp2.outputs['Y'],cb.inputs[1]); L.new(mn.outputs[0],cb.inputs[2])
st=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],st.inputs['Geometry']); L.new(rc.outputs['Is Hit'],st.inputs['Selection']); L.new(cb.outputs[0],st.inputs['Position'])
L.new(st.outputs[0],go.inputs[0])
md=T_o.modifiers.new('WS71_KasserS_walk_terrain_cut','NODES'); md.node_group=ng
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
T=bvh('Terrain_LiDAR_DTM_1m')
# checks
Wt=bvh(w.name); bad=0;n=0;mx=0
for (x,y0,cz,y1) in rows:
    for k in range(1,10):
        y=y0+(y1-BED-y0)*k/10; h=dn(T,x,y); s=dn(Wt,x,y)
        if h and s:
            n+=1; mx=max(mx,h.z-s.z)
            if h.z>s.z-0.005: bad+=1
print('W71 rows',len(rows),'slope range',round(min(S),3),round(max(S),3),'terrain-above-walk',bad,'/',n,'max',round(mx,3))
print('W71 width range',round(min(r[3]-r[1] for r in rows),2),round(max(r[3]-r[1] for r in rows),2))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('W71 SAVED')
