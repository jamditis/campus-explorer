import bpy, numpy as np, math
OB=bpy.data.objects
for o in OB:
    if o.type!='MESH' or o.name.startswith('WS162_'): continue
    me=o.data; n=len(me.vertices)
    if n==0: continue
    mw=np.array(o.matrix_world); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); W=co@mw[:3,:3].T+mw[:3,3]
    m=(W[:,0]>-309)&(W[:,0]<-285)&(W[:,1]>-238)&(W[:,1]<-170)
    if m.sum()==0: continue
    print('INSP',o.name[:55],o.hide_viewport,o.hide_render,m.sum(),'z',round(float(W[m,2].min()),2),round(float(W[m,2].max()),2),'of',n,'mods',[x.type for x in o.modifiers][:4])
