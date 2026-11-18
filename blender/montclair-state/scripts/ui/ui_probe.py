"""Read-only probe: QXP/QY/walks vs strip between south walk and plaza E of Partridge."""
import bpy, json, math
from mathutils import Vector
D='/workspace/nj-scenes/montclair-state/'
out={}
names=['QXP_pedestrian_area_313024781_paving_UNVERIFIED','QY_plaza_rim_band_313024781_UNVERIFIED',
 'UG_Partridge_E_seam_fill_lawn_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED',
 'UH_Partridge_E_seam_grass_points_UNVERIFIED','Footpaths_OSM',
 'TY_footway_313026406_to_Partridge_UNVERIFIED','TY_footway_313026407_to_Partridge_UNVERIFIED',
 'TY_footway_313026405_to_Partridge_UNVERIFIED','TY Partridge entrance steps+landings (UNVERIFIED)',
 'TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)',
 'TY_footway_313026404_to_Partridge_UNVERIFIED']
for n in names:
 o=bpy.data.objects.get(n)
 if not o: out[n]='MISS'; continue
 mw=o.matrix_world; xs=[]; ys=[]; zs=[]
 for v in o.data.vertices:
  p=mw@v.co; xs.append(p.x); ys.append(p.y); zs.append(p.z)
 out[n]={'nv':len(o.data.vertices),'nf':len(o.data.polygons),
  'x':[round(min(xs),2),round(max(xs),2)],'y':[round(min(ys),2),round(max(ys),2)],
  'z':[round(min(zs),2),round(max(zs),2)],
  'mats':[s.material.name if s.material else None for s in o.material_slots]}

# QXP face centers in strip band x -70..-35, y 244..252
o=bpy.data.objects['QXP_pedestrian_area_313024781_paving_UNVERIFIED']
mw=o.matrix_world
faces=[]
for poly in o.data.polygons:
 c=mw@poly.center
 if -70<c.x<-35 and 244<c.y<253:
  faces.append((round(c.x,2),round(c.y,2),round(c.z,2)))
out['qxp_strip_faces_n']=len(faces)
out['qxp_strip_faces_sample']=faces[::max(1,len(faces)//40)][:40]

# south walk candidates: Footpaths + TY walks near Partridge S
# sample which object sits at (x,y) for a grid
dg=bpy.context.evaluated_depsgraph_get()
cands=[n for n in names if bpy.data.objects.get(n)]
def hits(x,y):
 hs=[]
 for n in cands:
  o=bpy.data.objects[n]; e=o.evaluated_get(dg); mw=o.matrix_world; iw=mw.inverted()
  d=(iw.to_3x3()@Vector((0,0,-1))).normalized()
  r=e.ray_cast(iw@Vector((x,y,400)), d)
  if r[0]:
   hs.append((n,(mw@r[1]).z))
 hs.sort(key=lambda t:-t[1])
 return hs[:4]
grid=[]
for x in range(-68,-36,3):
 for y in [244.5,245.5,246.5,247.5,248.5,249.5,250.5,251.5]:
  hs=hits(x+0.5,y)
  grid.append({'xy':[x+0.5,y],'top':[(n,round(z,3)) for n,z in hs]})
out['grid']=grid
out['n_objects']=len(bpy.data.objects)
out['n_mats']=len(bpy.data.materials)
out['n_meshes']=len(bpy.data.meshes)
out['n_cams']=len(bpy.data.cameras)
json.dump(out, open(D+'data/ui/probe.json','w'), indent=1)
print('PROBE ok faces', out['qxp_strip_faces_n'], 'objs', out['n_objects'])
# print a compact y-slice at x=-55
for g in grid:
 if abs(g['xy'][0]+55)<0.1:
  print(g['xy'], '->', g['top'][:3])
