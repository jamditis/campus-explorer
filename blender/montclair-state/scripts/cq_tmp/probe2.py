import bpy, bmesh, os, runpy, numpy as np
os.environ['SAVE']='0'
G = runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_steps_lidar_southeave_20261020cp.py', run_name='__main__')
su=G['su']
ro=bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me=ro.data
names=[x.name if x else None for x in me.materials]
bm=bmesh.new(); bm.from_mesh(me); bm.transform(ro.matrix_world); bm.faces.ensure_lookup_table()
for S in (20.0, 50.0):
  print('--- near-edge section s',S)
  for f in bm.faces:
    ss=[su(v.co) for v in f.verts]; s_=[a for a,b in ss]; u_=[b for a,b in ss]
    if min(s_)<=S<=max(s_) and min(u_)<0.5 and max(u_)>-0.9 and 135.3<max(v.co.z for v in f.verts)<136.3 and f.material_index!=24 and f.material_index not in (8,9):
      print(f.index, names[f.material_index], 'nv',len(f.verts),'s %.2f-%.2f u %.3f-%.3f z %.3f-%.3f n %.2f,%.2f,%.2f'%(min(s_),max(s_),min(u_),max(u_),min(v.co.z for v in f.verts),max(v.co.z for v in f.verts),*f.normal))
for fi in (0,36,408):
  f=bm.faces[fi]; print('FACE',fi,[('%.2f'%su(v.co)[0],'%.3f'%su(v.co)[1],'%.3f'%v.co.z, v.index) for v in f.verts])
  print(' linked faces of verts', fi, sorted({(g.index,names[g.material_index]) for v in f.verts for g in v.link_faces if g.index!=fi})[:40])
# tile strips: TILE faces belonging to 6-face boxes with all u in [-0.1,0.45]
T=24; cnt=0
for f in bm.faces:
  if f.material_index==T and len(f.verts)==4:
    uu=[su(v.co)[1] for v in f.verts]
    if min(uu)>-0.1 and max(uu)<0.45: cnt+=1
print('STRIP faces candidate', cnt)
# plane fit of face 0
P=np.array([v.co[:] for v in bm.faces[0].verts]); M=np.c_[P[:,0],P[:,1],np.ones(len(P))]; k=np.linalg.lstsq(M,P[:,2],rcond=None)[0]; print('shed plane',k,'rms',np.sqrt(np.mean((M@k-P[:,2])**2)))
P2=np.array([v.co[:] for v in bm.faces[408].verts]); print('slab verts resid vs shed plane', P2[:,2]-np.c_[P2[:,0],P2[:,1],np.ones(len(P2))]@k)
P3=np.array([v.co[:] for v in bm.faces[36].verts]); print('f36 resid', P3[:,2]-np.c_[P3[:,0],P3[:,1],np.ones(len(P3))]@k)
