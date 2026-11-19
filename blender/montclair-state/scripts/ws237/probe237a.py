# ws237 read-only CHAIN: ray-identify what the WS68 W eye camera (ws236 cam 3) sees on a pixel grid (evaluated), then exit before render
import bpy, mathutils, os, math
cam=[float(v) for v in os.environ.get('PCAM','-370.0,-20.0,124.5,-320.0,0.0,121.5,30').split(',')]
E=mathutils.Vector(cam[:3]); T=mathutils.Vector(cam[3:6]); lens=cam[6]
W,H=704,396; sw=36.0; fx=lens/sw*W
f=(T-E).normalized(); r=f.cross(mathutils.Vector((0,0,1))).normalized(); u=r.cross(f)
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
PX=[tuple(map(int,p.split(':'))) for p in os.environ['PPIX'].split()] if os.environ.get('PPIX') else [(px,py) for py in range(150,396,30) for px in range(20,704,60)]
if True:
  for px,py in PX:
    d=(f*fx + r*(px-W/2) + u*(H/2-py)).normalized()
    h=sc.ray_cast(dg,E,d)
    if h[0]:
      o=h[4]; mi=h[3]; m=None
      try:
        me=o.evaluated_get(dg).data; m=me.materials[me.polygons[h[3]].material_index].name if me.materials else None
      except Exception: pass
      print('P237A',px,py,o.name[:40],'%.1f %.1f %.2f'%tuple(h[1]),'nz %.2f'%h[2].z,'dist %.1f'%(h[1]-E).length,(m or '')[:28],flush=True)
    else: print('P237A',px,py,None,flush=True)
os._exit(0)
