import bpy
from mathutils import Vector
from collections import Counter
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def probe(cn,rows,cols,ylo=0.0,yhi=1.0):
  cam=bpy.data.objects[cn]; d=cam.data
  fr=d.view_frame(scene=sc); mw=cam.matrix_world; o=mw.translation
  print('CAM',cn,'loc',tuple(round(v,2) for v in o))
  C=Counter(); pts={}
  for r in range(rows):
    for c in range(cols):
      u=(c+.5)/cols; v=ylo+(yhi-ylo)*(r+.5)/rows
      # frame corners: 0 TR,1 BR,2 BL,3 TL
      top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); p=bot.lerp(top,v)
      w=mw@p; dr=(w-o).normalized()
      h,loc,n,fi,ob,m=sc.ray_cast(dg,o,dr)
      if not h: C['sky']+=1; continue
      e=ob.evaluated_get(dg); mn='?'
      try: mn=e.material_slots[e.data.polygons[fi].material_index].name
      except Exception: pass
      k=(ob.name,mn); C[k]+=1; pts.setdefault(k,[]).append(loc)
  for k,n in C.most_common(25):
    if k=='sky': print(' sky',n); continue
    L=pts[k]; print(' %4d %s | %s | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f'%(n,k[0],k[1],min(p.x for p in L),max(p.x for p in L),min(p.y for p in L),max(p.y for p in L),min(p.z for p in L),max(p.z for p in L)))
probe('QM_CAM_eye_cels_from_west',14,20,0.0,0.32)
probe('QM_CAM_closeup_ccis_podium_edge_east',16,24)
img=bpy.data.images.get('ortho2020_north.jpg.001'); print('IMG',img and img.filepath, img and [u for u in ('users',)] , img and img.users)
for i in bpy.data.images:
  if 'ortho2020_north' in i.name: print(' img',i.name,i.filepath,i.packed_file is not None,i.users)
