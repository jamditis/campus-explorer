import bpy, numpy as np, json
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['WS196_lot_accessible_ISA_symbol_paint_UNVERIFIED','WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED','WS76_lot_stall_paint_white_ortho2020_UNVERIFIED',
'WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS94_lot_slit_filler_asphalt_UNVERIFIED','WS199_lot_gap_patch_asphalt_UNVERIFIED','WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges','WS81_lot_seam_underlay_asphalt','WS96_lot_E_edge_gap_filler_asphalt_UNVERIFIED','WS207_lot_pad_foot_fill_asphalt_ortho2020_UNVERIFIED','WS204_CollegeAve_lot_entrance_asphalt_fill_ortho2020']
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in names if n in a.objects]
out={}
for o in b.objects:
    me=o.data; mw=o.matrix_world
    print('O211',o.name,len(me.vertices),len(me.polygons),[m.name if m else None for m in me.materials],[(m.type,m.name) for m in o.modifiers],tuple(round(v,3) for v in o.location),flush=True)
    if 'paint' in o.name:
        V=np.array([(mw@v.co)[:] for v in me.vertices])
        polys=[list(p.vertices) for p in me.polygons]; mi=[p.material_index for p in me.polygons]
        out[o.name]={'V':V.tolist(),'P':polys,'M':mi}
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws211/paint.json','w'))
seen=set()
for o in b.objects:
    for m in o.data.materials:
        if not m or m.name in seen: continue
        seen.add(m.name); print('MAT211',m.name,'users',m.users)
        if m.node_tree:
            for n in m.node_tree.nodes: print('  N',n.type,n.name,n.label)
            for l in m.node_tree.links: print('  L',l.from_node.name,l.from_socket.identifier,'->',l.to_node.name,l.to_socket.identifier)
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM',l.strip())
