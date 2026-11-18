import bpy, mathutils
sc=bpy.context.scene
lc=bpy.context.view_layer.layer_collection
def find(l,n):
    if l.name==n: return l
    for c in l.children:
        r=find(c,n)
        if r: return r
ng=find(lc,'NG_CCOM_1F_open_floor_20261030ng'); ng.exclude=True
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
for z in (139.0,143.0):
  for y in range(-17,16,1):
    o=mathutils.Vector((-1,y+0.5,z)); hits=[]
    for k in range(6):
        hit,loc,n,i,ob,_=sc.ray_cast(dg,o,mathutils.Vector((1,0,0)),distance=35)
        if not hit: break
        hits.append('%s@%.1f'%(ob.name[:28],loc.x)); o=loc+mathutils.Vector((0.02,0,0))
    print('Z',z,'Y',y+0.5,' | '.join(hits))
