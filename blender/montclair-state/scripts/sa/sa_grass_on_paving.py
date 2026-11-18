# sa: cull MAIN grass points standing on visible QXP footway/paving faces inside the sa box (x -110..30, y 252..310). UNVERIFIED. REVERT=1 re-adds them (data/sa/grass_paving_removed.npz).
import bpy, os, numpy as np
REV=os.environ.get('REVERT')=='1'; Z='data/sa/grass_paving_removed.npz'
G=[o for o in bpy.data.objects if o.type=='MESH' and 'grass' in o.name.lower() and ('point' in o.name.lower() or 'clump' in o.name.lower()) and not o.library and len(o.data.polygons)==0]
if REV:
    z=np.load(Z,allow_pickle=True)
    for n in z.files:
        o=bpy.data.objects.get(n); a=z[n]
        if o is None or len(a)==0: continue
        me=o.data;k=len(me.vertices);me.vertices.add(len(a))
        for i,c in enumerate(a): me.vertices[k+i].co=c
        me.update()
    print('SAG reverted',{n:len(z[n]) for n in z.files})
else:
    R=0.5; x0,y0,nx,ny=-110,252,280,116; M=np.zeros((ny,nx),bool)
    P=[o for o in bpy.data.objects if o.type=='MESH' and not o.library and o.visible_get()==False or False]
    P=[o for o in bpy.data.objects if o.type=='MESH' and not o.library and not o.hide_render and o.name.startswith('QXP_') and ('footway' in o.name or 'paving' in o.name or 'pedestrian' in o.name) and len(o.data.polygons)]
    for o in P:
        mw=o.matrix_world
        for p in o.data.polygons:
            vs=np.array([tuple(mw@o.data.vertices[i].co) for i in p.vertices])
            if vs[:,0].max()<x0 or vs[:,0].min()>x0+nx*R or vs[:,1].max()<y0 or vs[:,1].min()>y0+ny*R: continue
            # sample polygon by fan triangles
            for t in range(1,len(vs)-1):
                A,B,C=vs[0],vs[t],vs[t+1]
                for u in np.linspace(0,1,9):
                    for v in np.linspace(0,1-u,max(2,int(9*(1-u)))):
                        q=A+u*(B-A)+v*(C-A); i=int((q[1]-y0)/R); j=int((q[0]-x0)/R)
                        if 0<=i<ny and 0<=j<nx: M[i,j]=True
    out={}
    import bmesh
    for o in G:
        me=o.data; n=len(me.vertices)
        if n==0: continue
        co=np.zeros(n*3,np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
        w=np.array(o.matrix_world); wc=co@w[:3,:3].T+w[:3,3]
        i=((wc[:,1]-y0)/R).astype(int); j=((wc[:,0]-x0)/R).astype(int); ok=(i>=0)&(i<ny)&(j>=0)&(j<nx)
        kill=np.zeros(n,bool); kill[ok]=M[i[ok],j[ok]]
        if kill.sum()==0: continue
        out[o.name]=co[kill]
        bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm,geom=[bm.verts[k] for k in np.nonzero(kill)[0]],context='VERTS'); bm.to_mesh(me); bm.free()
    np.savez(Z,**out); print('SAG paving objs',len(P),'cells',int(M.sum()),'culled',{k:len(v) for k,v in out.items()})
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
