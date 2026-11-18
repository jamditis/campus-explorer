import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
seen=set()
for x,y in [(26,117),(30,118),(34,119),(22,116),(38,118),(30,120.5)]:
    hit,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,160)),Vector((0,0,-1)))
    if not hit: print('MISS',x,y); continue
    oe=ob.evaluated_get(dg); me=oe.data
    p=me.polygons[i] if i<len(me.polygons) else None
    mat=ob.material_slots[p.material_index].material.name if p and ob.material_slots else None
    print('HIT',(x,y),ob.name,round(loc.z,2),round(n.z,3),mat,'mods',[md.type for md in ob.modifiers])
    seen.add(mat)
for mn in seen:
    mt=bpy.data.materials.get(mn)
    if not mt or not mt.node_tree: continue
    print('MAT',mn,[ (n.name,n.bl_idname) for n in mt.node_tree.nodes if any(k in n.name.lower() or k in n.bl_idname.lower() for k in ('crack','voronoi','wave','attribute','image','joint','edge','wireframe','bevel','ao'))])
    for n in mt.node_tree.nodes:
        if n.bl_idname=='ShaderNodeTexImage' and n.image: print('  IMG',n.name,n.image.name,n.image.filepath)
