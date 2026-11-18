import bpy,bmesh,numpy as np
from mathutils import Vector
for n in ['UA_SkylineWay_south_232846698_UNVERIFIED','WS110_NormalAve_carriageway_W11p3_ws84prep_ortho2020_UNVERIFIED','WS110_NormalAve_curb_W11p3_ws84prep_ortho2020_UNVERIFIED']:
    o=bpy.data.objects[n]; V=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices])
    print(n,V.min(0).round(1),V.max(0).round(1))
o=bpy.data.objects['Roads_OSM']; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data)
c=[mw@f.calc_center_median() for f in bm.faces]
sel=[p for p in c if -75<p.x<-55 and -300<p.y<-190]
print('Roads_OSM faces in corridor',len(sel), (min(p.y for p in sel),max(p.y for p in sel),min(p.x for p in sel),max(p.x for p in sel)) if sel else None)
# which walks in corridor
o=bpy.data.objects['Footpaths_OSM']; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); c=[mw@f.calc_center_median() for f in bm.faces]
s=[p for p in c if -75<p.x<-55 and -300<p.y<-190]; print('Footpaths in corridor',len(s),(min(p.y for p in s),max(p.y for p in s),min(p.x for p in s),max(p.x for p in s)) if s else None)
ws=[o for o in bpy.data.objects if o.name.startswith('WS134_ground_patch')][0]; V=np.array([tuple(v.co) for v in ws.data.vertices]); print('patch',V.min(0).round(1),V.max(0).round(1))
for xs in (-71,-65.5,-60):
  for y in (-200,-240,-280):
    pass
