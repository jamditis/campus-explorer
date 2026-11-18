import bpy,os
from mathutils import Vector
if 'WS81_lot_seam_underlay_asphalt' not in bpy.data.objects:
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws81/underlay81.py').read())
bpy.ops.wm.save_mainfile(); print('WS81a SAVED',flush=True)
# pixel probes (704x396 frame space) for the lawn lines/black wedge (oblique) and lane eye view
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def mkcam(name,eye,tgt,lens):
    c=bpy.data.cameras.new(name); c.lens=lens; o=bpy.data.objects.new(name,c)
    d=Vector((tgt[0]-eye[0],tgt[1]-eye[1],tgt[2]-eye[2])); o.location=eye; o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); return o
def gz(x,y):
    ok,loc,*_=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1))); return loc.z if ok else 125
sc.render.resolution_x=704; sc.render.resolution_y=396
specs={'OBL':((-290,-165,175),(-245,-108),30,None,[(470,190),(462,220),(455,250),(447,285),(440,300),(430,300),(455,315),(445,325),(420,290),(300,250)]),
       'LANE':((-227,-134,0),(-229,-96),28,1.7,[(50,262),(150,252),(250,244),(100,270),(200,258),(470,285),(440,292),(160,330)])}
for k,(e,t,lens,h,pxs) in specs.items():
    ez=e[2] if h is None else gz(e[0],e[1])+h; tz=gz(t[0],t[1])+(0 if h is None else 0.5)
    c=mkcam('WS81_probe_'+k,(e[0],e[1],ez),(t[0],t[1],tz),lens); sc.collection.objects.link(c); bpy.context.view_layer.update()
    TR,BR,BL,TL=[c.matrix_world@v for v in c.data.view_frame(scene=sc)]; o=c.matrix_world.translation
    for px,py in pxs:
        u=px/704; v=py/396; p=(TL.lerp(TR,u)).lerp(BL.lerp(BR,u),v); d=(p-o).normalized(); org=o.copy(); hits=[]
        for _ in range(3):
            ok,loc,n,i,ob,m=sc.ray_cast(dg,org,d)
            if not ok: break
            try: mat=ob.material_slots[ob.data.polygons[i].material_index].material.name
            except Exception: mat=None
            hits.append((ob.name,mat,tuple(round(x,2) for x in loc),round(n.z,2))); org=loc+d*0.01
        print('WS81PX',k,px,py,hits,flush=True)
    bpy.data.objects.remove(c)
