# Session ef (Oct 21 2026 ~7:35 PM ET): Commons photo "School of Communications.jpg" (2021, CC BY-SA 4.0) shows a mulch
# bed with white-flowering shrubs along the base of CCOM's tower west face, left of the entrance bins; the model had lawn.
# Adds 'CCOM tower west mulch bed (ef)' (draped on the DTM +4 cm, 1.6 m deep with a soft wavy edge; depth/extent by eye
# from the photo, UNVERIFIED) + 6 linked copies of 'dJ whiteflower shrub 00' (species UNVERIFIED), collection
# 'CCOM_tower_bed_20261021ef'. Grass points inside the bed (+0.15 m) are sunk 1 m (orig z in point attr ef_orig_z).
# SAVE=1 saves; REVERT=1 undoes.
import bpy, bmesh, os, re, math, mathutils
from mathutils import Vector
from mathutils.bvhtree import BVHTree
CN='CCOM_tower_bed_20261021ef'
REV=os.environ.get('REVERT')=='1'
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
tb=bmesh.new(); tb.from_mesh(ter.data); tb.transform(ter.matrix_world); tbvh=BVHTree.FromBMesh(tb)
def gz(x,y):
    h=tbvh.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return h[0].z if h[0] else 137.4
A=Vector((-20.0,18.3)); B=Vector((-18.3,24.99)); L=(B-A).length; u=(B-A)/L; n=Vector((-u.y,u.x))
if n.x>0: n=-n   # outward = west
T0,T1=-0.85,L+0.15
def depth(t): return 1.9+0.18*math.sin(t*1.3)+0.10*math.sin(t*3.1+1.0)
def outline():
    pts=[]
    for i in range(41):
        t=T0+(T1-T0)*i/40; pts.append(A+u*t+n*depth(t))
    return pts
def in_bed(x,y,pad=0.0):
    p=Vector((x,y))-A; t=p.dot(u); d=p.dot(n)
    return T0-pad<=t<=T1+pad and -0.3<=d<=depth(t)+pad
grass=[o for o in bpy.data.objects if o.type=='MESH' and re.match(r'(?i)^(dS_grass|cx_grass|cd_grass|Lawn_grass_instanced)',o.name)]
if REV:
    if CN in bpy.data.collections:
        c=bpy.data.collections[CN]
        for o in list(c.objects): bpy.data.objects.remove(o)
        bpy.data.collections.remove(c)
    for o in grass:
        a=o.data.attributes.get('ef_orig_z')
        if a:
            for v,d in zip(o.data.vertices,a.data):
                if d.value>-9000: v.co.z=d.value
            o.data.attributes.remove(a); o.data.update()
    print('EF_BED_REVERTED')
