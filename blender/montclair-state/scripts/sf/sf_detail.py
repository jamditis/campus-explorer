# sf detail (Nov 4 2026 ~3:33 PM ET): Lot 38 stall stripes + 2 green roll-off containers, both traced from the 2020 ortho
# (data/sf/ortho_lot38_zoom.jpg, ±0.4 m). Stripe spacing ~2.2 m, slant, container size/type UNVERIFIED. REVERT=1 removes.
import bpy, bmesh, os, math
from mathutils import Vector, Matrix
COL='SF_Lot38_QuadRoad_UNVERIFIED'; NAMES=('SF_Lot38_stall_stripes_UNVERIFIED','SF_Lot38_rolloff_containers_UNVERIFIED')
for n in NAMES:
    o=bpy.data.objects.get(n)
    if o: me=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.meshes.remove(me)
for n in ('SF_stripe_paint_worn_UNVERIFIED','SF_container_green_UNVERIFIED'):
    m=bpy.data.materials.get(n)
    if m: bpy.data.materials.remove(m)
if os.environ.get('REVERT')=='1':
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
col=bpy.data.collections[COL]; lot=bpy.data.objects['SF_Lot38_asphalt_313028558_UNVERIFIED']
dg=bpy.context.evaluated_depsgraph_get(); le=lot.evaluated_get(dg); iw=lot.matrix_world.inverted()
def lz(x,y):
    r=le.ray_cast(iw@Vector((x,y,300)),Vector((0,0,-1)))
    return (lot.matrix_world@r[1]).z if r[0] else None
def mat(n,c,r):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=r; return m
MP=mat('SF_stripe_paint_worn_UNVERIFIED',(0.55,0.55,0.52),0.8); MG=mat('SF_container_green_UNVERIFIED',(0.05,0.16,0.09),0.55)
def edge_y(x): return 355.0+(x-16.2)*(352.4-355.0)/(37.2-16.2)
bm=bmesh.new(); n=0
for k in range(8):
    xb=16.9+2.2*k; yb=348.2; yt=edge_y(xb+1.0)-0.45; xt=xb+1.0*(yt-yb)/5.8
    L=math.hypot(xt-xb,yt-yb); ux,uy=(xt-xb)/L,(yt-yb)/L; nx,ny=-uy*0.05,ux*0.05; seg=max(2,int(L/0.5))
    row=[]
    for i in range(seg+1):
        t=i/seg; x=xb+(xt-xb)*t; y=yb+(yt-yb)*t; z=lz(x,y)
        if z is None: row.append(None); continue
        row.append((bm.verts.new((x+nx,y+ny,z+0.006)),bm.verts.new((x-nx,y-ny,z+0.006))))
    for a,b in zip(row[:-1],row[1:]):
        if a and b: bm.faces.new((a[0],b[0],b[1],a[1])); n+=1
me=bpy.data.meshes.new(NAMES[0]); bm.to_mesh(me); bm.free(); me.materials.append(MP)
o=bpy.data.objects.new(NAMES[0],me); col.objects.link(o); o.visible_shadow=False; o['UNVERIFIED_sf']='stall lines traced from 2020 ortho, spacing ~2.2 m, worn white'
print('SF stripes faces',n)
bm=bmesh.new()
for cx,cy in ((6.2,342.2),(9.9,342.4)):
    z=lz(cx,cy) or 139.3
    r=bmesh.ops.create_cube(bm,size=1.0)['verts']
    for v in r:
        sx=2.3; sy=6.4; sz=1.75
        top=v.co.z>0
        v.co=Vector((v.co.x*(sx-(0.2 if top else 0)),v.co.y*(sy-(0.3 if top else 0)),(v.co.z+0.5)*sz))
    bmesh.ops.rotate(bm,verts=r,cent=(0,0,0),matrix=Matrix.Rotation(math.radians(-14),3,'Z'))
    bmesh.ops.translate(bm,verts=r,vec=(cx,cy,z+0.12))
    # rails
    rr=bmesh.ops.create_cube(bm,size=1.0)['verts']
    for v in rr: v.co=Vector((v.co.x*1.4,v.co.y*6.2,(v.co.z+0.5)*0.14))
    bmesh.ops.rotate(bm,verts=rr,cent=(0,0,0),matrix=Matrix.Rotation(math.radians(-14),3,'Z')); bmesh.ops.translate(bm,verts=rr,vec=(cx,cy,z-0.02))
me=bpy.data.meshes.new(NAMES[1]); bm.to_mesh(me); bm.free(); me.materials.append(MG)
o=bpy.data.objects.new(NAMES[1],me); col.objects.link(o); o['UNVERIFIED_sf']='2 green containers at the ortho positions (north wall by the loading dock); roll-off type/size UNVERIFIED'
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
