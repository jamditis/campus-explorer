import bpy
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
X0,X1,Y0,Y1=-275,-236,-70,-44
with bpy.data.libraries.load(src) as (fr,to): names=[n for n in fr.objects if not n.startswith(('T_','Context_skirt')) and not any(k in n.lower() for k in ('tuft','clover','flower','annual','newsroom','leaf'))]
sc=bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
for k in range(0,len(names),300):
    with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=names[k:k+300]
    for o in to.objects:
        if not o: continue
        ok=False
        if o.type=='MESH' and not o.hide_render:
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]
            ok=min(xs)<X1 and max(xs)>X0 and min(ys)<Y1 and max(ys)>Y0 and max(xs)-min(xs)<1200
        if ok: sc.collection.objects.link(o)
    bpy.data.batch_remove([o for o in to.objects if o and o.name not in sc.objects]); bpy.data.orphans_purge(do_recursive=True)
dg=bpy.context.evaluated_depsgraph_get()
print('P4 objs',len(sc.objects))
for y in (-62,-59,-56,-53,-50):
    row=[]
    for x in range(-272,-238,2):
        r=sc.ray_cast(dg,Vector((x,y,170)),Vector((0,0,-1)))
        row.append('%d:%s@%.2f'%(x,r[4].name[:9],r[1].z) if r[0] else '%d:-'%x)
    print('P4 y',y,' '.join(row))
