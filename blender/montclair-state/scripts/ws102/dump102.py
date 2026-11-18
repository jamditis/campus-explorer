import bpy, numpy as np, json
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_carriageway_2020ortho',
'UA_CollegeAve_spur_1557427669_UNVERIFIED','Footpaths_OSM','Roads_OSM','WS35_CollegeAve_bed_posts_black_PHOTO_JOE_20261110','WS35_CollegeAve_bed_chain_black_PHOTO_JOE_20261110']
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in s.objects if n in names or n.startswith(('UA_','WS73_','WS40_','WS82','WS83'))]
out={};info={}
for o in d.objects:
    if o.type!='MESH': continue
    me=o.data; n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); W=co@M[:3,:3].T+M[:3,3]
    m=(W[:,0]>-270)&(W[:,0]<-150)&(W[:,1]>-290)&(W[:,1]<-140)
    if not m.any(): continue
    fs=[]
    for pl in me.polygons:
        v=list(pl.vertices)
        if m[v].any(): fs.append(W[v].tolist())
    out[o.name]=fs; info[o.name]=dict(n=n,inreg=int(m.sum()),mods=[mm.type for mm in o.modifiers],mats=[s.material.name if s.material else None for s in o.material_slots],users=me.users)
    print('D102',o.name[:70],info[o.name])
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws102/dump102.json','w'));json.dump(info,open('/workspace/nj-scenes/montclair-state/scripts/ws102/info102.json','w'),indent=1)
