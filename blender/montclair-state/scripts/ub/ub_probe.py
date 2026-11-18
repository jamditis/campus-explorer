import bpy, os, math
from mathutils import Vector
sc=bpy.context.scene
cx,cy,cz=[float(a) for a in os.environ.get("CTR","-83.5,257,150").split(",")]
views=os.environ.get('VIEWS','SW,SE,S,W').split(',')
D={'SW':(-1,-1),'SE':(1,-1),'S':(0,-1),'W':(-1,0),'E':(1,0),'NE':(1,1),'NW':(-1,1),'N':(0,1)}
for o in bpy.data.objects:
    if o.get('tx_obj') and o.type=='MESH': print('OBJ',o.name,len(o.data.polygons),[m.name for m in o.data.materials])
for v in views:
    dx,dy=D[v]; r=float(os.environ.get('R','55'))
    p=Vector((cx+dx*r/math.hypot(dx,dy),cy+dy*r/math.hypot(dx,dy),cz+float(os.environ.get('DZ','12'))))
    cd=bpy.data.cameras.new('p'); c=bpy.data.objects.new('UBP_'+v,cd); sc.collection.objects.link(c)
    c.location=p; c.rotation_euler=(Vector((cx,cy,cz))-p).to_track_quat('-Z','Y').to_euler(); cd.lens=30
    sc.camera=c; sc.render.resolution_x=800; sc.render.resolution_y=450; sc.cycles.samples=int(os.environ.get('SPP','16'))
    sc.render.filepath=os.environ['OUTP']+v+'.jpg'; sc.render.image_settings.file_format='JPEG'
    bpy.ops.render.render(write_still=True); print('WROTE',sc.render.filepath)
