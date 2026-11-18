import bpy
c=bpy.data.collections.get('QP_Richardson_Hall_UNVERIFIED')
def walk(c,d=0):
    print(' '*d+'C',c.name,len(c.objects))
    for o in c.objects:
        mats=[s.material.name if s.material else None for s in o.material_slots]
        bb=[o.matrix_world@__import__('mathutils').Vector(b) for b in o.bound_box]
        zs=[v.z for v in bb]
        print(' '*d,' ',o.name,o.type,(len(o.data.polygons) if o.type=='MESH' else ''),mats,round(min(zs),2),round(max(zs),2))
    for ch in c.children: walk(ch,d+2)
walk(c)
for n in [m.name for m in bpy.data.materials if m.name.startswith('QP_Richardson')]:
    m=bpy.data.materials[n]; print('MAT',n,[ (nd.type,nd.name) for nd in m.node_tree.nodes][:12])
s=bpy.context.scene; print('engine',s.render.engine, s.cycles.max_bounces if hasattr(s,'cycles') else '', s.cycles.transparent_max_bounces)
