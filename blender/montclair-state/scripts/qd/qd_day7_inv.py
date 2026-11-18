import bpy, os, json
from mathutils import Vector
BB={'CCIS':(4.3,41.7,185.4,244.1),'CELS':(67.7,130.1,149.9,218.7)}
out=os.environ['QD_OUT']; f=open(out,'a'); f.write('\n## %s\n'%bpy.data.filepath)
for key,(x0,x1,y0,y1) in BB.items():
    hits=[]
    for o in bpy.data.objects:
        if o.type!='MESH' or max(o.dimensions)>400: continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        cx=sum(p.x for p in bb)/8; cy=sum(p.y for p in bb)/8
        if x0-5<cx<x1+5 and y0-5<cy<y1+5: hits.append((o.name,len(o.data.polygons),o.hide_render,o.users_collection[0].name if o.users_collection else ''))
    f.write('- %s: %d objects centred in the OSM bbox ±5 m\n'%(key,len(hits)))
    for h in sorted(hits,key=lambda h:-h[1])[:25]: f.write('  - `%s` %d polys hide_render=%s coll `%s`\n'%h)
rich=[o.name for o in bpy.data.objects if 'ichardson' in o.name]
f.write('- Richardson-named objects: %d %s\n'%(len(rich),rich[:15])); f.close()