else:
    if CN in bpy.data.collections:
        c=bpy.data.collections[CN]
        for o in list(c.objects): bpy.data.objects.remove(o)
    else:
        c=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(c)
    # bed mesh: grid (t, s) with s in [-0.1, depth]
    NT,NS=60,8; verts=[]; faces=[]
    for i in range(NT+1):
        t=T0+(T1-T0)*i/NT; dmax=depth(t)
        for j in range(NS+1):
            s=-0.1+(dmax+0.1)*j/NS; p=A+u*t+n*s
            verts.append((p.x,p.y,gz(p.x,p.y)+0.04 - (0.02 if j==NS else 0)))
    for i in range(NT):
        for j in range(NS):
            a=i*(NS+1)+j; faces.append((a,a+NS+1,a+NS+2,a+1))
    # small rim skirt on the outer edge
    base=len(verts)
    for i in range(NT+1):
        x,y,z=verts[i*(NS+1)+NS]; verts.append((x,y,z-0.12))
    for i in range(NT):
        o0=i*(NS+1)+NS; o1=(i+1)*(NS+1)+NS; faces.append((o0,base+i,base+i+1,o1))
    me=bpy.data.meshes.new('CCOM tower west mulch bed (ef)'); me.from_pydata(verts,[],faces)
    src=bpy.data.objects.get('dJ Sprague bed wrap mulch') or bpy.data.objects.get('Morehead west planting bed (mulch)')
    me.materials.append(src.data.materials[0]); print('EF mulch mat',src.data.materials[0].name)
    for p in me.polygons: p.use_smooth=True
    bed=bpy.data.objects.new(me.name,me); c.objects.link(bed); bed['ef_tower_bed']=1
    # ef v2: dense Shrub_Azalea collection instances (asset library, geonodes leaf scatter) form the shrub mass, with
    # a few 'dJ whiteflower shrub 00' copies tucked in for the photo's white flower heads (species UNVERIFIED).
    az=bpy.data.collections['Shrub_Azalea']; azo=bpy.data.objects['Shrub_Azalea']
    zmin=min((azo.matrix_world@Vector(v)).z for v in azo.bound_box)-az.instance_offset.z; Haz=azo.dimensions.z
    for k,(t,s,h,w) in enumerate([(0.2,0.85,0.8,1.2),(1.3,1.05,0.95,1.45),(2.5,0.95,0.85,1.3),(3.7,1.1,1.0,1.5),(4.9,0.95,0.85,1.25),(6.0,0.9,0.75,1.15),(0.9,1.65,0.45,0.8),(3.1,1.75,0.5,0.85),(5.4,1.7,0.42,0.75)]):
        p=A+u*t+n*s; e=bpy.data.objects.new(f'ef tower bed shrub {k:02d} (Shrub_Azalea; UNVERIFIED)',None)
        e.instance_type='COLLECTION'; e.instance_collection=az
        sz=h/Haz; sw=w/azo.dimensions.x
        e.scale=(sw,sw*(0.9+0.1*(k%2)),sz); e.rotation_euler=(0,0,k*2.1)
        e.location=(p.x,p.y,gz(p.x,p.y)); c.objects.link(e); e['ef_target']=(p.x,p.y,gz(p.x,p.y)+0.03)
    # asset sits away from origin (dI2 gotcha): measure each instance's core bbox after evaluation and shift it onto its target
    bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
    seen={}
    for inst in dg.object_instances:
        if inst.is_instance and inst.parent and inst.parent.name.startswith('ef tower bed shrub') and inst.object.name=='Shrub_Azalea':
            bb=[inst.matrix_world@Vector(cc) for cc in inst.object.bound_box]
            mn=Vector((min(b.x for b in bb),min(b.y for b in bb),min(b.z for b in bb))); mx=Vector((max(b.x for b in bb),max(b.y for b in bb),max(b.z for b in bb)))
            if (mx-mn).length>0.3: seen[inst.parent.name]=(mn,mx)
    for nm,(mn,mx) in seen.items():
        e=bpy.data.objects[nm]; t=Vector(e['ef_target']); cxy=(mn+mx)/2
        e.location=e.location+Vector((t.x-cxy.x,t.y-cxy.y,t.z-mn.z))
    print('EF shrub instances placed',len(seen))
    sh=bpy.data.objects['dJ whiteflower shrub 00']; H=sh.dimensions.z
    for k,(t,s,h) in enumerate([(0.75,0.75,1.3),(2.0,0.9,1.4),(3.2,0.8,1.45),(4.4,0.95,1.35),(5.6,0.85,1.25),(1.5,1.35,1.0),(3.9,1.45,1.05)]):
        p=A+u*t+n*s; o=sh.copy(); o.name=f'ef tower bed whiteflower {k:02d} (photo; species UNVERIFIED)'
        sc=h/H; o.scale=(sh.scale.x*sc*1.3, sh.scale.y*sc*1.3, sh.scale.z*sc); o.rotation_euler=(0,0,k*1.7)
        zb=min((sh.matrix_world@Vector(b)).z for b in sh.bound_box)-sh.location.z
        o.location=(p.x,p.y,gz(p.x,p.y)+0.02-zb*sc)
        for cc in list(o.users_collection): cc.objects.unlink(o)
        c.objects.link(o)
    tot=0
    for o in grass:
        me=o.data; mw=o.matrix_world; inv=mw.inverted()
        a=me.attributes.get('ef_orig_z')
        if a is None:
            a=me.attributes.new('ef_orig_z','FLOAT','POINT'); a.data.foreach_set('value',[-9999.0]*len(me.vertices))
        k=0
        for i,v in enumerate(me.vertices):
            w=mw@v.co
            if abs(w.x+19)>9 or abs(w.y-21)>9: continue
            if in_bed(w.x,w.y,0.15) and a.data[i].value<-9000:
                a.data[i].value=v.co.z; v.co.z=(inv@Vector((w.x,w.y,w.z-1.0))).z; k+=1
        me.update(); tot+=k
        if k: print('EF grass sunk',o.name,k)
    print('EF_BED_APPLIED faces',len(faces),'grass sunk',tot)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('EF_SAVED')
