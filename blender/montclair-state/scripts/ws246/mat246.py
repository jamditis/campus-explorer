# ws246 cheap inspect (no depsgraph eval): which ground objects cover the east bank, their materials/node trees and modifiers
import bpy, json, os
S='/workspace/nj-scenes/montclair-state/'
BB=json.load(open(S+'scripts/ws205/bbox205.json'))
cx0,cx1,cy0,cy1=-236,-205,100,150
want=[n for n,(t,hr,x0,x1,y0,y1,z0,z1,cols) in BB.items() if t=='MESH' and not hr and not (x1<cx0 or x0>cx1 or y1<cy0 or y0>cy1) and n.startswith(('M3a_','M3b_','Terrain','WS6','WS60','PK_','PZ_','Context'))]
print('M246 want',want,flush=True)
with bpy.data.libraries.load(S+'montclair_state.blend') as (a,b): b.objects=[n for n in want if n in set(a.objects)]
for o in b.objects:
    if not o: continue
    print('M246 OBJ',o.name,len(o.data.vertices),'mats',[m.name if m else None for m in o.data.materials],'uv',[u.name for u in o.data.uv_layers],'attrs',[a.name for a in o.data.attributes][:20],flush=True)
    print('M246 MODS',[(m.name,m.type) for m in o.modifiers],flush=True)
seen=set()
for o in b.objects:
    if not o: continue
    for m in o.data.materials:
        if not m or m.name in seen or not m.node_tree: continue
        seen.add(m.name)
        print('M246 MAT',m.name,flush=True)
        for n in m.node_tree.nodes:
            ex=''
            if n.type=='TEX_IMAGE' and n.image: ex=n.image.filepath
            if n.type=='ATTRIBUTE': ex=n.attribute_name
            if n.type=='UVMAP': ex=n.uv_map
            if n.type in('RGB',): ex=tuple(round(c,3) for c in n.outputs[0].default_value)
            if n.type=='VALTORGB': ex=[(round(e.position,2),tuple(round(c,2) for c in e.color[:3])) for e in n.color_ramp.elements]
            if n.type=='MIX': ex=(n.data_type,n.blend_type)
            print('M246   ',n.name,n.type,n.label,ex,flush=True)
        for l in m.node_tree.links: print('M246   L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name,flush=True)
import os; os._exit(0)
