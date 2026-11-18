"""Inspect block_base topology at door 0/2 openings; also lowest spandrel vs doors."""
import bpy, bmesh, json
from mathutils import Vector

def wv(o, co):
    return o.matrix_world @ co

BB=bpy.data.objects['TN_Blanton_block_base_UNVERIFIED']
bm=bmesh.new(); bm.from_mesh(BB.data); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
mw=BB.matrix_world

def door_basis(k):
    G=bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED'%k]
    gv=[G.matrix_world@v.co for v in G.data.vertices]
    gc=sum(gv,Vector())/len(gv)
    best=None
    for i in range(len(gv)):
        for j in range(i+1,len(gv)):
            d=gv[j]-gv[i]; d.z=0
            if best is None or d.length>best.length: best=d
    u=best.normalized(); n=Vector((-u.y,u.x,0))
    BC=Vector((141.6,450.4,0))
    if (gc-BC).to_2d().dot(n.to_2d())<0: n=-n
    half_w=max(abs((v-gc).dot(u)) for v in gv)
    zlo=min(v.z for v in gv); zhi=max(v.z for v in gv)
    return gc,u,n,half_w,zlo,zhi

report={}
for k in (0,1,2):
    gc,u,n,half_w,zlo,zhi=door_basis(k)
    faces_in=[]
    for f in bm.faces:
        c=mw@f.calc_center_median(); d=c-gc
        du=d.dot(u); dn=d.dot(n)
        if abs(du)<=half_w+0.4 and abs(dn)<=1.5:
            faces_in.append(dict(du=round(du,3),dn=round(dn,3),z=round(c.z,3),nverts=len(f.verts),
                                 nz=round((mw.to_3x3()@f.normal).z,3)))
    verts_in=[]
    for v in bm.verts:
        c=mw@v.co; d=c-gc
        if abs(d.dot(u))<=half_w+0.4 and abs(d.dot(n))<=1.5:
            verts_in.append(dict(du=round(d.dot(u),3),dn=round(d.dot(n),3),z=round(c.z,3)))
    # is there a continuous top strip (z~137.2) across |du|<half_w?
    top=[v for v in verts_in if v['z']>137.0]
    bot=[v for v in verts_in if v['z']<136.5]
    report['door_%d'%k]=dict(half_w=round(half_w,3),zlo=round(zlo,3),nfaces=len(faces_in),nverts=len(verts_in),
                              top_verts=top, bot_n=len(bot), faces_in=faces_in[:40],
                              top_du_range=([min(v['du'] for v in top), max(v['du'] for v in top)] if top else None))
    print('DOOR',k,'faces_in',len(faces_in),'verts_in',len(verts_in),'top',len(top),'top_du',report['door_%d'%k]['top_du_range'])
    for f in faces_in[:15]:
        print('  face',f)

# spandrel lowest band faces in door spans
SP=bpy.data.objects['TN_Blanton_spandrel_bands_UNVERIFIED']
sbm=bmesh.new(); sbm.from_mesh(SP.data); sbm.faces.ensure_lookup_table()
smw=SP.matrix_world
for k in (0,1,2):
    gc,u,n,half_w,zlo,zhi=door_basis(k)
    hits=[]
    for f in sbm.faces:
        c=smw@f.calc_center_median(); d=c-gc
        if abs(d.dot(u))<=half_w+0.2 and abs(d.dot(n))<=0.8 and c.z<140:
            hits.append(dict(du=round(d.dot(u),3),dn=round(d.dot(n),3),z=round(c.z,3)))
    print('SPANDREL door',k,'low faces',len(hits), hits[:10])
    report['sp_door_%d'%k]=hits

# surround vs glass: does surround solid fill behind/across glass?
for k in range(3):
    S=bpy.data.objects.get('TU_Blanton_entrance_%d_surround_UNVERIFIED'%k)
    if not S: continue
    gc,u,n,half_w,zlo,zhi=door_basis(k)
    vs=[S.matrix_world@v.co for v in S.data.vertices]
    zs=[v.z for v in vs]; dns=[(v-gc).dot(n) for v in vs]; dus=[(v-gc).dot(u) for v in vs]
    print('SURROUND',k,'z',round(min(zs),2),round(max(zs),2),'dn',round(min(dns),3),round(max(dns),3),'du',round(min(dus),2),round(max(dus),2))
    report['surround_%d'%k]=dict(z=[min(zs),max(zs)],dn=[min(dns),max(dns)],du=[min(dus),max(dus)])

# Also: is the white band maybe the BOTTOM rail of the door FRAME itself sitting too high / thick?
for k in range(3):
    F=bpy.data.objects['TJ_Blanton_entrance_%d_frame_UNVERIFIED'%k]
    G=bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED'%k]
    fv=[F.matrix_world@v.co for v in F.data.vertices]
    gv=[G.matrix_world@v.co for v in G.data.vertices]
    print('FRAME',k,'z',round(min(v.z for v in fv),3),round(max(v.z for v in fv),3),'nverts',len(fv))
    print('GLASS',k,'z',round(min(v.z for v in gv),3),round(max(v.z for v in gv),3))
    # bottom bar of frame: verts near zmin
    zmin=min(v.z for v in fv)
    bot=[v for v in fv if v.z<zmin+0.15]
    print('  frame bottom bar n',len(bot),'z~',round(zmin,3))

json.dump(report, open('/workspace/nj-scenes/montclair-state/data/vu/probe3.json','w'), indent=1)
bm.free(); sbm.free()
