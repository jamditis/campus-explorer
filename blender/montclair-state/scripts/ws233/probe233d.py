# ws233 probe d: identify the 2 dark specks in the NE eye view (pixels ~(325,108),(318,148) of 704x396) by scene ray casts from the real camera
import bpy,os,sys,json
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
BB=json.load(open(M+'scripts/ws205/bbox205.json')); cx0,cx1,cy0,cy1=110,170,180,245
want=[n for n,(t,hr,x0,x1,y0,y1,z0,z1,cols) in BB.items() if t in ('MESH','CURVE') and not hr and not n.startswith(('Context_skirt','BD_farfield')) and not (x1<cx0 or x0>cx1 or y1<cy0 or y0>cy1)]
with bpy.data.libraries.load(M+'montclair_state_ws233b.blend') as (a,b):
    have=set(a.objects); b.objects=[n for n in want if n in have]
sc=bpy.context.scene
for o in b.objects:
    if o: sc.collection.objects.link(o); [setattr(m,'show_viewport',False) for m in o.modifiers]
cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam); sc.camera=cam
cam.location=(151.0,228.0,138.6); cam.data.lens=30
d=Vector((134.0,198.0,137.4))-cam.location; cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
sc.render.resolution_x=1280; sc.render.resolution_y=720
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]  # tr, br, bl, tl
tr,br,bl,tl=fr
for px,py in [(325,108),(318,148)]:
    seen={}
    for ddx in range(-4,5):
        for ddy in range(-4,5):
            u=(px+ddx)/704; v=(py+ddy)/396
            p=tl+(tr-tl)*u+(bl-tl)*v; r=(p-cam.location).normalized()
            o0=cam.location.copy(); chain=[]
            for _ in range(6):
                h,loc,nrm,idx,ob,mat=sc.ray_cast(dg,o0,r)
                if not h: break
                chain.append((ob.name,round((loc-cam.location).length,1),round(loc.z,1))); o0=loc+r*0.02
            k=str(chain[:4]); seen[k]=seen.get(k,0)+1
    print('P233D',px,py,seen,flush=True)
sys.stdout.flush(); os._exit(0)
