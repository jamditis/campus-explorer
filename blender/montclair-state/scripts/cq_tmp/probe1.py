import bpy, bmesh, os, runpy, numpy as np
os.environ['SAVE']='0'
G = runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_steps_lidar_southeave_20261020cp.py', run_name='__main__')
A=G['A']; d=G['d']; n=G['n']; su=G['su']
ro=bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me=ro.data
names=[x.name if x else None for x in me.materials]
#print('MATS', list(enumerate(names)))
print('ATTRS', [(a.name,a.domain,a.data_type) for a in me.attributes])
UW=G['UW']; print('UW',UW)
bm=bmesh.new(); bm.from_mesh(me); bm.transform(ro.matrix_world)
for S in (5.0, 20.0, 40.0, 52.0):
  print('--- section s',S)
  for f in bm.faces:
    ss=[su(v.co) for v in f.verts]; s_=[a for a,b in ss]; u_=[b for a,b in ss]
    if min(s_)<=S<=max(s_) and min(u_)<3.6 and max(u_)>-1.6 and max(v.co.z for v in f.verts)>134.5 and f.material_index in (0,1,2,4,5,24,8,9):
      print(f.index, names[f.material_index], 'nv',len(f.verts),'s %.2f-%.2f u %.3f-%.3f z %.3f-%.3f n %.2f,%.2f,%.2f'%(min(s_),max(s_),min(u_),max(u_),min(v.co.z for v in f.verts),max(v.co.z for v in f.verts),*f.normal))
