# ws130 self-review fix 2: (a) lawn z-fight at the wall: proxy still held drive faces inside the wall -> removed; terrain under the
# drive pushed 15 cm under. (b) LiDAR class map shows a planted island x -189..-184.5, y -247.3..-250.5 (high-intensity ground)
# exactly where a tree trunk stood on bare asphalt -> curbed tree island (lawn) centred on the trunk, asphalt removed inside.
import bpy, bmesh, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
xFm=lambda y:-197.43+(y+227.0)*0.2433
xE=lambda y:-192.6+(y+235.0)*0.19
px=bpy.data.objects.get('WS113_paving_tops_proxy'); pw=px.matrix_world
pbm=bmesh.new(); pbm.from_mesh(px.data)
k=[f for f in pbm.faces if (lambda c:-229.4<c.y<-210.5 and -201<c.x<xFm(c.y)-0.3)(pw@f.calc_center_median())]
bmesh.ops.delete(pbm,geom=k,context='FACES'); pbm.to_mesh(px.data); pbm.free(); print('M130c proxy faces removed',len(k))
dr=[o for o in bpy.data.objects if o.name.startswith('WS130_Chapin_E_service_drive')][0]
TD=BVHTree.FromPolygons([v.co for v in dr.data.vertices],[p.vertices for p in dr.data.polygons if p.normal.z>0.5])
def zd(x,y):
    h=TD.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]; return None if h is None else h.z
n=0
for g in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'))]:
    gw=g.matrix_world; gi=gw.inverted()
    for v in g.data.vertices:
        p=gw@v.co
        if not (-201.5<p.x<-180 and -256<p.y<-210.5): continue
        zs=[z for z in (zd(p.x+dx,p.y+dy) for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5))) if z is not None]
        if p.x<xFm(p.y)+0.5 and p.y>-229.6 and p.x<xE(p.y):
            zs=zs or [None]
        if zs and zs[0] is not None and p.z>min(zs)-0.15: p.z=min(zs)-0.15; v.co=gi@p; n+=1
print('M130c terrain pushed',n)
# tree island
cands=[]
for o in bpy.data.objects:
    if o.type in ('MESH','EMPTY') and (o.name.startswith(('T_','Tree')) or 'tree' in o.name.lower()):
        l=o.matrix_world.translation
        if -191<l.x<-182 and -252<l.y<-245: cands.append((o.name,round(l.x,2),round(l.y,2),round(l.z,2)))
print('M130c trees near island',cands)
cx,cy=-186.7,-248.9   # LiDAR high-intensity ground island (not the L1 crown-derived tree point)
rx,ry=2.0,1.5
for nme,_,_,_ in cands:
    t=bpy.data.objects[nme]; old=t.location.copy(); t.location.x=cx; t.location.y=cy+0.2
    print('M130c moved tree',nme,'from',tuple(round(c,2) for c in old),'to',tuple(round(c,2) for c in t.location))
bm=bmesh.new(); bm.from_mesh(dr.data)
inside=lambda x,y:((x-cx)/rx)**2+((y-cy)/ry)**2<1.0
kill=[f for f in bm.faces if f.normal.z<0.5]+[f for f in bm.faces if f.normal.z>=0.5 and inside(*f.calc_center_median().xy)]
nk=len(kill); bmesh.ops.delete(bm,geom=kill,context='FACES'); bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
for ed in [ed for ed in bm.edges if ed.is_boundary]:
    a,b=ed.verts; a2=bm.verts.new(a.co-Vector((0,0,0.12))); b2=bm.verts.new(b.co-Vector((0,0,0.12))); bm.faces.new((a,b,b2,a2))
bm.to_mesh(dr.data); bm.free(); dr.data.update()
TD=BVHTree.FromPolygons([v.co for v in dr.data.vertices],[p.vertices for p in dr.data.polygons if p.normal.z>0.5])
cm=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED'); lm=bpy.data.materials.get('COLE_lawn_post2020_bs')
N=48; zs=[]
for i in range(N):
    a=2*np.pi*i/N; x=cx+(rx+0.25)*np.cos(a); y=cy+(ry+0.25)*np.sin(a); z=zd(x,y); zs.append(z)
zs=np.array([z for z in zs if z is not None]); zc=float(np.median(zs))
for nme,_,_,_ in cands: bpy.data.objects[nme].location.z=zc+0.10; print('M130c tree z',round(zc+0.10,2))
bm=bmesh.new(); rings=[]
for i in range(N):
    a=2*np.pi*i/N; ca,sa=np.cos(a),np.sin(a)
    xo=cx+(rx+0.02)*ca; yo=cy+(ry+0.02)*sa; zo=zd(cx+(rx+0.3)*ca,cy+(ry+0.3)*sa) or zc
    xi=cx+(rx-0.13)*ca; yi=cy+(ry-0.13)*sa
    rings.append([bm.verts.new((xo,yo,zo-0.2)),bm.verts.new((xo,yo,zo+0.14)),bm.verts.new((xi,yi,zo+0.14)),bm.verts.new((xi,yi,zo-0.2))])
for i in range(N):
    r0,r1=rings[i],rings[(i+1)%N]
    for j in range(3): bm.faces.new((r0[j],r1[j],r1[j+1],r0[j+1]))
m=bpy.data.meshes.new('WS130_island_curb'); bm.normal_update(); bm.to_mesh(m); bm.free(); m.materials.append(cm)
col=bpy.data.collections['WS130_Chapin_E_drive']
for o in [o for o in bpy.data.objects if o.name.startswith('WS130_tree_island')]: bpy.data.objects.remove(o)
co=bpy.data.objects.new('WS130_tree_island_curb_LiDAR2023int_UNVERIFIEDshape',m); col.objects.link(co)
# lawn top: polar grid, 3 cm under the curb top, slightly domed
bm=bmesh.new(); ctr=bm.verts.new((cx,cy,zc+0.13)); prev=None; R=[]
for k2 in (1,2,3):
    t=k2/3; R.append([bm.verts.new((cx+(rx-0.13)*t*np.cos(2*np.pi*i/N),cy+(ry-0.13)*t*np.sin(2*np.pi*i/N),zc+0.13-0.02*t)) for i in range(N)])
for i in range(N): bm.faces.new((ctr,R[0][i],R[0][(i+1)%N]))
for r0,r1 in zip(R[:-1],R[1:]):
    for i in range(N): bm.faces.new((r0[i],r1[i],r1[(i+1)%N],r0[(i+1)%N]))
m2=bpy.data.meshes.new('WS130_island_lawn'); bm.normal_update()
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
bm.to_mesh(m2); bm.free(); m2.materials.append(lm)
lo=bpy.data.objects.new('WS130_tree_island_lawn_LiDAR2023int_UNVERIFIEDsurface',m2); col.objects.link(lo)
print('M130c island at',cx,cy,'zc %.2f'%zc,'asphalt faces removed',nk)
if SAVE: bpy.ops.wm.save_mainfile(); print('M130c SAVED')
