import bpy, resource, time
t0=time.time()
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read().split('\n')
src='\n'.join(src[:18]).replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1]+[o.name for o in bpy.data.objects if o.name.startswith(('WS113_terrain_fan_fill','WS110_ground_patch','WS133b_','WS134_ground'))])")
exec(src)
camz('WS143_CAM_eye_forecourt_from_N_aisle',(-64.5,-160,0),(-73,-176),26,1.7,0.5)
sc.render.resolution_x=640; sc.render.resolution_y=360
# hide foliage
for o in bpy.data.objects:
    n=o.name.lower()
    if any(k in n for k in ('tree','leaf','canopy','crown','foliage','shrub')): o.hide_viewport=True
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['WS143_CAM_eye_forecourt_from_N_aisle']
fr=[cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]
o=cam.matrix_world.translation
tr,br,bl,tl=fr
for (px,py) in [(250,195),(290,190),(220,205),(310,188),(180,200),(80,210),(120,212),(60,208),(200,214),(150,215),(260,200)]:
    u=px/640; v=py/360
    p=tl+(tr-tl)*u+(bl-tl)*v; d=(p-o).normalized()
    hit,loc,nrm,i,ob,m=sc.ray_cast(dg,o,d)
    mat=None
    if hit:
        try: mat=ob.material_slots[ob.data.polygons[i].material_index].material.name if ob.type=='MESH' and i<len(ob.data.polygons) else 'evalidx'
        except Exception as e: mat=str(e)[:40]
    print("HIT",(px,py), ob.name[:70] if hit else None, mat, tuple(round(c,2) for c in loc) if hit else None)
# list objects whose bbox overlaps region N of Freeman
from mathutils import Vector
for ob in bpy.data.objects:
    if ob.type!='MESH' or ob.hide_render: continue
    bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    xs=[c.x for c in bb]; ys=[c.y for c in bb]
    if max(xs)-min(xs)>60 or max(ys)-min(ys)>60: continue
    if min(xs)<-66 and max(xs)>-90 and min(ys)<-160 and max(ys)>-180:
        mats=[s.material.name for s in ob.material_slots if s.material]
        print("OBJ",ob.name[:60],[round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(c.z for c in bb),2)],mats[:4])
print("MAXRSS_MB",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024,"t",round(time.time()-t0,1))
