# ws119 entrance detail: contrasting tread nosings on the WS117 stair, precast coping on the terrace edge walls.
import bpy, bmesh, os, numpy as np
ZL=124.77
stair=next(o for o in bpy.data.objects if o.name.startswith('WS117_Chapin_W_entrance_stair_11R'))
coll=stair.users_collection[0]
def mat(name,rgb,rough):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*rgb,1); p.inputs['Roughness'].default_value=rough; return m
mn=mat('WS119_stair_nosing_charcoal_UNVERIFIED',(0.045,0.045,0.048),0.75)
mc=mat('WS119_wall_coping_precast_UNVERIFIED',(0.62,0.61,0.58),0.6)
def box(bm,x0,x1,y0,y1,z0,z1):
    v=[bm.verts.new(c) for c in ((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([v[i] for i in f])
# treads: up-facing faces of the stair
mw=stair.matrix_world; tr=[]
for p in stair.data.polygons:
    n=mw.to_3x3()@p.normal
    if n.z>0.9 and p.area>0.2:
        ws=[mw@stair.data.vertices[i].co for i in p.vertices]
        tr.append((min(w.x for w in ws),min(w.y for w in ws),max(w.y for w in ws),max(w.z for w in ws)))
tr.sort(); print('D119 treads',len(tr),[(round(a,2),round(d,3)) for a,b,c,d in tr])
me=bpy.data.meshes.new('WS119_nosing'); ob=bpy.data.objects.new('WS119_Chapin_W_entrance_stair_nosings_charcoal_UNVERIFIED',me); coll.objects.link(ob); me.materials.append(mn)
bm=bmesh.new()
for x0,y0,y1,z in tr: box(bm,x0-0.003,x0+0.05,y0+0.04,y1-0.04,z-0.02,z+0.003)
# landing front edge (top nosing) at the stair head
x_head=max(t[0] for t in tr)+0.37; y0=min(t[1] for t in tr); y1=max(t[2] for t in tr)
box(bm,x_head-0.003,x_head+0.05,y0+0.04,y1-0.04,ZL-0.02,ZL+0.003)
bm.to_mesh(me); bm.free()
# coping: follow both straight edge walls (ws118 + ws119)
xr=lambda y: -213.3+(min(y,-184.0)+196.65)*(2.3/12.65)
xw=lambda y: -211.02+(y+182.0)*(3.12/10.0)
zt=lambda y: ZL+0.13*min(1.0,max(0.0,(y+182.0)/5.0))
me2=bpy.data.meshes.new('WS119_coping'); oc=bpy.data.objects.new('WS119_Chapin_W_terrace_wall_coping_precast_UNVERIFIED',me2); coll.objects.link(oc); me2.materials.append(mc)
bm=bmesh.new()
def run(ys,xe,ztop):
    R=[]
    for y in ys:
        x1=xe(y)+0.04; x0=xe(y)-0.30-0.03; z=ztop(y)
        R.append([bm.verts.new(c) for c in ((x0,y,z-0.02),(x1,y,z-0.02),(x1,y,z+0.06),(x0,y,z+0.06))])
    for r0,r1 in zip(R[:-1],R[1:]):
        for i in range(4):
            j=(i+1)%4; bm.faces.new((r0[i],r0[j],r1[j],r1[i]))
    bm.faces.new(R[0][::-1]); bm.faces.new(R[-1])
run(list(np.linspace(-196.65,-184.0,24))+list(np.linspace(-184.0,-182.0,4)[1:]),lambda y: xr(y)+0.01,lambda y: ZL+0.45)
run(list(np.linspace(-182.0,-172.0,21)),lambda y: xw(y)+0.01,lambda y: zt(y)+0.45)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me2); bm.free()
print('D119 nosings',len(tr)+1,'coping done')
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('D119 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('D119 SAVED',SAVE)
