# qt (2): Richardson ground-storey base plinth. The glass on the 1.2 m inset line stops at z 136.6 while the
# qq apron on the east/south side lies at ~136.1-136.4, so there was a 0.2-0.5 m see-under slot into the terrain
# hole under the building (black band in QP_CAM_eye_richardson_from_SE). Adds a 0.15 m concrete upstand on the
# inset line, 3 cm proud of the glass, z 134.8 -> 136.66, skipping the two door spans. UNVERIFIED. REVERT=1 removes it.
import bpy,bmesh,json,os,math
from mathutils import Vector
NAME='QT_Richardson_base_plinth_UNVERIFIED'
o=bpy.data.objects.get(NAME)
if o:
    me=o.data; bpy.data.objects.remove(o,do_unlink=True)
    if me.users==0: bpy.data.meshes.remove(me)
    print('QTP reverted')
if os.environ.get('REVERT')=='1':
    if os.environ.get('QTSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
P=json.load(open('data/qp/rich_poly.json')); IN=[Vector((x,y,0)) for x,y in P['inset']]
cen=Vector((sum(v.x for v in IN)/len(IN),sum(v.y for v in IN)/len(IN),0))
# door boxes from qq objects
boxes=[]
qq=bpy.data.collections.get('QQ_Richardson_entries_UNVERIFIED')
for ob in (qq.all_objects if qq else []):
    if ob.type=='MESH' and any(k in ob.name.lower() for k in ('door','leaf','threshold')):
        cs=[ob.matrix_world@Vector(c) for c in ob.bound_box]
        boxes.append((min(c.x for c in cs)-0.15,max(c.x for c in cs)+0.15,min(c.y for c in cs)-0.15,max(c.y for c in cs)+0.15)); print('QTP door obj',ob.name,[round(b,2) for b in boxes[-1]])
DOORS=[(74.64,242.13),(79.95,290.37)]  # qq door centres (OSM footway ends)
def indoor(x,y): return any(math.hypot(x-dx,y-dy)<1.4 for dx,dy in DOORS)
bm=bmesh.new(); Z0,Z1=134.8,136.66; T=0.15; G=0.03; nseg=0; nskip=0
for i in range(len(IN)):
    a,b=IN[i],IN[(i+1)%len(IN)]; e=b-a; L=e.length
    if L<0.05: continue
    t=e/L; n=Vector((t.y,-t.x,0))
    if n.dot(((a+b)/2)-cen)<0: n=-n
    k=max(1,int(L/0.25))
    for j in range(k):
        p=a+t*(L*j/k); q=a+t*(L*(j+1)/k); m=(p+q)/2
        if indoor(m.x,m.y): nskip+=1; continue
        po,qo=p+n*(G+T),q+n*(G+T); pi_,qi=p+n*G,q+n*G
        V=[bm.verts.new((v.x,v.y,z)) for v in (pi_,qi,qo,po) for z in (Z0,Z1)]
        # V: 0 pi lo,1 pi hi,2 qi lo,3 qi hi,4 qo lo,5 qo hi,6 po lo,7 po hi
        for f in ((6,4,5,7),(1,3,5,7)[::-1],(0,2,3,1)[::-1]):
            bm.faces.new([V[x] for x in f])
        nseg+=1
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
bm.normal_update()
for f in bm.faces:
    c=f.calc_center_median(); v=c-cen; v.z=0
    if abs(f.normal.z)<0.5 and f.normal.dot(v)<0 and (c-cen).length>0: pass
uv=bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    for l in f.loops: l[uv].uv=(l.vert.co.x+l.vert.co.y,l.vert.co.z)
me=bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
mat=bpy.data.materials.get('QQ_Richardson_apron_curb_concrete'); me.materials.append(mat)
o=bpy.data.objects.new(NAME,me); o['UNVERIFIED_qt']='base upstand under the ground-storey glass; closes see-under slot; design generic'
c=bpy.data.collections.get('QT_Richardson_walk_soil_edge_UNVERIFIED') or bpy.context.scene.collection; c.objects.link(o)
print('QTP segs',nseg,'skipped',nskip,'mat',mat.name if mat else None)
if os.environ.get('QTSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
