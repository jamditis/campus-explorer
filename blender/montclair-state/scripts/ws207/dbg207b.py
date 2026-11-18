TT={o.name[:12]:BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]) for o in bpy.data.objects if o.name.startswith(('WS98_lotE_entry','WS79_lot_E','WS76_accessible_lot_asphalt','WS98_lotE_raised','WS207_lot'))}
for y in (-83.0,-83.5,-84.0,-84.4):
  for x in np.arange(-218.0,-216.2,0.2):
    r=[]
    for n,t in TT.items():
      h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); r.append('%s=%s'%(n[:9],'%.3f'%h[0].z if h[0] else '--'))
    print('D207b %.1f %.1f'%(x,y),' '.join(r))
