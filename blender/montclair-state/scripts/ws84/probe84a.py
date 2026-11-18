import bpy,bmesh,math
from mathutils import Vector
sc=bpy.context.scene
for cn in ['WS80_CAM_oblique_sprague_lot_SW','WS81_CAM_eye_grandstand_lawn_from_SE']:
    c=bpy.data.objects.get(cn)
    if c: print('P84 CAM',cn,tuple(round(v,1) for v in c.location),tuple(round(math.degrees(v),1) for v in c.rotation_euler))
T=bpy.data.objects['Terrain']
print('P84 Terrain mods',[(m.type,m.name,m.show_render) for m in T.modifiers])
BOX=(-320,-170,-230,-95)
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[p.x for p in bb]; ys=[p.y for p in bb]
    if max(xs)<BOX[0] or min(xs)>BOX[1] or max(ys)<BOX[2] or min(ys)>BOX[3]: continue
    if (max(xs)-min(xs))>2000: tag='HUGE'
    else: tag=''
    print('P84 OB',o.name,tag,'x %.0f..%.0f y %.0f..%.0f z %.1f..%.1f'%(min(xs),max(xs),min(ys),max(ys),min(p.z for p in bb),max(p.z for p in bb)),'mats',[m.name for m in o.data.materials if m][:3])
dg=bpy.context.evaluated_depsgraph_get()
Te=T.evaluated_get(dg); me=Te.to_mesh()
b=bmesh.new(); b.from_mesh(me); b.transform(T.matrix_world)
b.faces.ensure_lookup_table()
fs=[f for f in b.faces if BOX[0]<f.calc_center_median().x<BOX[1] and BOX[2]<f.calc_center_median().y<BOX[3]]
print('P84 terrain faces in box',len(fs))
S=set(fs); cre=[]
for f in fs:
    for e in f.edges:
        if len(e.link_faces)==2:
            a,c=e.link_faces
            ang=math.degrees(a.normal.angle(c.normal,0))
            if ang>6: cre.append((ang,e))
print('P84 creases>6deg',len(set(id(e) for _,e in cre)))
# grid summary of crease edge positions
from collections import Counter
cnt=Counter()
for ang,e in cre:
    m=(e.verts[0].co+e.verts[1].co)/2; cnt[(int(m.x//10)*10,int(m.y//10)*10)]+=1
for k,v in sorted(cnt.items(),key=lambda q:-q[1])[:25]: print('P84 cell',k,v)
areas=sorted([f.calc_area() for f in fs]); print('P84 face area med %.2f max %.1f'%(areas[len(areas)//2],areas[-1]))
big=[f for f in fs if f.calc_area()>20]; print('P84 big faces',len(big))
for f in big[:15]:
    c=f.calc_center_median(); print('P84 BF %.1f %.1f z%.2f a%.1f n(%.2f,%.2f,%.2f) mat%d'%(c.x,c.y,c.z,f.calc_area(),*f.normal,f.material_index))
