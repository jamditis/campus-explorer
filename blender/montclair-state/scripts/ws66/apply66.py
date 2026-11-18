# ws66: bring the Red Hawk Deck (north-file model, same world coords) into MAIN as collection WS66_RedHawkDeck_from_north.
# REVERT=1: delete that collection + its objects.
import bpy,os,hashlib
from mathutils import Vector
CN='WS66_RedHawkDeck_from_north'
if os.environ.get('REVERT'):
    c=bpy.data.collections.get(CN)
    if c:
        obs=list(c.all_objects); bpy.data.batch_remove(obs); bpy.data.collections.remove(c); bpy.data.orphans_purge(do_recursive=True)
    bpy.ops.wm.save_mainfile(); print('A66 reverted'); raise SystemExit
src='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
skipc={'North_Kasser_linked_ce','North_replaced_rhd_20261013','KX2_rhd_walk','North_DeckNEWalkLawn_gk','North_DeckNELawn_gj','North_DeckNEBermLawn_gl','North_RHD_fb'}
have=set(bpy.data.objects.keys())
with bpy.data.libraries.load(src) as (fr,to): cols=[c for c in fr.collections if c not in skipc and ('RHD' in c or 'RedHawk' in c or 'rhd' in c or c in ('North_parking_decks','North_Kasser_joint_cf','North_DeckBaseStrip_fu'))]
with bpy.data.libraries.load(src,link=False) as (fr,to): to.collections=cols
keep=[];drop=set()
for c in to.collections:
    for o in c.all_objects:
        if o in keep or o.name in drop: continue
        bb=[o.matrix_world@Vector(v) for v in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]
        inreg=min(xs)<-228 and max(xs)>-350 and min(ys)<45 and max(ys)>-65 and max(xs)-min(xs)<200
        base=o.name.rsplit('.',1)[0] if o.name[-4:-3]=='.' and o.name[-3:].isdigit() else o.name
        ok=o.type=='MESH' and not o.hide_render and inreg and base not in have and not any(m.type=='NODES' and 'grass' in o.name.lower() for m in o.modifiers)
        (keep.append(o) if ok else drop.add(o.name))
dst=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(dst)
for o in keep: dst.objects.link(o)
# remove the appended north collections themselves (objects now live in dst) and anything not kept
dropobs=[o for c in to.collections for o in c.all_objects if o not in keep]
for c in list(to.collections): bpy.data.collections.remove(c)
bpy.data.batch_remove(list(set(dropobs))); bpy.data.orphans_purge(do_recursive=True)
nf=sum(len(o.data.polygons) for o in keep)
print('A66 kept',len(keep),'faces',nf); [print('A66K',o.name[:70]) for o in keep]
if os.environ.get('SAVE'): bpy.ops.wm.save_mainfile(); print('A66 saved')
