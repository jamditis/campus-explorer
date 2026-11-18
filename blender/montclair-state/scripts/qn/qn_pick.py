import bpy,os
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['QM_CAM_eye_cels_from_east']; sc.camera=cam
sc.render.resolution_x=1024; sc.render.resolution_y=576
dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
o=mw.translation
def ray(px,py):
    u=px/1024; v=1-py/576
    tl,tr,br,bl=fr[1],fr[0],fr[3],fr[2]  # view_frame order: tr, br, bl, tl
    tr,br,bl,tl=fr
    p=bl+(br-bl)*u+(tl-bl)*v
    d=(mw@p-o).normalized()
    r=sc.ray_cast(dg,o,d)
    return r
for px,py in [(355,530),(345,515),(365,545),(250,470),(420,500),(600,520),(800,540),(900,470),(200,540)]:
    r=sc.ray_cast(dg,o,(mw@(lambda u,v:(fr[2]+(fr[1]-fr[2])*0+ (fr[1]-fr[2])*0))(0,0)-o)) if False else ray(px,py)
    ok,loc,n,fi,ob,_=r
    print(px,py,ob.name if ob else None,fi,tuple(round(c,2) for c in loc) if ok else None, round(n.z,2) if ok else None, ob.material_slots[ob.evaluated_get(dg).data.polygons[fi].material_index].name if ok and ob.type=='MESH' and len(ob.material_slots) else '')
print('cam',tuple(round(c,2) for c in o))
nt=bpy.data.materials['Ground_ortho_grass'].node_tree
for nd in nt.nodes:
    if nd.type in('UVMAP','TEX_IMAGE','TEX_COORD','ATTRIBUTE'): print(nd.type,nd.name,getattr(nd,'uv_map',''),getattr(nd,'attribute_name',''), nd.image.name if nd.type=='TEX_IMAGE' and nd.image else '', nd.image.size[:] if nd.type=='TEX_IMAGE' and nd.image else '')
