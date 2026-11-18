import bpy, bmesh
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
# objects whose world bbox overlaps the band
X0,X1,Y0,Y1=4,12,-34,-26
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
    if min(xs)<X1 and max(xs)>X0 and min(ys)<Y1 and max(ys)>Y0 and (max(xs)-min(xs))<2000:
        print('OBJ',o.name,o.type,round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(zs),2),round(max(zs),2),[m.name for m in o.data.materials][:4] if hasattr(o.data,'materials') else '', 'hide',o.hide_render)
# top-down ray grid: first hit
for y in [-34,-32,-31,-30,-29,-28,-26]:
    row=[]
    for x in [2,4,6,7,8,9,10,12]:
        r=bpy.context.scene.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
        row.append(f"{x}:{r[4].name[:18] if r[0] else '-'}@{r[1].z:.2f}" if r[0] else f"{x}:-")
    print('Y',y,' | '.join(row))
# grass counts in band
for name in ('Lawn_grass_instanced (3g)','dS_grass_ccom_points'):
    o=bpy.data.objects.get(name)
    if not o: continue
    m=o.matrix_world; n=sum(1 for v in o.data.vertices if X0<(m@v.co).x<X1 and Y0<(m@v.co).y<Y1)
    print('GRASS',name,n)
ap=bpy.data.objects['CCOM_dock_apron_20261014jf3']
for mat in ap.data.materials:
    print('APMAT',mat.name,[ (n.type,n.name) for n in mat.node_tree.nodes])
