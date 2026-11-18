import bpy, json
from mathutils import Vector
R=(-132.5,-82.5,-65.7,-27.0)
def inR(p): return R[0]<p.x<R[1] and R[2]<p.y<R[3]
out={'R':R}
for name in ['Footpaths_OSM','COLE_add_forecourt_bu']:
  o=bpy.data.objects[name]; me=o.data; mw=o.matrix_world
  print('MODS',name,[(md.name,md.type,md.node_group.name if md.type=='NODES' and md.node_group else '', md.show_render) for md in o.modifiers])
  fl=[]
  for f in me.polygons:
    c=mw@f.center
    if name.startswith('COLE') or inR(c):
      fl.append({'i':f.index,'m':f.material_index,'v':[list((mw@me.vertices[k].co)[:]) for k in f.vertices]})
  out[name]=fl
  print('FACES',name,len(fl))
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
print('MODS terrain',[(md.name,md.type,md.node_group.name if md.type=='NODES' and md.node_group else '',md.show_render) for md in t.modifiers])
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws3/extract.json','w'))
