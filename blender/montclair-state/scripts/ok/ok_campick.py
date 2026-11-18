import bpy, math
from mathutils import Vector, Matrix
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mi=t.matrix_world.inverted()
def gz(p):
    h,l,n,i=t.ray_cast(mi@Vector((p.x,p.y,400)),mi.to_3x3()@Vector((0,0,-1))); return (t.matrix_world@l).z if h else 138
ws=[o for o in bpy.data.objects if o.name.startswith('SCH_win_') and o.get('run')=='(-0.92, 0.4, 77)' and o.get('row')==1]
ctr=sum((o.matrix_world.translation for o in ws),Vector())/len(ws)
M=ws[0].matrix_world; X=(M.to_3x3()@Vector((1,0,0))).normalized(); Y=(M.to_3x3()@Vector((0,1,0))).normalized()
res=[]
for D in (6,8,10,12,14,18,22):
  for S in (-30,-24,-18,-12,-6,0,6,12,18):
    for T in (-6,0,6):
      q=ctr+Y*D+X*S; q.z=gz(q)+1.65; tg=ctr+X*T+Vector((0,0,0.5)); f=(tg-q).normalized()
      bl=0; nn=0
      for a in range(-30,31,6):
        for e in (-10,0,10):
          d=Matrix.Rotation(math.radians(a),3,'Z')@f; d=(d+Vector((0,0,math.radians(e)))).normalized()
          h,l,_,_,ob,_=sc.ray_cast(dg,q,d,distance=60); nn+=1
          if h and ob and (ob.name.startswith('T_') or (l-q).length<4): bl+=1
      res.append((bl/nn,D,S,T))
res.sort()
for r in res[:8]: print('PICK',r)
