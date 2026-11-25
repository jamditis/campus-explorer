# W59: Context_skirt modifiers + evaluated free (boundary) edges in the box W of the police building, after each modifier
import bpy, os, bmesh
O=bpy.data.objects.get('Context_skirt_3DEP_ortho_4km')
out=[]
X0,X1,Y0,Y1=-420,-320,-80,10
for m in O.modifiers: out.append('MOD %s %s render=%s'%(m.name,m.type,m.show_render)+((' group='+m.node_group.name) if m.type=='NODES' and m.node_group else ''))
mods=[m for m in O.modifiers if m.show_render]
for m in O.modifiers: m.show_viewport=False
def stat(tag):
    dg=bpy.context.evaluated_depsgraph_get(); ev=O.evaluated_get(dg); me=ev.to_mesh()
    mw=O.matrix_world
    cnt={}; fe=[]
    for e in me.edges:
        pass
    bm=bmesh.new(); bm.from_mesh(me)
    nf=0
    for f in bm.faces:
        c=mw@f.calc_center_median()
        if X0<=c.x<=X1 and Y0<=c.y<=Y1: nf+=1
    bnd=[]
    for e in bm.edges:
        if e.is_boundary:
            a=mw@e.verts[0].co; b=mw@e.verts[1].co
            if X0<=a.x<=X1 and Y0<=a.y<=Y1: bnd.append((round(a.x,1),round(a.y,1),round(a.z,2),round(b.x,1),round(b.y,1)))
    out.append('%s faces_in_box=%d boundary_edges_in_box=%d totfaces=%d'%(tag,nf,len(bnd),len(bm.faces)))
    for t in bnd[:60]: out.append('   B %s'%(t,))
    bm.free(); ev.to_mesh_clear()
stat('raw')
for m in mods:
    m.show_viewport=True; stat('after '+m.name)
open('/workspace/nj-scenes/montclair-state/scripts/ws242/probe242a.out','w').write('\n'.join(out)); print('P242A ok',flush=True); os._exit(0)
