# ov (Oct 31 2026 ~11:30 PM ET): see-through slots in the oo context-wall skirts (e.g. the two black slots between CELS volumes in the
# OR CELS eye view). The oo skirt builder skipped some footprint segments (jogs/corners), so below the floating OSM wall bottom there was
# no face and the hollow shell showed its far inside wall ~55 m away. Fix (ALL UNVERIFIED, new objects only, nothing existing edited):
# for every OO_skirt_* object, each wall footprint segment whose wall bottom floats >0.25 m over the DTM and has no skirt face gets a
# filler quad (same skirt material) from the wall bottom down to DTM-0.30, plus a base-course box (OR material, DTM-0.22..+0.42, 6 cm proud).
# Collection OV_skirt_gapfill_20261031ov; cam OV_CAM_closeup_CELS_skirt_gapfill. REVERT=1 removes all of it.
import bpy, os, sys, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CC='OV_skirt_gapfill_20261031ov'
c=bpy.data.collections.get(CC)
if c:
    for o in list(c.objects):
        d=o.data; bpy.data.objects.remove(o)
        if d is not None:
            (bpy.data.cameras if isinstance(d,bpy.types.Camera) else bpy.data.meshes).remove(d)
    bpy.data.collections.remove(c)
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; dg=bpy.context.evaluated_depsgraph_get()
e=ter.evaluated_get(dg); tm=e.to_mesh(); mw=ter.matrix_world
bt=BVHTree.FromPolygons([mw@v.co for v in tm.vertices],[p.vertices[:] for p in tm.polygons]); e.to_mesh_clear()
def dtm(x,y):
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),900); return h[0].z if h[0] else None
col=bpy.data.collections.new(CC); bpy.context.scene.collection.children.link(col)
tot=0; report=[]
for sk in [o for o in bpy.data.objects if o.name.startswith('OO_skirt_') and o.type=='MESH']:
    wn=sk.name[len('OO_skirt_'):]; w=bpy.data.objects.get(wn)
    if not w: print('NOWALL',sk.name); continue
    sm=sk.matrix_world; sme=sk.data
    have=[]
    for p in sme.polygons:
        q=[(sm@sme.vertices[i].co).xy for i in p.vertices]
        xy=[]
        for v in q:
            if all((v-u).length>0.03 for u in xy): xy.append(v)
        if len(xy)==2: have.append((xy[0].copy(),xy[1].copy()))
    def covered(a,b):
        a=Vector(a); b=Vector(b)
        for u,v in have:
            if ((u-a).length<0.08 and (v-b).length<0.08) or ((u-b).length<0.08 and (v-a).length<0.08): return True
        return False
    # base-course material from the OR object of this building, if any
    bcm=None
    for o in bpy.data.objects:
        if o.name.startswith('OR_base_course_') and wn.startswith(o.name[len('OR_base_course_'):]) and o.data.materials: bcm=o.data.materials[0]; break
    wm=w.matrix_world; wme=w.data
    V=[];F=[];FB=[];VB=[]; n_seg=0
    segs={}
    for p in wme.polygons:
        if abs(p.normal.z)>0.2: continue
        pts=[wm@wme.vertices[i].co for i in p.vertices]
        d={}
        for q in pts:
            k=(round(q.x,2),round(q.y,2)); d[k]=min(d.get(k,1e9),q.z)
        if len(d)!=2: continue
        (a,za),(b,zb)=sorted(d.items()); key=(a,b)
        if key in segs:
            s0=segs[key]; segs[key]=(min(s0[0],za),min(s0[1],zb),s0[2])
        else: segs[key]=(za,zb,p.normal.copy())
    for (a,b),(za,zb,pn) in segs.items():
        if covered(a,b): continue
        ga=dtm(*a); gb=dtm(*b)
        if ga is None or gb is None: continue
        if min(za-ga,zb-gb)<0.25: continue
        n=(wm.to_3x3()@pn); n.z=0; n.normalize()
        A=Vector((a[0],a[1],0)); Bv=Vector((b[0],b[1],0))
        i0=len(V); V+= [Vector((A.x,A.y,za+0.02)),Vector((A.x,A.y,ga-0.30)),Vector((Bv.x,Bv.y,gb-0.30)),Vector((Bv.x,Bv.y,zb+0.02))]
        f=[i0,i0+1,i0+2,i0+3]
        fn=(V[i0+1]-V[i0]).cross(V[i0+3]-V[i0]).normalized()
        if fn.dot(n)<0: f=f[::-1]
        F.append(f); n_seg+=1
        # base course box (6 cm proud, 25 cm deep into the wall)
        if bcm:
            o1=n*0.06; o2=-n*0.25; j=len(VB)
            for (P,g) in ((A,ga),(Bv,gb)):
                for off in (o1,o2):
                    VB.append(Vector((P.x+off.x,P.y+off.y,g-0.22))); VB.append(Vector((P.x+off.x,P.y+off.y,g+0.42)))
            # verts: A_out_bot0 A_out_top1 A_in_bot2 A_in_top3 B_out_bot4 B_out_top5 B_in_bot6 B_in_top7
            for q in ((0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5),(1,5,7,3),(0,2,6,4)): FB.append([j+x for x in q])
    if not F: continue
    me=bpy.data.meshes.new('OV_gapfill_'+wn[:40]); me.from_pydata(V,[],F); me.update()
    me.materials.append(sme.materials[0] if sme.materials else None)
    ob=bpy.data.objects.new('OV_gapfill_'+wn[:40],me); col.objects.link(ob); ob['UNVERIFIED']='ov skirt gap fill (oo skirt skipped these segments)'
    # flat UVs so the stucco texture maps like the skirt (u along wall, v=z)
    uv=me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        vs=[me.vertices[i].co for i in poly.vertices]; o0=vs[0]
        t=(vs[3]-vs[0]) if (vs[3]-vs[0]).xy.length>0.01 else (vs[2]-vs[1]); t.z=0; t.normalize()
        for li,vi in zip(poly.loop_indices,poly.vertices):
            co=me.vertices[vi].co; uv.data[li].uv=((co-o0).dot(t)*0.25,co.z*0.25)
    if FB:
        mb=bpy.data.meshes.new('OV_gapfill_base_'+wn[:36]); mb.from_pydata(VB,[],FB); mb.update()
        bm=bmesh.new(); bm.from_mesh(mb); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mb); bm.free()
        mb.materials.append(bcm); obb=bpy.data.objects.new('OV_gapfill_base_'+wn[:36],mb); col.objects.link(obb); obb['UNVERIFIED']='ov base course on gap fill'
    tot+=n_seg; report.append((wn,n_seg,bool(bcm))); print('FILL',wn,n_seg,'bcmat',bcm.name if bcm else None)
# close-up cam on the CELS east jog slot
cd=bpy.data.cameras.new('OV_CAM_closeup_CELS_skirt_gapfill'); cd.lens=30
cam=bpy.data.objects.new('OV_CAM_closeup_CELS_skirt_gapfill',cd); col.objects.link(cam)
tgt=Vector((127.3,196.1,131.8)); g=dtm(136.0,193.0) or 129.0; cam.location=Vector((136.0,192.5,g+1.65))
cam.rotation_euler=(tgt-cam.location).to_track_quat('-Z','Y').to_euler()
print('TOTAL',tot,report)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
