# ws246 low-memory render tweaks (after upd239): simplify subdiv 0, no child particles, report what survives the cull
import bpy, os
from mathutils import Vector
sc=bpy.context.scene; sc.render.use_simplify=True; sc.render.simplify_subdivision_render=0; sc.render.simplify_child_particles_render=0.0
cx0,cx1,cy0,cy1=map(float,os.environ['CULL'].split(','))
vis=[]; 
for o in sc.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<cx0 or min(xs)>cx1 or max(ys)<cy0 or min(ys)>cy1: continue
    vis.append((len(o.data.vertices),o.name[:40],[m.type for m in o.modifiers if m.show_render][:3],len(o.particle_systems)))
vis.sort(reverse=True); print('P246L vis',len(vis),sum(v[0] for v in vis),vis[:12],flush=True)
sc.render.threads_mode='FIXED'; sc.render.threads=2; sc.cycles.texture_limit_render='512'
