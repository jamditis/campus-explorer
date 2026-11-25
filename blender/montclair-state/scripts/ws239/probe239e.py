# ws239 read-only (subset, evaluated): ray from the eye camera to each m2c239 object's bbox centre; first hit object.
import bpy, os, json
from mathutils import Vector
E=Vector([float(v) for v in os.environ.get('PEYE','-256.0,-62.0,126.6').split(',')])
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for n in json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws239/m2c_new239.json')):
    o=bpy.data.objects.get(n)
    if not o: print('P239E missing',n[:40]); continue
    c=sum((o.matrix_world@Vector(b) for b in o.bound_box),Vector())/8
    d=(c-E); L=d.length; h=sc.ray_cast(dg,E,d.normalized(),distance=L+0.5)
    print('P239E',n[:36],'ctr %.1f %.1f %.2f'%tuple(c),'hit',(h[4].name[:40] if h[0] else None),'at %.2f of %.2f'%(((h[1]-E).length if h[0] else -1),L),flush=True)
os._exit(0)
