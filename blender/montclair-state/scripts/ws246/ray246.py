# ws246 camera-ray probe: which objects/materials do the pixels in a box of a look render hit (evaluated scene)
import bpy, os, collections
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cx,cy,cz,tx,ty,tz,fl=[float(a) for a in os.environ['CAM'].split(',')]
c=bpy.data.objects.new('C246',bpy.data.cameras.new('C246')); sc.collection.objects.link(c)
c.location=(cx,cy,cz); c.data.lens=fl; c.rotation_euler=(Vector((tx,ty,tz))-Vector((cx,cy,cz))).to_track_quat('-Z','Y').to_euler()
sc.render.resolution_x=1280; sc.render.resolution_y=720; bpy.context.view_layer.update()
fr=c.data.view_frame(scene=sc); M=c.matrix_world
x0,x1,y0,y1=[float(v) for v in os.environ['PIX'].split(',')]  # fractions of width/height, y from top
cnt=collections.Counter(); ex={}
for i in range(12):
    for j in range(8):
        u=x0+(x1-x0)*i/11; v=y0+(y1-y0)*j/7
        # view_frame: [tr, br, bl, tl]
        tr,br,bl,tl=fr; top=tl.lerp(tr,u); bot=bl.lerp(br,u); p=top.lerp(bot,v)
        d=(M.to_3x3()@p).normalized(); o=M.translation
        for _k in range(8):
            hit,loc,nor,idx,ob,_=sc.ray_cast(dg,o,d)
            if not (ob and (ob.hide_render or ob.name.startswith(('C246','C189')))): break
            o=loc+d*0.01
        k=(ob.name[:44] if ob else 'SKY'); 
        if ob and ob.type=='MESH' and ob.data.materials:
            e=ob.evaluated_get(dg); 
            try: k+=' | '+str(e.data.polygons[idx].material_index)+':'+(e.data.materials[e.data.polygons[idx].material_index].name[:30] if e.data.materials[e.data.polygons[idx].material_index] else 'None')
            except Exception: pass
        cnt[k]+=1; ex.setdefault(k,tuple(round(a,1) for a in loc))
for k,n in cnt.most_common(): print('P246R',n,k,ex[k],flush=True)
os._exit(0)
