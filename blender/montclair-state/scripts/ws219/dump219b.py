import bpy, json
PAIRS={'WS179_CollegeAve_S_leg_crosswalk_line0':'WS179_CollegeAve_S_leg_carriageway','WS179_CollegeAve_S_leg_crosswalk_line1':'WS179_CollegeAve_S_leg_carriageway',
 'WS130_stall_lines_and_facade_hatch_paint':'WS130_Chapin_E_service_drive_and_stall_bay','WS135a_edge_lines_and_stall_lines_paint':'WS135a_Skyline_Way_asphalt',
 'WS138a_lot_paint_Nrow_stalls_hatch':'WS138a_Russ_S_and_BK_lot_asphalt_one_surface','SF_Lot38_stall_stripes':'SF_Lot38_asphalt_313028558'}
def find(p): 
    c=[o for o in bpy.data.objects if o.name.startswith(p) and o.type=='MESH']; return c[0] if len(c)==1 else (c and c[0])
def bcol(m):
    try: return list([n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0].inputs['Base Color'].default_value)
    except Exception: return None
OUT={}
for pp,bp in PAIRS.items():
    o=find(pp); b=find(bp)
    if not o or not b: print('D219B missing',pp,bool(o),bp,bool(b)); continue
    M=o.matrix_world
    V=[list((M@v.co)[:]) for v in o.data.vertices]
    F=[(list(p.vertices),p.material_index) for p in o.data.polygons if p.normal.z>0.5]
    mats=[(s.material.name if s.material else None,bcol(s.material) if s.material else None) for s in o.material_slots]
    bm=[s.material.name if s.material else None for s in b.material_slots]
    busers={n:[x.name[:30] for x in bpy.data.objects if x.type=='MESH' and any(s.material and s.material.name==n for s in x.material_slots)] for n in bm if n}
    chain={n:('ws213z_msep' in bpy.data.materials[n].node_tree.nodes, any(k.startswith('ws219') for k in bpy.data.materials[n].node_tree.nodes.keys())) for n in bm if n}
    OUT[o.name]={'V':V,'F':F,'mats':mats,'base':b.name,'bmats':bm,'mods':[m.type for m in o.modifiers],'bfacemat':sorted(set(p.material_index for p in b.data.polygons))}
    print('D219B',o.name[:40],'->',b.name[:40],'faces',len(F),'mats',[(a,[round(x,2) for x in c] if c else None) for a,c in mats],'bmats',bm,'busers',{k:len(v) for k,v in busers.items()},'chain',chain,'mods',[m.type for m in o.modifiers],'bmods',[m.type for m in b.modifiers],flush=True)
json.dump(OUT,open('/workspace/nj-scenes/montclair-state/scripts/ws219/paint219.json','w'))
