import bpy, bmesh
o0=bpy.data.objects['WS4_Planting_bed_mulch_at_Cole_sign_UNVERIFIED']
X=(-78.8,-75.2); Y=(-53.2,-51.5)
for o in bpy.data.objects:
  if o.type!='MESH' or o==o0 or o.name.startswith('WS4') or 'Terrain' in o.name: continue
  mw=o.matrix_world
  cs=[mw@__import__('mathutils').Vector(c) for c in o.bound_box]
  if min(c.x for c in cs)>X[1] or max(c.x for c in cs)<X[0] or min(c.y for c in cs)>Y[1] or max(c.y for c in cs)<Y[0]: continue
  hits=[p.index for p in o.data.polygons if X[0]<(mw@p.center).x<X[1] and Y[0]<(mw@p.center).y<Y[1]]
  if hits: print('HIT',o.name,len(hits),len(o.data.polygons))
  n=o.name.lower()
  if hits and any(k in n for k in ('lawn','turf','grass')) and len(hits)<200:
    bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.faces[i] for i in hits],context='FACES_ONLY'); bm.to_mesh(o.data); bm.free(); print('CUT',o.name,len(hits))
bpy.ops.wm.save_mainfile(); print('SAVED')
