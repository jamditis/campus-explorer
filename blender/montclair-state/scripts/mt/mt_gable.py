# Session mt (Oct 29 2026): CCOM west entrance pavilion top per MontclairCCOM FB photos (Oct 27 2026):
# white stucco gable with red-brown rake + round medallion, tan band only around the arch (jambs + archivolt), no flat tan cornice.
# Shape from photos; all dimensions UNVERIFIED (gable base/apex scaled against the tower window and sign).
import bpy, bmesh, math
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
def P(u,z,w): v=t*u+n*w; return Vector((v.x,v.y,z))
U0,U1=3.197,10.397; UC=(U0+U1)/2; HW=(U1-U0)/2
WF,WB=22.693,22.211
ZS=143.612; ZB=147.9; ZA=150.35
M=bpy.data.materials
col=bpy.data.collections.new('MS_CCOM_entrance_gable_20261029mt'); bpy.context.scene.collection.children.link(col)
sup=bpy.data.collections.new('MT_superseded_CCOM_entrance_flat_top'); bpy.context.scene.collection.children.link(sup)
def mk(name,verts,faces,mat,shadow=True):
    me=bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts],[],faces); me.update()
    me.materials.append(M[mat]); o=bpy.data.objects.new(name,me); col.objects.link(o)
    o['status']='shape from MontclairCCOM FB photos Oct 27 2026; dims UNVERIFIED (session mt)'
    for p in me.polygons: p.use_smooth=False
    return o
def box(name,quad_front,w0,w1,mat):
    # quad_front: list of (u,z) polygon; extruded from w0 (back) to w1 (front)
    k=len(quad_front); vs=[P(u,z,w1) for u,z in quad_front]+[P(u,z,w0) for u,z in quad_front]
    fs=[list(range(k)),list(range(2*k-1,k-1,-1))]+[[i,(i+1)%k,k+(i+1)%k,k+i] for i in range(k)]
    return mk(name,vs,fs,mat)
# 1) spandrel -> white stucco, cut top to gable base
sp=bpy.data.objects['CCOM entrance spandrel (outer)']
sp.data.materials[0]=M['Wall_SCM_precast']
mi=sp.matrix_world.inverted(); mw=sp.matrix_world
for v in sp.data.vertices:
    g=mw@v.co
    if g.z>ZB+0.01: g.z=ZB; v.co=mi@g
sp.data.update()
# 2) piers end at the arch springing
for nm in ['CCOM entrance pier -1','CCOM entrance pier +1']:
    o=bpy.data.objects[nm]; mi=o.matrix_world.inverted(); mw=o.matrix_world
    for v in o.data.vertices:
        g=mw@v.co
        if g.z>ZS+0.01: g.z=ZS; v.co=mi@g
    o.data.update()
# 3) flat cornice superseded
c=bpy.data.objects['CCOM entrance cornice']
for cc in list(c.users_collection): cc.objects.unlink(c)
sup.objects.link(c); c.hide_render=True; c.hide_viewport=True
sup.hide_render=True
# 4) tan jambs + archivolt (U band), slightly proud of the stucco
R1,R2=2.9,3.6; WFa=WF+0.035; WBa=WF-0.10; N=24
outer=[(UC-R2,137.412)]+[(UC-R2*math.cos(math.pi*i/N),ZS+R2*math.sin(math.pi*i/N)) for i in range(N+1)]+[(UC+R2,137.412)]
inner=[(UC+R1,137.412)]+[(UC+R1*math.cos(math.pi*i/N),ZS+R1*math.sin(math.pi*i/N)) for i in range(N+1)][::-1]+[(UC-R1,137.412)]
# build as strip of quads
ring_o=[(UC-R2*math.cos(math.pi*i/N),ZS+R2*math.sin(math.pi*i/N)) for i in range(N+1)]
ring_i=[(UC-R1*math.cos(math.pi*i/N),ZS+R1*math.sin(math.pi*i/N)) for i in range(N+1)]
po=[(UC-R2,137.412)]+ring_o+[(UC+R2,137.412)]
pi_=[(UC-R1,137.412)]+ring_i+[(UC+R1,137.412)]
K=len(po); vs=[]
for (u,z) in po: vs.append(P(u,z,WFa))
for (u,z) in pi_: vs.append(P(u,z,WFa))
for (u,z) in po: vs.append(P(u,z,WBa))
for (u,z) in pi_: vs.append(P(u,z,WBa))
fs=[]
for i in range(K-1):
    fs.append([i,i+1,K+i+1,K+i])                       # front
    fs.append([2*K+K+i,2*K+K+i+1,2*K+i+1,2*K+i])        # back
    fs.append([2*K+i,2*K+i+1,i+1,i])                    # outer edge
    fs.append([K+i,K+i+1,2*K+K+i+1,2*K+K+i])            # inner edge (soffit)
