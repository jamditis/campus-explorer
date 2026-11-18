import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
DRY=os.environ.get('DRY')=='1'
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    me=o.evaluated_get(dg).to_mesh(); w=o.matrix_world
    return BVHTree.FromPolygons([w@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
br=bpy.data.objects['WS11_Cole_SW_bed_walk_bridge_UNVERIFIED']
names=['COLE_planting_beds_smooth_bu','Footpaths_OSM','WS3_Cole_plaza_paving_20261109',br.name]+[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('OZ_walk_joints','WS12_bridge_slab_joints'))]
TS=[bvh(bpy.data.objects[n]) for n in names]
A=Vector((-86.4,-63.92,0)); B=Vector((-69.74,-68.43,0)); d=(B-A); d.z=0; d.normalize(); nrm=Vector((-d.y,d.x,0))
w=br.matrix_world; P=[]
for v in br.data.vertices:
    q=w@v.co; r=Vector((q.x,q.y,0))-A; P.append((r.dot(d),r.dot(nrm)))
tmin=min(p[0] for p in P); tmax=max(p[0] for p in P)
rows={}
WK=[]
for n in ('WS3_Cole_plaza_paving_20261109','Footpaths_OSM'):
    o=bpy.data.objects[n]; ww=o.matrix_world
    for v in o.data.vertices:
        q=ww@v.co; r=Vector((q.x,q.y,0))-A; t_,s_=r.dot(d),r.dot(nrm)
        if 0.0<t_<tmin and -2.3<s_<2.5: WK.append((round(t_*2)/2,s_))
for t,s in P+WK:
    k=round(t,2); lo,hi=rows.get(k,(9,-9)); rows[k]=(min(lo,s),max(hi,s))
ks=sorted(rows)
print('T',round(tmin,2),round(tmax,2),'rows',len(ks))
def sm(i,side):
    win=[rows[ks[j]] for j in range(max(0,i-3),min(len(ks),i+4))]
    return min(x[0] for x in win) if side<0 else max(x[1] for x in win)
# keep edging only where the bridge crosses the bed: probe bed under the edge line
TB=TS[0]
W_OUT=0.18; W_IN=0.06; Z=0.008
verts=[];faces=[];L=0
for side in (-1,1):
    line=[]
    for i,k in enumerate(ks):
        s=sm(i,side); line.append((k,s))
    # ends: skip 0.6 m at each end so it doesn't run onto the joined walks
    line=[x for x in line if x[0]<tmax-0.3]
    base=len(verts); cnt=0; segs=[]
    for t,s in line:
        for off in (-W_IN*side if False else 0,):
            pass
        si=s-side*W_IN; so=s+side*W_OUT
        pts=[]
        for ss in (si,so):
            p=A+d*t+nrm*ss; zs=[]
            for T in TS:
                h=T.ray_cast(Vector((p.x,p.y,140)),Vector((0,0,-1)),10)
                if h[0]: zs.append(h[0].z)
            pts.append(Vector((p.x,p.y,(max(zs) if zs else 134.5)+Z)))
        p=A+d*t+nrm*so; hb=TB.ray_cast(Vector((p.x,p.y,140)),Vector((0,0,-1)),10)
        if not hb[0] or hb[0].z<pts[1].z-Z-0.08:
            if cnt>=2: segs.append((base,cnt))
            base=len(verts); cnt=0; continue
        ob_=pts[1]-Vector((0,0,0.045))
        verts+= [pts[0],pts[1],ob_]; cnt+=1
    if cnt>=2: segs.append((base,cnt))
    print('SIDE',side,'SEGS',[(c) for b,c in segs],'t',round(line[0][0],2),round(line[-1][0],2))
    for base,cnt in segs:
     for i in range(cnt-1):
        a=base+3*i; b=a+3
        faces.append((a,b,b+1,a+1) if side>0 else (a,a+1,b+1,b))
        faces.append((a+1,b+1,b+2,a+2) if side>0 else (a+1,a+2,b+2,b+1))
    L+=(line[-1][0]-line[0][0]) if line else 0
print('EDGING verts',len(verts),'faces',len(faces),'len',round(L,1),'z',round(min(v.z for v in verts),3),round(max(v.z for v in verts),3))
if not DRY:
    o_=bpy.data.objects.get('WS13_Cole_SW_bridge_brick_edging_UNVERIFIED')
    if o_: bpy.data.objects.remove(o_)
    me=bpy.data.meshes.new('WS13_Cole_SW_bridge_brick_edging'); me.from_pydata(verts,[],faces); me.update()
    uv=me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        for li in poly.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            r=Vector((co.x,co.y,0))-A; uv.data[li].uv=(r.dot(d)/1.0, (r.dot(nrm)+co.z)/1.0)
    ob=bpy.data.objects.new('WS13_Cole_SW_bridge_brick_edging_UNVERIFIED',me)
    me.materials.append(bpy.data.materials['WS3_Brick_soldier_course'])
    bpy.data.collections['WS9_Cole_walk_brick_edging_20261109'].objects.link(ob)
    bpy.ops.wm.save_mainfile(); print('SAVED')
