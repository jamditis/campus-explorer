import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PF=('WS98_lotE_entry_aisle','WS98_lotE_raised_concrete','WS27_CollegeAve_carriageway','WS27_CollegeAve_curb_right','Terrain_LiDAR_DTM_1m','WS99_lotE_padS_bed','WS98_CollegeAve_bend_teardrop','Footpaths_OSM')
with bpy.data.libraries.load(M) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PF)]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
out={}
for o in b.objects:
    me=o.data; mw=o.matrix_world
    vs=[mw@v.co for v in me.vertices]
    sel=[v for v in vs if -218<v.x<-196 and -96<v.y<-74]
    out[o.name]={'nv':len(me.vertices),'nf':len(me.polygons),'mods':[m.type for m in o.modifiers],'mat':[m.name for m in me.materials if m],'nsel':len(sel)}
    if o.name.startswith(('WS98_lotE_entry','Terrain','WS98_lotE_raised','WS27_CollegeAve_curb_right')):
        out[o.name]['pts']=[(round(v.x,2),round(v.y,2),round(v.z,3)) for v in sel][:4000]
json.dump(out,open('probe205.json','w'))
for k,v in out.items(): print('P205',k,v['nv'],v['nf'],v['mods'],v['mat'],v['nsel'])
