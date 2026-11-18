# ws124f: massed low shrubs in the bare WS116 mulch beds (E1, E2, W) on the Chapin W entrance bank, reusing the ws108 smooth shrub meshes (species/count UNVERIFIED).
import bpy, random, os
from mathutils import Vector
random.seed(124)
src=[o for o in bpy.data.objects if o.name.startswith('WS105_bank_shrub_') and o.type=='MESH']
meshes=list({o.data.name:o.data for o in src}.values()); mat=src[0].active_material
print('M124f shrub meshes',[m.name for m in meshes], 'src',len(src))
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
col=bpy.data.collections.get('WS124_Chapin_W_bank_bed_shrubs') or bpy.data.collections.new('WS124_Chapin_W_bank_bed_shrubs')
if col.name not in [c.name for c in sc.collection.children]: sc.collection.children.link(col)
n=0
for bn in ('WS116_Chapin_W_bed_E1','WS116_Chapin_W_bed_E2','WS116_Chapin_W_bed_W'):
    bed=next(o for o in bpy.data.objects if o.name.startswith(bn))
    bb=[bed.matrix_world@Vector(c) for c in bed.bound_box]
    x0,x1=min(v.x for v in bb)+0.6,max(v.x for v in bb)-0.6; y0,y1=min(v.y for v in bb)+0.6,max(v.y for v in bb)-0.6
    y=y0; row=0
    while y<=y1:
        x=x0+(0.85 if row%2 else 0)
        while x<=x1:
            px,py=x+random.uniform(-0.25,0.25),y+random.uniform(-0.25,0.25)
            hit,loc,nor,idx,ho,mtx=sc.ray_cast(dg,Vector((px,py,140)),Vector((0,0,-1)))
            if hit and ho is not None and ho.name==bed.name:
                o=bpy.data.objects.new(f'WS124_bed_shrub_{n:03d}_UNVERIFIEDspecies',meshes[n%len(meshes)])
                # fit: shrub meshes have flat base at local z min; normalise to ~1.1 m wide, 0.75 m tall
                m=o.data; vs=[v.co for v in m.vertices]; w=max(v.x for v in vs)-min(v.x for v in vs); h=max(v.z for v in vs)-min(v.z for v in vs); zmin=min(v.z for v in vs)
                s=random.uniform(0.85,1.2); sx=1.1*s/w; sz=0.75*s/h
                o.scale=(sx,sx*random.uniform(0.9,1.1),sz); o.rotation_euler[2]=random.uniform(0,6.28)
                o.location=(px,py,loc.z-0.08-zmin*sz)
                if mat and not o.data.materials: o.data.materials.append(mat)
                col.objects.link(o); n+=1
            x+=1.7
        y+=1.5; row+=1
print('M124f shrubs placed',n)
bpy.ops.wm.save_mainfile(); print('M124f SAVED')
