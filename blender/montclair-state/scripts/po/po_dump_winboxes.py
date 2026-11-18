# po: dump world-space 2D hulls + z ranges of every PJ Feliciano window unit (mesh islands) -> data/po/pj_winboxes.json
import bpy, bmesh, json
out=[]
for o in bpy.data.objects:
    if not (o.name.startswith('PJ_Feliciano_') and 'windows' in o.name and o.type=='MESH'): continue
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); mw=o.matrix_world
    seen=set()
    for v in bm.verts:
        if v.index in seen: continue
        stack=[v]; isl=[]
        seen.add(v.index)
        while stack:
            a=stack.pop(); isl.append(a)
            for e in a.link_edges:
                b=e.other_vert(a)
                if b.index not in seen: seen.add(b.index); stack.append(b)
        P=[mw@x.co for x in isl]
        out.append({'o':o.name,'xy':[(p.x,p.y) for p in P],'z0':min(p.z for p in P),'z1':max(p.z for p in P)})
    bm.free()
json.dump(out,open('data/po/pj_winboxes.json','w')); print('WINBOXES',len(out))
