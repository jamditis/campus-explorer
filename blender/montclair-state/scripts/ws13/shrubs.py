import bpy, os, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
DRY=os.environ.get('DRY')=='1'
dg=bpy.context.evaluated_depsgraph_get()
bed=bpy.data.objects['COLE_planting_beds_smooth_bu']; me=bed.evaluated_get(dg).to_mesh(); w=bed.matrix_world
TB=BVHTree.FromPolygons([w@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
A=Vector((-86.4,-63.92,0)); B=Vector((-69.74,-68.43,0)); d=(B-A); d.z=0; d.normalize(); nrm=Vector((-d.y,d.x,0))
ed=bpy.data.objects['WS13_Cole_SW_bridge_brick_edging_UNVERIFIED']
E=[]
for v in ed.data.vertices:
    q=ed.matrix_world@v.co; r=Vector((q.x,q.y,0))-A; E.append((r.dot(d),r.dot(nrm)))
# obstacles: lamps/poles/trees within 1.2 m
obs=[o.matrix_world.translation.copy() for o in bpy.data.objects if any(k in o.name.lower() for k in ('lamp','pole','light_','tree','t_pinoak','sign')) and o.type in ('MESH','EMPTY')]
src={n:bpy.data.objects[n] for n in ('Shrub_Azalea','Shrub_Boxwood')}
col=bpy.data.collections.get('WS13_Cole_SW_bed_shrubs_20261109')
if col:
    for o in list(col.objects): bpy.data.objects.remove(o)
else:
    col=bpy.data.collections.new('WS13_Cole_SW_bed_shrubs_20261109'); bpy.context.scene.collection.children.link(col)
random.seed(13); n=0
for side in (-1,1):
    es=[s for t,s in E if (s>0)==(side>0)]
    edge=(max(es) if side>0 else min(es))
    t=4.2+ (0.9 if side>0 else 0)
    while t<15.0:
        s=edge+side*random.uniform(0.75,0.95)
        p=A+d*t+nrm*s
        h=TB.ray_cast(Vector((p.x,p.y,140)),Vector((0,0,-1)),10)
        near=any((Vector((o.x,o.y,0))-Vector((p.x,p.y,0))).length<1.3 for o in obs)
        if h[0] and not near:
            kind='Shrub_Boxwood' if n%3!=1 else 'Shrub_Azalea'; s_=src[kind]
            if not DRY:
                o=bpy.data.objects.new(f'WS13_{kind.split("_")[1]}_Cole_SW_bed_{n}_UNVERIFIED',s_.data); col.objects.link(o)
                for m in s_.modifiers:
                    nm=o.modifiers.new(m.name,m.type)
                    if m.type=='DISPLACE':
                        nm.texture=m.texture; nm.strength=m.strength; nm.mid_level=m.mid_level; nm.texture_coords=m.texture_coords
                    elif m.type=='NODES':
                        nm.node_group=m.node_group
                        for k in m.keys():
                            try: nm[k]=m[k]
                            except Exception: pass
                sc=random.uniform(0.7,0.85); o.scale=(sc,sc,sc*random.uniform(0.85,1.0))
                o.location=(p.x,p.y,h[0].z-0.04); o.rotation_euler=(0,0,random.uniform(0,6.28))
            print('SHRUB',n,kind,round(t,1),side,[round(c,2) for c in p[:2]],round(h[0].z,2)); n+=1
        else: print('SKIP',round(t,1),side,'bed' if not h[0] else 'near')
        t+=random.uniform(2.3,2.9)
print('N',n)
if not DRY: bpy.ops.wm.save_mainfile(); print('SAVED')
