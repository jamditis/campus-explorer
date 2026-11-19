# ws234 read-only probe of north/montclair_north.blend: visibility of the M2b station/rail batch candidates
import bpy, json
MS='/workspace/nj-scenes/montclair-state/'
man=json.load(open(MS+'scripts/ws217/north_manifest217.json'))
C={'North_station_platform','North_railway_MontclairLine','NJT_consist_A_stopped','NJT_consist_B_moving','NJT_ALP46_loco','NJT_Comet_cab','NJT_Comet_trailer','North_MontclairHeights_20261014'}
cand=[n for n,v in man.items() if v[0] in('APPEND','NONMESH_EMPTY','NONMESH_FONT','NONMESH_CURVE') and C&set(v[4] if len(v)>4 else [])]
vl=bpy.context.view_layer
def lc_excluded(lc,name,path=()):
    out={}
    for c in lc.children:
        out[c.name]=(c.exclude or c.collection.hide_render or c.hide_viewport) or any(path)
        out.update(lc_excluded(c,name,path+((c.exclude or c.collection.hide_render),)))
    return out
EXC=lc_excluded(vl.layer_collection,None)
res={}
for n in cand:
    o=bpy.data.objects.get(n)
    if not o: res[n]='MISSING'; continue
    cols=[c.name for c in o.users_collection]
    vis=(not o.hide_render) and any(not EXC.get(c,False) for c in cols)
    res[n]=dict(vis=vis,hr=o.hide_render,hv=o.hide_viewport,cols=cols,lib=o.library.filepath if o.library else None,
               parent=o.parent.name if o.parent else None,inst=o.instance_collection.name if o.instance_collection else None,
               instlib=(o.instance_collection.library.filepath if o.instance_collection and o.instance_collection.library else None),
               mods=[m.type for m in o.modifiers])
json.dump(res,open(MS+'scripts/ws234/m2b_vis234.json','w'),indent=0)
import collections
print('P234 cand',len(cand),'vis',sum(1 for v in res.values() if isinstance(v,dict) and v['vis']),'hidden',[n[:40] for n,v in res.items() if isinstance(v,dict) and not v['vis']])
print('P234 libs',collections.Counter(v['lib'] for v in res.values() if isinstance(v,dict)))
print('P234 inst',collections.Counter((v['inst'],v['instlib']) for v in res.values() if isinstance(v,dict) and v['inst']))
print('P234 mods',collections.Counter(m for v in res.values() if isinstance(v,dict) for m in v['mods']))
# terrain heights in north under rail/station: sample North_terrain_LiDAR_1m
for t in ('North_terrain_LiDAR_1m','North_skirt_lowdetail_4m','MH_terrain_LiDAR_1m'):
    o=bpy.data.objects.get(t)
    if o:
        import mathutils
        bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
        print('P234 terr',t,[round(min(v[i] for v in bb),1) for i in range(3)],[round(max(v[i] for v in bb),1) for i in range(3)],len(o.data.vertices) if o.type=='MESH' else 0)