fs.append([0,K,3*K,2*K]); fs.append([K-1,2*K+K-1,3*K+K-1-K+K-1-(K-1) if False else 4*K-1,2*K-1])
mk('CCOM entrance archivolt + jambs (tan, mt)',vs,fs,'Cast_stone_tan')
# keystone pulled proud of the archivolt
ks=bpy.data.objects['CCOM entrance keystone']; ks.location+=n*0.06
# 5) gable wall (white stucco prism into the building)
WIN=18.7
box('CCOM entrance gable wall (stucco, mt)',[(U0,ZB),(U1,ZB),(UC,ZA)],WIN,WF,'Wall_SCM_precast')
# 6) rake fascia boards + tile roof slabs
pitch=math.atan2(ZA-ZB,HW); OV=0.35; FD=0.30; FT=0.13
for side,s in (('S',-1),('N',1)):
    # fascia: along rake from eave end (overhang past corner) to apex, sitting on the rake line
    ue=UC+s*(HW+OV*math.cos(pitch)); ze=ZB-OV*math.sin(pitch)
    a=(ue,ze-0.05); b=(UC,ZA-0.05)
    up=FD/math.cos(pitch)
    quad=[a,b,(b[0],b[1]+up),(a[0],a[1]+up)] if s<0 else [b,a,(a[0],a[1]+up),(b[0],b[1]+up)]
    box('CCOM entrance gable rake fascia %s (mt)'%side,quad,WIN,WF+0.40,'Eave_fascia_dark_wood')
    # roof slab on top of fascia
    zt=0.10/math.cos(pitch)
    a2=(a[0],a[1]+up); b2=(b[0],b[1]+up)
    quad=[a2,b2,(b2[0],b2[1]+zt),(a2[0],a2[1]+zt)] if s<0 else [b2,a2,(a2[0],a2[1]+zt),(b2[0],b2[1]+zt)]
    box('CCOM entrance gable roof tiles %s (mt)'%side,quad,WIN,WF+0.44,'Roof_tile_or_membrane')
# 7) medallion (round ornament under the apex)
ZM=ZB+0.42*(ZA-ZB)
def disc(name,r,w0,w1,zc,mat,N=32):
    pts=[(UC+r*math.cos(2*math.pi*i/N),zc+r*math.sin(2*math.pi*i/N)) for i in range(N)]
    return box(name,pts,w0,w1,mat)
disc('CCOM entrance gable medallion ring (mt)',0.36,WF-0.05,WF+0.05,ZM,'SCM_tower_precast')
disc('CCOM entrance gable medallion boss (mt)',0.22,WF-0.05,WF+0.10,ZM,'SCM_tower_precast')
print('GABLE pitch_deg',round(math.degrees(pitch),1),'ZB',ZB,'ZA',ZA,'ZM',round(ZM,2))
print('COUNT',len(bpy.data.objects))
bpy.ops.wm.save_mainfile(); print('SAVED')
