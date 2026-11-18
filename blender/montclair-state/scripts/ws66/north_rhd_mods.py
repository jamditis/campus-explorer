import bpy
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
skip={'North_Kasser_linked_ce','North_replaced_rhd_20261013'}
with bpy.data.libraries.load(src) as (fr,to): cols=[c for c in fr.collections if c not in skip and ('RHD' in c or 'RedHawk' in c or 'rhd' in c or c in ('North_parking_decks','North_Kasser_joint_cf','North_DeckBaseStrip_fu','North_DeckNEWalkLawn_gk','North_DeckNELawn_gj','North_DeckNEBermLawn_gl','ge_grass_deckbase_clumps'))]
with bpy.data.libraries.load(src,link=False) as (fr,to): to.collections=cols
seen=set()
for c in to.collections:
    for o in c.all_objects:
        if o.name in seen: continue
        seen.add(o.name)
        bb=[o.matrix_world@Vector(v) for v in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]
        inreg=min(xs)<-228 and max(xs)>-350 and min(ys)<45 and max(ys)>-65
        mods=[(m.type,[ (i.identifier, getattr(m.get(i.identifier),'name',None)) for i in (m.node_group.interface.items_tree if m.type=='NODES' and m.node_group else []) if i.item_type=='SOCKET' and i.in_out=='INPUT' and getattr(m.get(i.identifier),'name',None)] if m.type=='NODES' else getattr(getattr(m,'object',None),'name',None)) for m in o.modifiers]
        print('NM',c.name[:22],'|',o.name[:55],'|',o.type,'hr',o.hide_render,'reg',inreg,round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),'|',mods)
print('NM objs in data',len(bpy.data.objects),[ob.name[:40] for ob in bpy.data.objects if ob.name not in seen][:30])
