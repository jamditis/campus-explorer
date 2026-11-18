import bpy
from mathutils import Vector
sc=bpy.context.scene
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
def gz(x,y):
    mi=T.matrix_world.inverted(); ok,l,n,i=T.ray_cast(mi@Vector((x,y,400)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
    return (T.matrix_world@l).z if ok else 128.0
L=Vector((-64.6,-193.5,gz(-64.6,-193.5)+1.6)); G=Vector((-68.6,-184.5,gz(-68.6,-184.5)))
cd=bpy.data.cameras.new('c'); cd.lens=30; cam=bpy.data.objects.new('c',cd); sc.collection.objects.link(cam)
cam.location=L; cam.rotation_euler=(G-L).to_track_quat('-Z','Y').to_euler(); bpy.context.view_layer.update()
sc.render.resolution_x=768; sc.render.resolution_y=432
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
near=[o for o in sc.objects if o.type=='MESH' and not o.hide_render and o.visible_get() and (lambda bb:min(v.x for v in bb)<-60 and max(v.x for v in bb)>-72 and min(v.y for v in bb)<-186 and max(v.y for v in bb)>-197)([o.matrix_world@Vector(c) for c in o.bound_box])]
print("NEAR",len(near))
for u,v in [(0.45,0.84),(0.55,0.86),(0.65,0.82),(0.40,0.88),(0.70,0.95),(0.30,0.95)]:
    top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); d=((mw@top.lerp(bot,v))-L).normalized()
    best=None
    for o in near:
        mi=o.matrix_world.inverted(); ok,l,n,i=o.ray_cast(mi@L,(mi.to_3x3()@d).normalized())
        if ok:
            w=o.matrix_world@l; dist=(w-L).length
            if best is None or dist<best[0]:
                m='?'
                try: m=o.material_slots[o.data.polygons[i].material_index].material.name
                except Exception: pass
                best=(dist,o.name,m,tuple(round(x,2) for x in w))
    print("PIX",u,v,best)
