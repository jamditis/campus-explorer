import bpy, bmesh, os
from mathutils import Vector
DRY=os.environ.get('DRY')=='1'
ZC=137.45  # ~2.6 m above the walk (walk top ~134.75-134.95)
def inzone(p): return -80<p.x<-45 and -58.4<p.y<-51.9 and p.z<ZC
for o in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('T_') and o.data.name.startswith('Tree_')]:
  mw=o.matrix_world
  if not (-90<mw.translation.x<-35 and -70<mw.translation.y<-38): continue
  bm=bmesh.new(); bm.from_mesh(o.data)
  kill=[f for f in bm.faces if all(inzone(mw@v.co) for v in f.verts)]
  print('TREE',o.name,'faces_in_clearance',len(kill),'of',len(bm.faces))
  if kill and not DRY:
    me=o.data.copy(); me.name=o.data.name+'_limbed_ws10_'+o.name
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=kill,context='FACES')
    bm.to_mesh(me); o.data=me; o['ws10_limbed_up']='faces below %.2f over Cole-Morehead walk removed (pruning clearance)'%ZC
  bm.free()
if not DRY: bpy.ops.wm.save_mainfile(); print('SAVED')
