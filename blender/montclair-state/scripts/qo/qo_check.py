import bpy
from mathutils import Vector
exec(open('scripts/qo/qo_probe2.py').read().split('# road lift')[0].replace('rows[::max(1,len(rows)//60)]','[r for r in rows if r[4]!="Roof_tile_or_membrane"][:20]'))
dg=bpy.context.evaluated_depsgraph_get()
def ev(n): return bpy.data.objects[n].evaluated_get(dg)
T=[ev(n) for n in ('Terrain_LiDAR_DTM_1m','QJ_NE_seam_fill_UNVERIFIED','Context_skirt_3DEP_ortho_4km')]
def gz(x,y):
  b=None
  for e in T:
    iw=e.matrix_world.inverted(); r=e.ray_cast(iw@Vector((x,y,300)),Vector((0,0,-1)))
    if r[0]:
      z=(e.matrix_world@r[1]).z; b=z if b is None else max(b,z)
  return b
for n,off in (('Roads_OSM',0.03),('Footpaths_OSM',0.05)):
  o=ev(n); M=o.matrix_world; bad=[]; under=0
  for v in o.data.vertices:
    w=M@v.co
    if 205<w.x<235 and 195<w.y<230:
      g=gz(w.x,w.y)
      if g is None: continue
      if w.z-g-off>0.08: bad.append((round(w.x,2),round(w.y,2),round(w.z-g,2)))
      if w.z<g: under+=1
  bad.sort(key=lambda t:-t[2]); print('LIFT',n,len(bad),bad[:8],'under_ground',under)
