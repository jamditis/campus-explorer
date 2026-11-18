# ws76a: parking-stall paint as thin draped decal strips (WS76_lot_stall_paint_ortho2020_UNVERIFIED), rows placed by eye from the 2020 ortho.
# Each line: 0.12 m wide, sampled every 0.25 m, draped on the top-most asphalt surface +1.5 cm (samples not on asphalt are dropped).
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
for n in ('WS76_lot_stall_paint_white_ortho2020_UNVERIFIED','WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED','WS76_lot_zebra_walkway_paint_ortho2020_UNVERIFIED','WS76_lot_accessible_symbol_standin_UNVERIFIED'):
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o,do_unlink=True)
def nrm(v): v=np.array(v,float); return v/np.linalg.norm(v)
L=[]  # (a,b,kind)
def row(p0,p1,d,n,length,kind,pitch=None,shift=0.0):
    p0=np.array(p0);p1=np.array(p1);d=nrm(d)
    for k in range(n):
        t=k/(n-1) if n>1 else 0
        p=p0+(p1-p0)*t+d*shift
        L.append((p,p+d*length,kind))
# Sprague N row: 14 lines, top ends (-254,-86.5)->(-220,-90), stall dir (-0.278,-0.961), 5.0 m
row((-254,-86.5),(-220,-90),(-1.3,-4.5),14,5.0,'w')
# West angled rows by the cogen plant
row((-280.5,-56.5),(-263,-59.5),(3,-6.5),7,6.0,'w')
row((-284,-65.8),(-267,-69.5),(3.5,-6.0),7,6.0,'w')
# East accessible rows (wheelchair symbols visible in ortho): lines between stalls, perpendicular to row, centred on the symbol line
SYM=[]
for (a,b,nd_,OFF) in (((-247.5,-68.3),(-219.2,-75.6),9,-1.2),((-252.2,-77.8),(-223.5,-83.7),9,0.0)):
    a=np.array(a);b=np.array(b);u=nrm(b-a);pn=np.array([-u[1],u[0]]);pitch=np.linalg.norm(b-a)/(nd_-1)
    for k in range(nd_+1):
        c=a+u*pitch*(k-0.5)+pn*OFF; L.append((c-pn*2.7,c+pn*2.7,'b'))
    for k in range(nd_): SYM.append((a+u*pitch*k+pn*OFF,u))
bpy.context.view_layer.update()
# N-S zebra walkway across the lots (2020 ortho), centreline by eye, 3 m bars, 0.45 m wide, 0.9 m pitch
CL=np.array([(-258.5,-56),(-261.5,-73),(-262,-80),(-261,-95)])
segL=np.r_[0,np.cumsum(np.linalg.norm(np.diff(CL,axis=0),axis=1))]
for t in np.arange(0.45,segL[-1],0.9):
    i=min(np.searchsorted(segL,t)-1,len(CL)-2); f=(t-segL[i])/(segL[i+1]-segL[i]); c=CL[i]+(CL[i+1]-CL[i])*f
    u=nrm(CL[i+1]-CL[i]); pn=np.array([-u[1],u[0]])
    L.append((c-pn*1.5,c+pn*1.5,'z'))
dg=bpy.context.evaluated_depsgraph_get()
box=(-290,-212,-102,-50)
cands=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith(('T_','OZ_walk_joints')) or 'helper' in o.name or o.name.startswith('WS76_lot'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]
    if min(xs)<box[1] and max(xs)>box[0] and min(ys)<box[3] and max(ys)>box[2] and len(o.data.vertices)<600000:
        oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
        mats=[s.material.name if s.material else '' for s in o.material_slots]
        fm=[ (mats[f.material_index] if f.material_index<len(mats) else '') for f in bm.faces]
        cands.append((o.name,BVHTree.FromBMesh(bm),fm)); bm.free(); oe.to_mesh_clear()
print('WS76a cands',len(cands),flush=True)
def top(x,y):
    best=None
    for n,t,fm in cands:
        h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        if h[0] and (best is None or h[0].z>best[0]): best=(h[0].z,n,fm[h[2]] if h[2]<len(fm) else '')
    return best
stat={}
def ok(b): return b and ('sphalt' in b[2] or 'asphalt' in b[2].lower() or 'lot' in b[2].lower())
def build(kind,name,mat):
    bm=bmesh.new()
    for a,b,k in L:
        if k!=kind[0]: continue
        W=0.225 if k=='z' else 0.06
        v=b-a; ln=np.linalg.norm(v); u=v/ln; pn=np.array([-u[1],u[0]]); ns=max(2,int(ln/0.25)+1)
        prev=None
        for i in range(ns):
            p=a+v*i/(ns-1); h=top(*p)
            if not ok(h):
                stat[h[1] if h else None]=stat.get(h[1] if h else None,0)+1; prev=None; continue
            z=h[0]+0.015
            l=bm.verts.new((p[0]-pn[0]*W,p[1]-pn[1]*W,z)); r=bm.verts.new((p[0]+pn[0]*W,p[1]+pn[1]*W,z))
            if prev: bm.faces.new((prev[0],prev[1],r,l))
            prev=(l,r)
    if kind=='b':  # blue square + white disc symbol stand-in at each accessible stall
        for c,u in SYM:
            h=top(*c)
            if not ok(h): continue
            z=h[0]+0.017; pn=np.array([-u[1],u[0]])
            q=[bm.verts.new((*(c+u*sx*0.75+pn*sy*0.75),z)) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
            bm.faces.new(q)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(mat)
    o['ws76']='stall paint, rows by eye from 2020 ortho, UNVERIFIED'; return o
def pm(n,rgb,r=0.55):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n); m.use_nodes=True
    b=[x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED'][0]; b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=r; return m
mw=pm('WS76_paint_white_faded',(0.58,0.58,0.54)); mb=pm('WS76_paint_blue_accessible',(0.012,0.075,0.30))
oz=build('z','WS76_lot_zebra_walkway_paint_ortho2020_UNVERIFIED',mw)
ow=build('w','WS76_lot_stall_paint_white_ortho2020_UNVERIFIED',mw)
ob=build('b','WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED',mb)
# white disc symbols on the blue squares
bm=bmesh.new()
for c,u in SYM:
    h=top(*c)
    if not ok(h): continue
    z=h[0]+0.025; cv=bm.verts.new((c[0],c[1],z)); vs=[bm.verts.new((c[0]+0.38*np.cos(a),c[1]+0.38*np.sin(a),z)) for a in np.linspace(0,2*np.pi,17)[:-1]]
    for i in range(16): bm.faces.new((cv,vs[i],vs[(i+1)%16]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new('WS76_acc_sym'); bm.to_mesh(me); bm.free()
os_=bpy.data.objects.new('WS76_lot_accessible_symbol_standin_UNVERIFIED',me); bpy.context.scene.collection.objects.link(os_); os_.data.materials.append(mw)
for o in (ow,ob,os_):
    for c in list(o.users_collection): pass
print('WS76a lines',len(L),'zebra faces',len(oz.data.polygons),'white faces',len(ow.data.polygons),'blue faces',len(ob.data.polygons),'sym',len(os_.data.polygons),'dropped-by-top',sorted(stat.items(),key=lambda a:-a[1])[:8],flush=True)
