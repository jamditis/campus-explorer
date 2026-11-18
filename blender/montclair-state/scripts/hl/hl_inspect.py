import bpy, numpy as np, json
P=np.array(json.load(open('/workspace/nj-scenes/montclair-state/north/data/day_heroes/ct/amphi_locate_ct.json'))['osm']['232850516']['pts'])
def inside(x,y):
    c=np.zeros(len(x),bool); n=len(P)
    for i in range(n-1):
        x1,y1=P[i];x2,y2=P[i+1]
        m=((y1>y)!=(y2>y)); xi=x1+(y-y1)*(x2-x1)/(y2-y1+1e-12)
        c^=m&(x<xi)
    return c
for o in bpy.context.scene.objects:
    if o.type!='MESH': continue
    bb=np.array([o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box])
    if bb[:,0].max()<-201 or bb[:,0].min()>-152 or bb[:,1].max()<-9.5 or bb[:,1].min()>36: continue
    me=o.data; n=len(me.vertices)
    if n>3_000_000: print('BIG',o.name,n); continue
    co=np.empty(n*3,np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); w=co@M[:3,:3].T+M[:3,3]
    k=inside(w[:,0],w[:,1])
    if k.sum()==0: continue
    print('OBJ',repr(o.name),'verts_in',int(k.sum()),'of',n,'z %.2f..%.2f'%(w[k,2].min(),w[k,2].max()),'hide',o.hide_render,'coll',[c.name for c in o.users_collection][:2], 'mods',[m.type for m in o.modifiers][:3])
