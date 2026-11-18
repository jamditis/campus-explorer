# ws123: (1) UNIFY #27 flare tops into WS113_paving_tops_proxy so the verge lawn grades up to the flare edge;
# (2) Chapin W entrance doors: solid bronze slab -> storefront pair (frame, sidelites, meeting stile, transom, push bars, recessed glass);
# (3) D-planter lollipop tree -> linked campus asset Tree_HoneyLocust_LOD1_Oct_turning scaled to a young plaza tree (species UNVERIFIED).
import bpy, bmesh, os, math
from mathutils import Vector, Matrix
def ob(p): return next(o for o in bpy.data.objects if o.name.startswith(p))
# (1)
fl=ob('WS121_Chapin_W_plaza_NW_corner_sidewalk_flare'); pv=bpy.data.objects['WS113_paving_tops_proxy']
b2=bmesh.new(); b2.from_mesh(pv.data); n0=len(b2.faces)
t=bmesh.new(); t.from_mesh(fl.data); t.transform(fl.matrix_world); t.normal_update()
bmesh.ops.delete(t,geom=[f for f in t.faces if f.normal.z<0.5],context='FACES')
t.transform(pv.matrix_world.inverted())
m3=bpy.data.meshes.new('tmp'); t.to_mesh(m3); t.free(); b2.from_mesh(m3); bpy.data.meshes.remove(m3)
b2.to_mesh(pv.data); b2.free(); pv.data.update(); print('M123 proxy',n0,'->',len(pv.data.polygons))
# (2)
d=ob('WS117_Chapin_W_entrance_doors'); col=d.users_collection[0]
fr=bpy.data.materials.get('WS108_Chapin_window_frame_dark_bronze')
glass=None
for o in bpy.data.objects:
    if o.name.startswith('WS122_Chapin_windows'):
        for m in o.data.materials:
            if m and 'glass' in m.name.lower(): glass=m
if glass is None: glass=next((m for m in bpy.data.materials if 'glass' in m.name.lower()),fr)
print('M123 glass',glass.name)
X0,X1=-209.22,-209.05; YA,YB=-200.38,-197.88; Z0,Z1=124.77,127.52
bm=bmesh.new()
def box(x0,x1,y0,y1,z0,z1,mi):
    r=bmesh.ops.create_cube(bm,size=1.0); vs=r['verts']
    for v in vs:
        v.co.x=x0 if v.co.x<0 else x1; v.co.y=y0 if v.co.y<0 else y1; v.co.z=z0 if v.co.z<0 else z1
    for f in {f for v in vs for f in v.link_faces}: f.material_index=mi
# back reveal (dark interior) and recessed glass
box(-209.10,X1,YA,YB,Z0,Z1,0)
box(-209.200,-209.190,YA,YB,Z0,Z1,1)
fx0,fx1=X0-0.02,-209.17   # frame bars 2 cm proud of old face
w=0.05
for yc,ww in ((YA+w/2,w),(YB-w/2,w),(YA+0.30,0.04),(YB-0.30,0.04),((YA+YB)/2,0.07)):
    box(fx0,fx1,yc-ww/2,yc+ww/2,Z0,Z1,0)
for zc,hh in ((Z0+0.06,0.12),(Z1-0.04,0.08),(Z0+2.25,0.07)):   # bottom rail, head, transom
    box(fx0,fx1,YA,YB,zc-hh/2,zc+hh/2,0)
# leaf kick rails + vertical pull bars at the meeting stile
ym=(YA+YB)/2
for s in (-1,1):
    box(fx0,fx1,min(ym,ym+s*0.95),max(ym,ym+s*0.95),Z0+0.12,Z0+0.30,0)
    yb=ym+s*0.16; box(fx0-0.07,fx0-0.04,yb-0.015,yb+0.015,Z0+0.85,Z0+1.85,2)
me=bpy.data.meshes.new('WS123_Chapin_W_entrance_storefront_doors_pair_UNVERIFIED'); bm.to_mesh(me); bm.free()
steel=bpy.data.materials.get('WS123_brushed_steel') or bpy.data.materials.new('WS123_brushed_steel')
steel.use_nodes=True; bs=steel.node_tree.nodes.get('Principled BSDF')
if bs: bs.inputs['Base Color'].default_value=(0.62,0.62,0.6,1); bs.inputs['Metallic'].default_value=1.0; bs.inputs['Roughness'].default_value=0.3
for m in (fr,glass,steel): me.materials.append(m)
nd=bpy.data.objects.new(me.name,me); col.objects.link(nd)
bpy.data.objects.remove(d,do_unlink=True); print('M123 doors',len(me.polygons))
# (3)
tr=ob('WS120_Chapin_W_round_planter_ornamental_tree'); vs=[tr.matrix_world@v.co for v in tr.data.vertices]
cx=sum(v.x for v in vs)/len(vs); cy=sum(v.y for v in vs)/len(vs); z0=min(v.z for v in vs)
tcol=tr.users_collection[0]
lib='//../assets/campus_assets.blend'
with bpy.data.libraries.load(bpy.path.abspath(lib),link=True,relative=True) as (df,dt):
    dt.collections=['Tree_HoneyLocust_LOD1_Oct_turning'] if 'Tree_HoneyLocust_LOD1_Oct_turning' not in bpy.data.collections else []
c=bpy.data.collections['Tree_HoneyLocust_LOD1_Oct_turning']
e=bpy.data.objects.new('WS123_Chapin_W_planter_tree_HoneyLocust_young_UNVERIFIEDspecies',None)
S=0.24; SZ=0.25; RZ=math.radians(37)
src=[o for o in c.all_objects if o.type=='MESH'][0]; off=src.matrix_world.translation.copy()   # library tree sits at (100,90,0)
ox=S*(off.x*math.cos(RZ)-off.y*math.sin(RZ)); oy=S*(off.x*math.sin(RZ)+off.y*math.cos(RZ))
e.instance_type='COLLECTION'; e.instance_collection=c; e.location=(cx-ox,cy-oy,z0-0.05-SZ*off.z); e.scale=(S,S,SZ); e.rotation_euler[2]=RZ
print('M123 tree offset comp',round(ox,2),round(oy,2))
tcol.objects.link(e)
bpy.data.objects.remove(tr,do_unlink=True); print('M123 tree at',round(cx,2),round(cy,2),round(z0,2))
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M123 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M123 SAVED',SAVE)
