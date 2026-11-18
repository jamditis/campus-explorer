# low-memory partial diagnosis: append a camera + objects whose bbox is within R m of it from ws150a, ray-cast a pixel box
import bpy, json, os, resource
from mathutils import Vector
P='/workspace/nj-scenes/montclair-state/montclair_state_ws150a.blend'
CAM=os.environ['CAM']; R=float(os.environ.get('R','8')); PX=[float(v) for v in os.environ['PX'].split(',')]  # u0,u1,v0,v1 in 0..1 (v from top)
with bpy.data.libraries.load(P, link=False) as (s,d): d.objects=[CAM]
cam=d.objects[0]; bpy.context.scene.collection.objects.link(cam); c=cam.matrix_world.translation.copy()
print("CAMLOC",tuple(round(x,2) for x in c),"lens",cam.data.lens)
names=[]
for l in open('/workspace/nj-scenes/montclair-state/scripts/ws147/bboxes.jsonl'):
    j=json.loads(l)
    if j['t'] not in ('MESH','CURVE','CURVES','POINTCLOUD','EMPTY'): continue
    b=j['bb']; dx=max(b[0]-c.x,0,c.x-b[3]); dy=max(b[1]-c.y,0,c.y-b[4]); dz=max(b[2]-c.z,0,c.z-b[5])
    if (dx*dx+dy*dy+dz*dz)**.5<R and b[3]-b[0]<400: names.append(j['n'])
names+=[n for n in os.environ.get('EXTRA','').split(',') if n]
with bpy.data.libraries.load(P, link=False) as (s,d): d.objects=[n for n in names if n in s.objects]
sc=bpy.context.scene
for o in d.objects:
    if o and o.name not in sc.collection.objects: sc.collection.objects.link(o)
print("APPENDED",len(d.objects),"rss",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
sc.camera=cam; sc.render.resolution_x=768; sc.render.resolution_y=432
dg=bpy.context.evaluated_depsgraph_get(); fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
hits={}
for iy in range(12):
  for ix in range(24):
    u=PX[0]+(PX[1]-PX[0])*ix/23; v=PX[2]+(PX[3]-PX[2])*iy/11
    p=fr[1].lerp(fr[0],u); q=fr[2].lerp(fr[3],u); pt=p.lerp(q,v)
    dd=(mw@pt)-mw.translation
    ok,lp,n,fi,ob,_=sc.ray_cast(dg,mw.translation,dd.normalized())
    if ok:
        me=ob.data if ob.type=='MESH' else None
        mat=''
        try: mat=ob.material_slots[ob.data.polygons[fi].material_index].material.name if me and fi<len(me.polygons) else '?'
        except Exception: mat='?'
        k=(ob.name,mat); h=hits.setdefault(k,[0,lp,(lp-mw.translation).length]); h[0]+=1
    else: hits.setdefault(('MISS',''),[0,None,0])[0]+=1
for k,v in sorted(hits.items(),key=lambda kv:-kv[1][0]):
    print("HIT",v[0],k, tuple(round(x,2) for x in v[1]) if v[1] else '', round(v[2],2))
if os.environ.get('RENDER'):
    sc.render.engine='BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_WORKBENCH'
    sc.render.filepath=os.environ['RENDER']; bpy.ops.render.render(write_still=True)
