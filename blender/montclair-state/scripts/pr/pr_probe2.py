import bpy
exec(open('scripts/pq/pq_probe.py').read().split("probe('PK")[0])
pts=[(x,y) for y in range(140,320,20) for x in (208,218,228,238,248)]
probe('PK_CAM_oblique_feliciano_from_NW',pts)
for o in bpy.data.objects:
    if o.name.startswith('PO_') : print('OBJ',o.name,o.type,len(o.data.vertices) if o.type=='MESH' else '', [round(x,1) for x in o.dimensions])
