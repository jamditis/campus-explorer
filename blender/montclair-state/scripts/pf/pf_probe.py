import bpy, mathutils
NORTH='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
pts=[(-222,145),(-215,150),(-210,155),(-220,160),(-214,165),(-208,170),(-212,172),(-205,166.5),(-230,175),(-245,176),(-200,168),(-216,169)]
for x,y in pts:
    hits=[]; o=mathutils.Vector((x,y,175))
    for k in range(4):
        h,loc,n,i,ob,m=sc.ray_cast(dg,o,(0,0,-1))
        if not h: break
        hits.append((ob.name[:28],round(loc.z,2))); o=loc-mathutils.Vector((0,0,0.01))
    print('G',x,y,hits)
for c in bpy.data.collections:
    if 'Felic' in c.name or 'felic' in c.name: print('MCOLL',c.name)
