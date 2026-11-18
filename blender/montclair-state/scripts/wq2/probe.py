import bpy, collections, json
from mathutils import Vector
sc=bpy.context.scene
cam=bpy.data.objects['CAM_oblique_cole_hall_nnw_br']
print('CAM',list(cam.matrix_world.translation),cam.data.lens)
dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc)
mw=cam.matrix_world; o=mw.translation
tl,bl,br_,tr=None,None,None,None
# frame order: tr, br, bl, tl
tr,br_,bl,tl=[mw@v for v in fr]
NX,NY=64,36
grid={}
cnt=collections.Counter()
for j in range(NY):
  row=''
  for i in range(NX):
    u=(i+.5)/NX; v=(j+.5)/NY
    top=tl.lerp(tr,u); bot=bl.lerp(br_,u); p=top.lerp(bot,v)
    d=(p-o).normalized()
    hit,loc,nor,idx,ob,_=sc.ray_cast(dg,o,d)
    if not hit: key='SKY'
    else:
      m=ob.active_material.name if ob.active_material else '-'
      try:
        mi=ob.data.polygons[idx].material_index; m=ob.material_slots[mi].material.name
      except Exception: pass
      key=f'{ob.name}|{m}'
      grid[(i,j)]=(key,[round(x,1) for x in loc])
    cnt[key]+=1
for k,n in cnt.most_common(60): print(n,k)
json.dump({f'{i},{j}':v for (i,j),v in grid.items()},open('/workspace/nj-scenes/montclair-state/scripts/wq2/probe.json','w'))
