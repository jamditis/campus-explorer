import bpy,json
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
with bpy.data.libraries.load(src) as (fr,to): cols=[c for c in fr.collections if ('RHD' in c or 'RedHawk' in c or 'rhd' in c or c in ('North_parking_decks','North_Kasser_linked_ce','North_Kasser_joint_cf','North_DeckBaseStrip_fu','North_DeckNEWalkLawn_gk','North_DeckNELawn_gj','North_DeckNEBermLawn_gl','ge_grass_deckbase_clumps'))]
with bpy.data.libraries.load(src,link=False) as (fr,to): to.collections=cols
out={}
for c in to.collections:
    rows=[]
    for o in c.all_objects:
        bb=[o.matrix_world@Vector(v) for v in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
        nf=len(o.data.polygons) if o.type=='MESH' else 0
        rows.append((o.name,o.type,nf,round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),round(min(zs),1),round(max(zs),1),bool(o.library or (o.data and o.data.library)),len(o.modifiers)))
    out[c.name]=rows
    print('NC',c.name,len(rows),sum(r[2] for r in rows), 'lib',sum(r[9] for r in rows))
json.dump(out,open('data/ws66_north_rhd_cols.json','w'))
