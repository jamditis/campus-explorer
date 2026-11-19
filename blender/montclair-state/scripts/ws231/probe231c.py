# ws231 probe c: node-group wiring of the drape / lift modifiers on Footpaths_OSM + Roads_OSM and the terrain band modifiers (no evaluation)
import bpy,sys,os
M='/workspace/nj-scenes/montclair-state/'
with bpy.data.libraries.load(M+'montclair_state.blend',link=False) as (src,dst):
    dst.objects=['Footpaths_OSM','Roads_OSM','Terrain_LiDAR_DTM_1m']
for o in dst.objects:
    for m in o.modifiers:
        if o.name=='Terrain_LiDAR_DTM_1m' and m.name not in ('QM_terrain_band_to_DTM','QM_terrain_band_to_DTM_cut','WS113_paving_edge_grade','QG_north_strip_LiDAR_patch'): continue
        ng=m.node_group; refs=[]
        for k in m.keys():
            v=m[k]; refs.append((k,getattr(v,'name',v) if not hasattr(v,'__len__') or isinstance(v,str) else 'arr'))
        print('P231C',o.name,m.name,ng.name,'refs',refs,flush=True)
        for n in ng.nodes:
            ins=[]
            for i in n.inputs:
                if not i.is_linked and hasattr(i,'default_value'):
                    dv=i.default_value
                    if hasattr(dv,'name'): ins.append((i.name,dv.name))
                    elif isinstance(dv,(int,float)) and not isinstance(dv,bool): ins.append((i.name,round(dv,3)))
            ex=getattr(n,'image',None) or getattr(n,'object',None)
            print('P231C   ',n.bl_idname,n.name,getattr(n,'operation',getattr(n,'data_type','')),ins[:5],ex.name if ex else '',flush=True)
sys.stdout.flush(); os._exit(0)
