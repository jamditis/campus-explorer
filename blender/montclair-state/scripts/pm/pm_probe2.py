import bpy, numpy as np
for o in bpy.data.objects:
    if 'eliciano' in o.name and o.type=='MESH':
        m=o.data; n=len(m.vertices); co=np.zeros(n*3); m.vertices.foreach_get('co',co); co=co.reshape(-1,3)
        mw=np.array(o.matrix_world); co=co@mw[:3,:3].T+mw[:3,3]
        print(repr(o.name), n, len(m.polygons), 'z', round(co[:,2].min(),2), round(co[:,2].max(),2), 'hide', o.hide_render, [md.name for md in o.modifiers][:4])
w=bpy.data.objects.get('Feliciano School of Business walls')
if w:
    m=w.data; n=len(m.vertices); co=np.zeros(n*3); m.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    zs=np.round(co[:,2],1); u,c=np.unique(zs,return_counts=True); print('wall z levels', [(a,b) for a,b in zip(u,c) if b>3][:40])
