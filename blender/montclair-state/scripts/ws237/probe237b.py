# read-only: dump node trees of the ground materials on both sides of the W53p seam
import bpy, os
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('M3b_','M3a_','PK_Feliciano','WS60_terrain','WS68_RHD_ground'))]
for o in b.objects:
    print('OBJ',o.name,[m.name for m in o.data.materials],len(o.data.polygons),[ (uv.name) for uv in o.data.uv_layers],[a.name for a in o.data.attributes if a.domain in('POINT','CORNER','FACE')][:12])
seen=set()
for o in b.objects:
  for m in o.data.materials:
    if not m or m.name in seen: continue
    seen.add(m.name); print('MAT',m.name)
    if not m.use_nodes: continue
    for n in m.node_tree.nodes:
        ex=''
        if n.type=='TEX_IMAGE' and n.image: ex=f'img={n.image.name} {n.image.filepath} {tuple(n.image.size)}'
        if n.type=='UVMAP': ex='uv='+n.uv_map
        if n.type=='ATTRIBUTE': ex='attr='+n.attribute_name
        vals=[(i.name,tuple(i.default_value)[:4] if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if not i.is_linked and hasattr(i,'default_value') and i.name in('Fac','Color','Color1','Color2','A','B','Scale','Roughness','Base Color','Strength','Hue','Saturation','Value','Gamma','Bright','Contrast')]
        print('  N',n.name,n.type,ex,vals)
    for l in m.node_tree.links: print('  L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
