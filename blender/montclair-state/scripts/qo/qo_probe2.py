import bpy, numpy as np
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
def ev(n): return bpy.data.objects[n].evaluated_get(dg)
R=ev('Center for Computing and Information Science roof (LiDAR)'); me=R.data; mw=R.matrix_world
print('ROOF mods',[m.name for m in bpy.data.objects[R.name].modifiers])
rows=[]
for p in me.polygons:
  c=mw@p.center
  if 33<c.x<38.5 and 204<c.y<224: rows.append((round(c.x,2),round(c.y,2),round(c.z,2),round(p.normal.z,2),R.material_slots[p.material_index].name))
rows.sort(); print('ROOF faces near podium edge',len(rows))
for r in rows[::max(1,len(rows)//60)]: print(' ',r)
for n in ['QF_CCIS_stucco_skin_recessed_openings_photo','QF_CCIS_windows_red_frames_spandrels_brackets_photo','Center for Computing and Information Science walls']:
  o=ev(n); M=o.matrix_world; vs=[M@v.co for v in o.data.vertices]
  sel=[v for v in vs if 204<v.y<224 and v.x>33]
  if sel: print('OBJ',n,'x %.2f..%.2f z %.2f..%.2f'%(min(v.x for v in sel),max(v.x for v in sel),min(v.z for v in sel),max(v.z for v in sel)))
  zs=sorted(set(round(v.z,2) for v in sel if v.z>140.0)); print('  zlevels>140',zs[:20])
# road lift near (221,214.5)
T=[ev(n) for n in ('Terrain_LiDAR_DTM_1m','QJ_NE_seam_fill_UNVERIFIED','Context_skirt_3DEP_ortho_4km')]
def gz(x,y):
  b=None
  for e in T:
    iw=e.matrix_world.inverted(); r=e.ray_cast(iw@Vector((x,y,300)),Vector((0,0,-1)))
    if r[0]:
      z=(e.matrix_world@r[1]).z; b=z if b is None else max(b,z)
  return b
for n,off in (('Roads_OSM',0.03),('Footpaths_OSM',0.05)):
  o=ev(n); M=o.matrix_world; bad=[]
  for v in o.data.vertices:
    w=M@v.co
    if 205<w.x<235 and 200<w.y<230:
      g=gz(w.x,w.y)
      if g is not None and w.z-g-off>0.08: bad.append((round(w.x,2),round(w.y,2),round(w.z-g,2)))
  bad.sort(key=lambda t:-t[2]); print('LIFT',n,len(bad),bad[:15])
print('QK mods',[(m.name,m.type) for m in bpy.data.objects['Roads_OSM'].modifiers])
mat=bpy.data.materials['Ground_ortho_grass']; nt=mat.node_tree
for nd in nt.nodes: print('GNODE',nd.name,nd.type,getattr(nd,'image',None) and nd.image.name,[ (l.from_node.name,l.to_socket.name) for i in nd.inputs for l in i.links])
