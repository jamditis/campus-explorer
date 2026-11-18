# on: delete 3 stray og-boolean faces (jamb triangles + head) that stick 0.6 m OUT of the Schmitt facade at SCH_win_104_r2 (white shard in the OH view). REVERT=1 restores the original mesh.
import bpy, bmesh, os, sys
from mathutils import Vector
w=bpy.data.objects['Schmitt Hall walls']; KEY='Schmitt walls (pre-on shard fix)'
if os.environ.get('REVERT')=='1':
    o=bpy.data.meshes.get(KEY)
    if o:
        cur=w.data; w.data=o; o.use_fake_user=False; bpy.data.meshes.remove(cur); o.name='Schmitt Hall walls'
    print('ON_REVERTED')
else:
    if bpy.data.meshes.get(KEY): print('already applied'); sys.exit(0)
    orig=w.data.copy(); orig.name=KEY; orig.use_fake_user=True
    M=w.matrix_world
    C=Vector((-15.67,117.09)); A=Vector((0.396,0.918)).normalized(); N=Vector((-0.918,0.396)).normalized()
    bm=bmesh.new(); bm.from_mesh(w.data); kill=[]
    for f in bm.faces:
        ok=True; outside=False
        for v in f.verts:
            p=M@v.co; q=Vector((p.x,p.y))-C; a=q.dot(A); n=q.dot(N)
            if not (-0.81<=a<=0.81 and -0.61<=n<=0.01 and 146.27<=p.z<=148.09): ok=False; break
            if n<-0.3: outside=True
        if ok and outside: kill.append(f)
    print('KILL',len(kill),[round(f.calc_area(),3) for f in kill])
    bmesh.ops.delete(bm,geom=kill,context='FACES_ONLY'); bm.to_mesh(w.data); bm.free()
    print('faces',len(w.data.polygons))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
