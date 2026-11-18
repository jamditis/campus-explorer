import bpy
from mathutils import Vector
w=bpy.data.objects['Calcia Hall walls']; me=w.data; mw=w.matrix_world; uv=me.uv_layers['facade'].data; wt=me.attributes.get('win_top')
for p in me.polygons:
    n=mw.to_3x3()@p.normal
    if abs(n.z)>0.1 or p.area<3: continue
    L=list(p.loop_indices); U=[uv[l].uv for l in L]; P=[mw@me.vertices[me.loops[l].vertex_index].co for l in L]
    print('F',p.index,len(L),round(p.area,1),'u',round(min(q.x for q in U),2),round(max(q.x for q in U),2),'v',round(min(q.y for q in U),2),round(max(q.y for q in U),2),'z',round(min(q.z for q in P),2),round(max(q.z for q in P),2),'wt',[round(wt.data[me.loops[l].vertex_index].value,2) for l in L][:4] if wt else None)
