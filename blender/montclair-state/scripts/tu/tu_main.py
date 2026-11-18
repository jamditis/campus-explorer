# tu (Nov 5 2026 ~5:30 AM ET, MAIN, day 8 east edge). ALL UNVERIFIED, reversible (REVERT=1).
# Blanton entrance/precast-frame clash: TN piers stood in front of TJ door bays (pier through the canopy).
# Fix: slide each clashing TJ entrance (frame+glass objects) along its wall to the centre of the nearest
# clear bay between piers; cut the TN block base out of the new door span; add a short draped concrete
# landing from the OSM footway end to the shifted door. Originals: object locations in 'tu_orig_loc',
# base mesh kept with a fake user and swapped back on revert.
import bpy, bmesh, os, json
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; DRY=os.environ.get('DRY')=='1'
def revert():
    for o in [o for o in bpy.data.objects if 'tu_obj' in o]:
        me=o.data; bpy.data.objects.remove(o)
        if me and me.users==0:
            (bpy.data.meshes if hasattr(me,'vertices') else bpy.data.cameras).remove(me)
    for o in bpy.data.objects:
        if 'tu_orig_loc' in o: o.location=Vector(o['tu_orig_loc']); del o['tu_orig_loc']
    b=bpy.data.objects.get('TN_Blanton_block_base_UNVERIFIED')
    if b and 'tu_orig_mesh' in b:
        new=b.data; b.data=bpy.data.meshes[b['tu_orig_mesh']]; b.data.use_fake_user=False; del b['tu_orig_mesh']
        if new.users==0: bpy.data.meshes.remove(new)
    c=bpy.data.collections.get('TU_blanton_entry_fix_UNVERIFIED')
    if c: bpy.data.collections.remove(c)
    print('TU reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
GN=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','RZ2_SC_LiDAR_ground_patch','QW_DTM_north_edge_ramp_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED']
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
def hit(x,y):
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
# pier islands
P=bpy.data.objects['TN_Blanton_piers_UNVERIFIED']; mw=P.matrix_world
bm=bmesh.new(); bm.from_mesh(P.data); bm.verts.ensure_lookup_table()
seen=set(); piers=[]
for v in bm.verts:
    if v.index in seen: continue
    st=[v]; isl=[]
    seen.add(v.index)
    while st:
        a=st.pop(); isl.append(mw@a.co)
        for e in a.link_edges:
            b=e.other_vert(a)
            if b.index not in seen: seen.add(b.index); st.append(b)
    c=sum(isl,Vector())/len(isl); piers.append((c,isl))
bm.free(); print('TU piers',len(piers))
summ=[]
fix=[]
fixgap=[]
BC=Vector((141.6,450.4,0))
def nside(p,n):
    return n
for k in range(3):
    F=bpy.data.objects['TJ_Blanton_entrance_%d_frame_UNVERIFIED'%k]; G=bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED'%k]
    gv=[G.matrix_world@v.co for v in G.data.vertices]
    c=sum(gv,Vector())/len(gv)
    # wall direction = horizontal axis of max extent of glass
    best=None
    for i in range(len(gv)):
        for j in range(len(gv)):
            d=gv[j]-gv[i]; d.z=0
            if best is None or d.length>best.length: best=d
    u=best.normalized(); n=Vector((-u.y,u.x,0))
    fv=[F.matrix_world@v.co for v in F.data.vertices]; fc=sum(fv,Vector())/len(fv)
    if (fc-c).dot(n)<0: n=-n
    near=[]
    for pc,isl in piers:
        d=pc-c; d.z=0
        if abs(d.dot(n))<1.5 and abs(d.dot(u))<12:
            hw=max(abs((q-pc).dot(u)) for q in isl)
            near.append((d.dot(u),hw,pc))
    near.sort(key=lambda t:t[0])
    W=2.6+0.24; CAN=2.6+1.0
    clash=[t for t in near if abs(t[0])<W/2+t[1]+0.05]
    gaps=[]
    for a,b in zip(near,near[1:]):
        lo=a[0]+a[1]; hi=b[0]-b[1]; gaps.append(((lo+hi)/2,hi-lo))
    ok=[g for g in gaps if g[1]>=CAN+0.1] or [g for g in gaps if g[1]>=W+0.1]
    tgt=min(ok,key=lambda g:abs(g[0])) if ok else None
    print('TU door',k,'c',[round(x,2) for x in c],'u',[round(x,3) for x in u],'piers near',[(round(t[0],2),round(t[1],2)) for t in near],'clash',len(clash),'target',tgt and (round(tgt[0],2),round(tgt[1],2)))
    summ.append(dict(k=k,c=list(c),u=list(u),n=list(n),clash=len(clash),shift=tgt and tgt[0],gap=tgt and tgt[1]))
    if clash and tgt: fix.append((k,F,G,c,u,n,tgt[0])); fixgap.append((k,tgt[1]))
json.dump(summ,open('data/tu/door_probe.json','w'),indent=1)
if DRY: raise SystemExit
col=bpy.data.collections.new('TU_blanton_entry_fix_UNVERIFIED'); sc.collection.children.link(col)
wm=None
for nm in ('TJ_walk_546643368_UNVERIFIED','QW_footway_546643369_ext_UNVERIFIED'):
    o=bpy.data.objects.get(nm)
    if o and o.data.materials: wm=o.data.materials[0]; break
if wm is None:
    for o in bpy.data.objects:
        if o.name.startswith('TJ_walk_') and o.data.materials: wm=o.data.materials[0]; break
# base cut
B=bpy.data.objects['TN_Blanton_block_base_UNVERIFIED']
orig=B.data; nb=orig.copy(); nb.name='TU_Blanton_block_base_doorcut_UNVERIFIED'
orig.use_fake_user=True; B['tu_orig_mesh']=orig.name; B.data=nb
bmb=bmesh.new(); bmb.from_mesh(nb); bmi=B.matrix_world.inverted()
for k,F,G,c,u,n,s in fix:
    for o in (F,G):
        o['tu_orig_loc']=list(o.location); o.location=o.location+u*s
    nc=c+u*s
    # cut base: bisect at the two door edges, delete faces between near the wall, fill ends
    half=(2.6+0.24)/2+0.02
    for sgn in (-1,1):
        p=bmi@(nc+u*half*sgn); no=(bmi.to_3x3()@u).normalized()
        geom=bmb.verts[:]+bmb.edges[:]+bmb.faces[:]
        bmesh.ops.bisect_plane(bmb,geom=geom,plane_co=p,plane_no=no)
    bmb.faces.ensure_lookup_table()
    dl=[]
    for f in bmb.faces:
        q=B.matrix_world@f.calc_center_median(); d=q-nc; d.z=0
        if abs(d.dot(u))<half and abs(d.dot(n))<1.2: dl.append(f)
    bmesh.ops.delete(bmb,geom=dl,context='FACES')
    edges=[e for e in bmb.edges if e.is_boundary]
    if edges: bmesh.ops.holes_fill(bmb,edges=edges,sides=0)
    # landing: from old door centre to new door centre, 1.8 m deep, draped, +6 cm
    g0=hit(*(c+nside(c,n)*1.0).to_2d()) or 136.8
    bml=bmesh.new(); rows=[]
    span_lo=min(0,s)-1.6; span_hi=max(0,s)+1.6
    N=max(2,int((span_hi-span_lo)/0.5))
    for i in range(N+1):
        t=span_lo+(span_hi-span_lo)*i/N; row=[]
        for dn in (0.02,0.9,1.8):
            q=c+u*t+nside(c,n)*dn; z=hit(q.x,q.y) or g0
            row.append(bml.verts.new((q.x,q.y,z+0.06)))
        row=[bml.verts.new((row[0].co.x,row[0].co.y,row[0].co.z-0.25))]+row+[bml.verts.new((row[-1].co.x,row[-1].co.y,row[-1].co.z-0.25))]
        rows.append(row)
    for a,b in zip(rows,rows[1:]):
        for j in range(len(a)-1): bml.faces.new((a[j],a[j+1],b[j+1],b[j]))
    for row in (rows[0],rows[-1]): bml.faces.new(row if True else row[::-1])
    bmesh.ops.recalc_face_normals(bml,faces=bml.faces)
    me=bpy.data.meshes.new('TU_Blanton_entrance_%d_landing_UNVERIFIED'%k); bml.to_mesh(me); bml.free()
    if wm: me.materials.append(wm)
    ob=bpy.data.objects.new(me.name,me); col.objects.link(ob); ob['tu_obj']=1
    ob['UNVERIFIED']='landing joining OSM footway end to the door moved into a clear precast bay (tu)'
    # entrance surround panel over the painted ground-storey windows in this bay (precast tone)
    gz=min((F.matrix_world@v.co).z for v in F.data.vertices)
    SP=bpy.data.objects['TN_Blanton_spandrel_bands_UNVERIFIED']
    zs=sorted((SP.matrix_world@v.co).z for v in SP.data.vertices if ((SP.matrix_world@v.co)-nc).to_2d().length<4.0)
    top=next((z for z in zs if z>gz+3.0),gz+3.6)+0.02
    gw=[t for t in fixgap if t[0]==k][0][1]-0.02
    # measure the real TI wall face across the bay (wall is not exactly parallel to the door axis)
    TI=[o for o in bpy.data.objects if o.name.startswith('TI_Blanton_Hall_313029108') and o.type=='MESH']
    ws=[]
    for i in range(9):
        su=-gw/2+0.1+(gw-0.2)*i/8
        for dz in (0.3,1.5,2.8):
            o_=nc+u*su+n*3; o_.z=gz+dz
            for ob_ in TI:
                e_=ob_.evaluated_get(dg); iw=ob_.matrix_world.inverted()
                r=e_.ray_cast(iw@o_,(iw.to_3x3()@(-n)).normalized(),distance=6)
                if r[0]: ws.append(((ob_.matrix_world@r[1])-nc).dot(n))
    front=(max(ws) if ws else -0.035)+0.012
    for o in (F,G): o.location=o.location+n*(front+0.072)
    print('TU wall offsets door',k,'min %.3f max %.3f n=%d'%(min(ws),max(ws),len(ws)) if ws else 'none','door pushed out %.3f'%(front+0.072))
    bmp=bmesh.new(); vs=[]
    for su in (-gw/2,gw/2):
        for sn_ in (-0.2,front):
            for z in (gz-0.15,top):
                q=nc+u*su+nside(nc,n)*sn_; vs.append(bmp.verts.new((q.x,q.y,z)))
    bmesh.ops.convex_hull(bmp,input=vs)
    me=bpy.data.meshes.new('TU_Blanton_entrance_%d_surround_UNVERIFIED'%k); bmp.to_mesh(me); bmp.free()
    me.materials.append(SP.data.materials[0])
    ob=bpy.data.objects.new(me.name,me); col.objects.link(ob); ob['tu_obj']=1
    ob['UNVERIFIED']='plain precast entrance surround in the door bay (hides painted ground-storey windows); design guessed'
    print('TU fixed door',k,'shift',round(s,2),'surround w',round(gw,2),'z',round(gz,2),round(top,2))
bmb.to_mesh(nb); bmb.free()
# camera: front of door 0 (south) at eye level
c0=summ[0]; cc=Vector(c0['c'])+Vector(c0['u'])*(c0['shift'] or 0); nn=Vector(c0['n'])
if nn.dot(Vector((150,418,0))-Vector((cc.x,cc.y,0)))<0: nn=-nn
loc=cc+nn*14+Vector(c0['u'])*-5; loc.z=(hit(loc.x,loc.y) or 137)+1.65
cd=bpy.data.cameras.new('TU_CAM_closeup_Blanton_S_entrance_bay'); cd.lens=32; cd.clip_end=30000
co=bpy.data.objects.new(cd.name,cd); col.objects.link(co); co['tu_obj']=1; co.location=loc
d=(cc+Vector((0,0,1.8)))-loc; co.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
print('TU cam',[round(x,1) for x in loc])
c2=summ[2]; cc=Vector(c2['c'])+Vector(c2['u'])*(c2['shift'] or 0); nn=nside(cc,Vector(c2['n']))
loc=cc+nn*15+Vector(c2['u'])*-6; loc.z=(hit(loc.x,loc.y) or 137)+1.65
cd=bpy.data.cameras.new('TU_CAM_eye_Blanton_W_entrances'); cd.lens=28; cd.clip_end=30000
co=bpy.data.objects.new(cd.name,cd); col.objects.link(co); co['tu_obj']=1; co.location=loc
d=(cc+Vector((0,0,2.2)))-loc; co.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
print('TU cam2',[round(x,1) for x in loc])
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
