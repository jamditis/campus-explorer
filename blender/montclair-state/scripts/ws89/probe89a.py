import bpy,math
from mathutils import Vector
want=['COLE_plaza_edge_bs','COLE_plaza_deck_bs','WS35_Kasser_terrace_steps_concrete_5risers_UNVERIFIED','WS35_Kasser_steps_cheek_walls_UNVERIFIED','WS35_Cole_steps_handrails_MAROON_JOEphoto20261112','WS40_Cole_deck_cut_fascia_concrete_UNVERIFIED','WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020']
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (s,d):
    d.objects=[n for n in s.objects if n in want or n.startswith('Plaza long arched wall')]
C=Vector((-166.66,-79.9))
for o in d.objects:
    if not o: continue
    bpy.context.scene.collection.objects.link(o)
    P=[o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else []
    if not P: print('P89',o.name,o.type); continue
    xs=[p.x for p in P];ys=[p.y for p in P];zs=[p.z for p in P]
    rs=[(p.xy-C).length for p in P]
    print('P89',o.name[:50],'v',len(P),'f',len(o.data.polygons),'x',round(min(xs),2),round(max(xs),2),'y',round(min(ys),2),round(max(ys),2),'z',round(min(zs),2),round(max(zs),2),'r',round(min(rs),2),round(max(rs),2),'mods',[m.type+':'+m.name for m in o.modifiers],'mats',[m.name for m in o.data.materials if m][:4],'parent',o.parent.name if o.parent else None)
