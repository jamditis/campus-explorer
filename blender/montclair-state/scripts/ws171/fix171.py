# ws171: UNIFY #74 part 2 — yard/street trees S of Normal Ave W from the 2023 LiDAR CHM (prep/ws169_woods/peaks169.json, chm169_1m.npy).
# Peaks with crown radius >=6 m (tree crowns; the r<=3 peaks at h 13.8-15.6 lie on the wire line y=-260+(x+331.7)(-0.25) = wire returns, skipped).
# Peaks <4.6 m apart merged (one crown, two LiDAR maxima). Built as linked duplicates of the WS165 red-maple tree scaled h/18 about its trunk base
# (same method as ws166c); species UNVERIFIED (residential yard trees, likely oak/maple mix); trunk = crown peak (+-1 m).
import bpy, math
from mathutils import Matrix, Vector
OB=bpy.data.objects
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/hdr166.py').read())
for o in [o for o in OB if o.name.startswith('WS171_tree_')]: OB.remove(o)
src=[o for o in OB if o.name.startswith('WS165_tree_aisle_mouth')][0]
_mw=src.matrix_world; _W=[_mw@v.co for v in src.data.vertices]; _zm=min(w.z for w in _W); _L=[w for w in _W if w.z<_zm+0.3]
B0=Vector((sum(w.x for w in _L)/len(_L),sum(w.y for w in _L)/len(_L),_zm))
T=[(-317.0,-274.0,22.3,'S_yard_A'),(-295.5,-275.5,18.2,'S_yard_B'),(-295.5,-283.5,23.8,'S_yard_C'),(-339.5,-282.0,27.1,'S_yard_D'),
   (-331.5,-280.5,26.9,'S_yard_E'),(-318.5,-286.5,22.5,'S_yard_H'),(-333.5,-287.5,27.5,'S_yard_I'),(-341.5,-288.5,25.7,'S_yard_K')]
bpy.context.view_layer.update()
others=[]
for o in OB:
    if o.type!='MESH' or o is src: continue
    n=o.name.lower()
    if not ('tree' in n or n.startswith('t_') or 'maple' in n or 'oak' in n): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(c.z for c in bb)-min(c.z for c in bb)<4: continue
    others.append((o.name,Vector((sum(c.x for c in bb)/8,sum(c.y for c in bb)/8))))
col=src.users_collection[0]; made=[]
for k,(x,y,h,lab) in enumerate(T):
    near=[n for n,c in others if (c-Vector((x,y))).length<3.0]
    if near: print('TREE171 skip',lab,near[:3],flush=True); continue
    s=h/18.0; b=Vector((x,y,dz(x,y)-0.15))
    M=Matrix.Translation(b)@Matrix.Rotation(1.3*k+0.7,4,'Z')@Matrix.Diagonal((s,s,s,1))@Matrix.Translation(-B0)@src.matrix_world
    t=OB.new('WS171_tree_%s_LiDAR2023_h%dm_UNVERIFIEDspecies'%(lab,round(h)),src.data); col.objects.link(t); t.matrix_world=M; made.append(t)
    for i,sl in enumerate(src.material_slots):
        if sl.link=='OBJECT': t.material_slots[i].link='OBJECT'; t.material_slots[i].material=sl.material
bpy.context.view_layer.update()
for t in made:
    bb=[t.matrix_world@Vector(c) for c in t.bound_box]
    cx=(min(c.x for c in bb)+max(c.x for c in bb))/2
    ywire=-260+(cx+331.7)*(-0.25)
    print('TREE171',t.name,'x',round(min(c.x for c in bb),1),round(max(c.x for c in bb),1),'y',round(min(c.y for c in bb),1),round(max(c.y for c in bb),1),
          'crownN-wire',round(max(c.y for c in bb)-ywire,1),flush=True)
print('TREE171 made',len(made),flush=True)
