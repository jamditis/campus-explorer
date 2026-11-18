# sd: RED HAWK COUNTRY mural — the black + white outline layers of the W (HAWK) and N (COUNTRY) had their notches
# filled solid (offset-fill error -> dark wedges). Swap the letters object to a copy of its mesh with those two letters'
# black/white faces removed, and add clean rebuilt outline slabs (red + 3.1 cm black, + 5.1 cm white, round joins,
# from data/sd/letters_rebuild.json). Original mesh kept with a fake user. REVERT=1 restores exactly.
import bpy, bmesh, json, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
o=[x for x in bpy.data.objects if x.name.startswith('MI Annex RED HAWK COUNTRY 3D letters')][0]
NEW='SD_RedHawk_W_N_outline_rebuild_UNVERIFIED'
ORIG=o.get('sd_orig_mesh')
if REV:
    if ORIG and bpy.data.meshes.get(ORIG):
        cur=o.data; o.data=bpy.data.meshes[ORIG]; o.data.use_fake_user=False
        if cur.users==0: bpy.data.meshes.remove(cur)
        del o['sd_orig_mesh']
    n=bpy.data.objects.get(NEW)
    if n: d=n.data; bpy.data.objects.remove(n); bpy.data.meshes.remove(d)
    print('SD_LETTERS reverted')
else:
    J=json.load(open('data/sd/letters_rebuild.json'))
    tx,ty=Vector((0.07,1.0)).normalized()
    if not ORIG:
        orig=o.data; orig.use_fake_user=True; o['sd_orig_mesh']=orig.name; o.data=orig.copy(); o.data.name=orig.name+'_sd'
    mw=o.matrix_world; inv=mw.inverted()
    bm=bmesh.new(); bm.from_mesh(o.data)
    kill=[]
    for f in bm.faces:
        if f.material_index not in (0,1): continue
        us=[ (mw@v.co).x*tx+(mw@v.co).y*ty for v in f.verts]
        for L in J['letters']:
            if all(L['u0']<u<L['u1'] for u in us): kill.append(f); break
    bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(o.data); bm.free(); print('SD_LETTERS removed faces',len(kill))
    # rebuilt slabs (world coords; new object at identity)
    me=bpy.data.meshes.new(NEW); bm=bmesh.new()
    def V(u,z,a,b):
        x=a+b*u; y=(u-tx*x)/ty; return bm.verts.new((x,y,z))
    for L in J['letters']:
        for ms,lay in L['layers'].items():
            m=int(ms); pf=J['planes'][ms]['front']; pb=J['planes'][ms]['back']
            for t in lay['tris']:
                fv=[V(u,z,*pf) for u,z in t]; bv=[V(u,z,*pb) for u,z in t]
                for vs,rev in ((fv,False),(bv,True)):
                    try:
                        f=bm.faces.new(vs); f.material_index=m; f.normal_update()
                        if (f.normal.x<0)==rev: f.normal_flip()
                    except ValueError: pass
            for ring in lay['rings']:
                for (u1,z1),(u2,z2) in zip(ring[:-1],ring[1:]):
                    f=bm.faces.new([V(u1,z1,*pf),V(u2,z2,*pf),V(u2,z2,*pb),V(u1,z1,*pb)]); f.material_index=m
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5)
    bm.to_mesh(me); bm.free()
    for s in o.material_slots[:2]: me.materials.append(s.material)
    n=bpy.data.objects.new(NEW,me); o.users_collection[0].objects.link(n); n['UNVERIFIED_sd']='rebuilt outline, widths measured from the other 12 letters'
    for p in me.polygons: p.use_smooth=False
    # check front orientation
    fr=sum(1 for p in me.polygons if p.normal.x<-0.9); print('SD_LETTERS new',len(me.polygons),'front-facing',fr)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
