# crop big ground meshes to CULL box (+pad) on mesh data before modifier eval (lite only; never saved)
import bpy,bmesh,os
X0,X1,Y0,Y1=map(float,os.environ['CULL'].split(',')); P=float(os.environ.get('CROPPAD','15'))
for o in list(bpy.data.objects):
    if o.type!='MESH' or len(o.data.vertices)<20000: continue
    bm=bmesh.new(); bm.from_mesh(o.data); mw=o.matrix_world
    dv=[v for v in bm.verts if not (X0-P<(mw@v.co).x<X1+P and Y0-P<(mw@v.co).y<Y1+P)]
    n0=len(bm.verts); bmesh.ops.delete(bm,geom=dv,context='VERTS'); bm.to_mesh(o.data); bm.free()
    print('LR crop',o.name,n0,'->',len(o.data.vertices),flush=True)
bpy.data.orphans_purge(do_recursive=True)
