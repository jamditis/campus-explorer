"""wv fix5: an overlapping second wv_fix run (two Blender processes; the first was not visible to pgrep from a
new shell) built a duplicate patch WV_..._UNVERIFIED.001 + its own skirt GN. fix2-4 edited the original.
Remove the duplicate object/mesh/collection, the skirt modifier + node group that point at it. Report."""
import bpy, json
O=bpy.data.objects; R='/workspace/nj-scenes/montclair-state'
sk=O['Context_skirt_3DEP_ortho_4km']; dup=O.get('WV_stone_west_LiDAR_patch_UNVERIFIED.001'); keep=O['WV_stone_west_LiDAR_patch_UNVERIFIED']
rep={'mods_before':[m.name for m in sk.modifiers if m.name.startswith('WV')]}
for m in list(sk.modifiers):
    if m.type=='NODES' and m.node_group and m.node_group.name.startswith('WV_'):
        tgt=[n.inputs['Object'].default_value for n in m.node_group.nodes if n.bl_idname=='GeometryNodeObjectInfo']
        rep.setdefault('mod_targets',{})[m.name]=[(m.node_group.name,t.name if t else None) for t in tgt]
        if any(t==dup for t in tgt):
            ng=m.node_group; sk.modifiers.remove(m); 
            if ng.users==0: bpy.data.node_groups.remove(ng)
cols=[c.name for c in dup.users_collection] if dup else []
if dup:
    me=dup.data; bpy.data.objects.remove(dup)
    if me.users==0: bpy.data.meshes.remove(me)
for cn in cols:
    c=bpy.data.collections.get(cn)
    if c and len(c.objects)==0 and cn!='WV_stone_west_LiDAR_UNVERIFIED': bpy.data.collections.remove(c)
rep['dup_cols']=cols
rep['keep_cols']=[c.name for c in keep.users_collection]
rep['mods_after']=[m.name for m in sk.modifiers if m.name.startswith('WV')]
rep['wv_ngs']=[n.name for n in bpy.data.node_groups if n.name.startswith('WV_')]
rep['wv_cols']=[c.name for c in bpy.data.collections if c.name.startswith('WV_')]
rep['objs']=len(O)
print('REP',json.dumps(rep),flush=True)
r=json.load(open(f'{R}/data/wv/fix_report.json')); r['fix5_dedupe']=rep; json.dump(r,open(f'{R}/data/wv/fix_report.json','w'),indent=1)
bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
