# W59b: what covers the M3b gap x -395..-380, y -52..-21 (base mesh vs evaluated), per ground object
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); out=[]
pts=[(-387.5,-35.5),(-385.5,-45.5),(-390.5,-25.5),(-383.5,-22.5),(-392.5,-50.5)]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    mw=o.matrix_world; me=o.data
    if not me.polygons: continue
    tb=BVHTree.FromPolygons([(mw@v.co)[:] for v in me.vertices],[p.vertices[:] for p in me.polygons])
    hb=[tb.ray_cast(Vector((x,y,600)),Vector((0,0,-1)))[0] for x,y in pts]
    if not any(hb): continue
    ev=o.evaluated_get(dg); m2=ev.to_mesh()
    te=BVHTree.FromPolygons([(mw@v.co)[:] for v in m2.vertices],[p.vertices[:] for p in m2.polygons]); ev.to_mesh_clear()
    he=[te.ray_cast(Vector((x,y,600)),Vector((0,0,-1)))[0] for x,y in pts]
    out.append('%s mods=%s base=%s eval=%s'%(o.name[:60],[m.name for m in o.modifiers if m.show_render][:8],[round(h.z,2) if h else None for h in hb],[round(h.z,2) if h else None for h in he]))
open('/workspace/nj-scenes/montclair-state/scripts/ws242/probe242e.out','w').write('\n'.join(out)); print('P242E ok',flush=True); os._exit(0)
