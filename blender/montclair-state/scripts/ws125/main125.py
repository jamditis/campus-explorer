# ws125: shrub variety (Boxwood/Azalea/Yew leaf-card assets replace the 41 plain WS124 blobs), pachysandra-style groundcover mats, door threshold.
import bpy, random, math
from mathutils import Vector
random.seed(125)
sc=bpy.context.scene
LIB='/workspace/nj-scenes/assets/campus_assets.blend'
want=['Shrub_Boxwood','Shrub_Azalea','Shrub_Yew']
with bpy.data.libraries.load(LIB,link=False) as (df,dt):
    dt.objects=[n for n in df.objects if n in want]
src={o.name:o for o in dt.objects}
for o in src.values(): print('M125 asset',o.name,[m.type for m in o.modifiers],tuple(round(x,2) for x in o.dimensions),[round(v.co.z,2) for v in o.data.vertices][:1], min(v.co.z for v in o.data.vertices))
col=bpy.data.collections.new('WS125_Chapin_W_bank_planting'); sc.collection.children.link(col)
old=[o for o in bpy.data.objects if o.name.startswith('WS124_bed_shrub_')]
dg=bpy.context.evaluated_depsgraph_get()
def dup(base,name):
    o=base.copy(); o.name=name; o.data=base.data  # share mesh
    for m in o.modifiers:
        pass
    col.objects.link(o); return o
types=['Shrub_Boxwood','Shrub_Azalea','Shrub_Yew']
pts=[]
for i,ob in enumerate(sorted(old,key=lambda o:o.name)):
    t=types[i%3]; b=src[t]
    n=dup(b,f'WS125_bed_shrub_{i:02d}_{t[6:]}_UNVERIFIEDspecies')
    dx,dy,dz=b.dimensions; bz=min(v.co.z for v in b.data.vertices)
    w=random.uniform(0.95,1.3); h=random.uniform(0.7,0.95)
    sx=w/max(dx,dy); sz=h/dz
    n.scale=(sx,sx*random.uniform(0.92,1.08),sz); n.rotation_euler[2]=random.uniform(0,6.28)
    zc=ob.location.z+ (0.08+ min(v.co.z for v in ob.data.vertices)*ob.scale.z)  # ground z under old shrub
    n.location=(ob.location.x,ob.location.y,zc-0.04-bz*sz)
    pts.append((ob.location.x,ob.location.y))
    bpy.data.objects.remove(ob)
print('M125 shrubs',len(pts))
# groundcover: low flattened boxwood-leaf mats (pachysandra-like) between shrubs
g=src['Shrub_Boxwood']; gz=min(v.co.z for v in g.data.vertices); k=0
for bn in ('WS116_Chapin_W_bed_E1','WS116_Chapin_W_bed_E2','WS116_Chapin_W_bed_W'):
    bed=next(o for o in bpy.data.objects if o.name.startswith(bn))
    bb=[bed.matrix_world@Vector(c) for c in bed.bound_box]
    x0,x1=min(v.x for v in bb)+0.35,max(v.x for v in bb)-0.35; y0,y1=min(v.y for v in bb)+0.35,max(v.y for v in bb)-0.35
    y=y0
    while y<=y1:
        x=x0
        while x<=x1:
            px,py=x+random.uniform(-0.2,0.2),y+random.uniform(-0.2,0.2)
            if all((px-a)**2+(py-b_)**2>0.75**2 for a,b_ in pts):
                hit,loc,nor,idx,ho,mtx=sc.ray_cast(dg,Vector((px,py,140)),Vector((0,0,-1)))
                if hit and ho is not None and ho.name==bed.name and nor.z>0.5:
                    o=dup(g,f'WS125_bed_groundcover_{k:03d}_UNVERIFIED'); k+=1
                    s=random.uniform(0.55,0.85)
                    o.scale=(s,s*random.uniform(0.9,1.1),random.uniform(0.14,0.2)); o.rotation_euler[2]=random.uniform(0,6.28)
                    o.location=(px,py,loc.z-0.03-gz*o.scale.z)
                    pts.append((px,py)) if False else None
            x+=0.7
        y+=0.7
print('M125 groundcover',k)
# door threshold: bronze saddle + clean sill across the pair (doors x -209.31..-209.05, y -200.38..-197.88, floor 124.768)
import bmesh
me=bpy.data.meshes.new('WS125_threshold'); bm=bmesh.new()
bmesh.ops.create_cube(bm,size=1.0)
for v in bm.verts: v.co.x=v.co.x*0.34-209.19; v.co.y=v.co.y*2.50-199.13; v.co.z=v.co.z*0.045+124.768+0.0225-0.005
bm.to_mesh(me); bm.free()
th=bpy.data.objects.new('WS125_Chapin_W_door_threshold_bronze_saddle_UNVERIFIED',me); col.objects.link(th)
mat=next((m for m in bpy.data.materials if 'bronze' in m.name.lower() or 'door' in m.name.lower()),None)
dm=bpy.data.objects['WS123_Chapin_W_entrance_storefront_doors_pair_UNVERIFIED']
if dm.data.materials: th.data.materials.append(dm.data.materials[0])
print('M125 threshold mat',[m.name for m in dm.data.materials])
bpy.ops.wm.save_mainfile(); print('M125 SAVED')
