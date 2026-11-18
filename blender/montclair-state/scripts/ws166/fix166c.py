# ws166c: lower 8-13 m canopy over the Normal Ave W N-walk (ws165 research item). 2023 LiDAR class-1 heights over the class-2 ground
# (las163.npy, 1 m max grid, 5x5 local maxima): crowns at (-303.5,-250.5) 10.2 m [inside the aisle-mouth mulch bed], (-293.5,-251.5) 12.9,
# (-286.5,-253.5) 10.7, (-276.5,-255.5) 11.7 (a street-tree row ~2 m N of the walk back edge, 7-10 m spacing) and (-283.5,-246.5) 12.4 (lawn).
# Crowns ~8-9 m across in the grid. Built as linked duplicates of the WS165 red-maple tree scaled by h/18 about its trunk base
# (crown ~14*h/18 m, lowest leaves ~3.7*h/18 m); trunk = crown peak (offset up to ~1 m possible); species UNVERIFIED. Skips a spot if a tree
# object already stands within 3 m. Idempotent (removes WS166_tree_ first).
import bpy, math
from mathutils import Matrix, Vector
OB=bpy.data.objects
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/hdr166.py').read())
for o in [o for o in OB if o.name.startswith('WS166_tree_')]: OB.remove(o)
src=[o for o in OB if o.name.startswith('WS165_tree_aisle_mouth')][0]
_mw=src.matrix_world; _W=[_mw@v.co for v in src.data.vertices]; _zm=min(w.z for w in _W); _L=[w for w in _W if w.z<_zm+0.3]
B0=Vector((sum(w.x for w in _L)/len(_L),sum(w.y for w in _L)/len(_L),_zm))   # actual trunk base of the WS165 tree (not the bbox centre)
print('TREEC src trunk base',tuple(round(a,2) for a in B0),'n',len(_L),flush=True)
T=[(-303.5,-250.5,10.2,'in_aisle_bed'),(-293.5,-251.5,12.9,'NormalAve_N_row1'),(-286.5,-253.5,10.7,'NormalAve_N_row2'),(-276.5,-255.5,11.7,'NormalAve_N_row3'),(-283.5,-246.5,12.4,'lawn_N_of_row')]
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
    if near: print('TREEC skip',lab,'existing',near[:3],flush=True); continue
    s=h/18.0; b=Vector((x,y,dz(x,y)-0.12))
    M=Matrix.Translation(b)@Matrix.Rotation(0.9*k+0.4,4,'Z')@Matrix.Diagonal((s,s,s,1))@Matrix.Translation(-B0)@src.matrix_world
    t=OB.new('WS166_tree_%s_LiDAR2023_h%dm_UNVERIFIEDspecies'%(lab,round(h)),src.data); col.objects.link(t); t.matrix_world=M; made.append(t)
    for i,sl in enumerate(src.material_slots):
        if sl.link=='OBJECT': t.material_slots[i].link='OBJECT'; t.material_slots[i].material=sl.material
    print('TREEC mats',[(sl.link,sl.material.name if sl.material else None) for sl in t.material_slots],flush=True)
bpy.context.view_layer.update()
for t in made:
    bb=[t.matrix_world@Vector(c) for c in t.bound_box]
    _W2=[t.matrix_world@v.co for v in t.data.vertices]; _z2=min(w.z for w in _W2); _L2=[w for w in _W2 if w.z<_z2+0.3]
    print('TREEC trunk',round(sum(w.x for w in _L2)/len(_L2),2),round(sum(w.y for w in _L2)/len(_L2),2),'base-g',round(_z2-dz(sum(w.x for w in _L2)/len(_L2),sum(w.y for w in _L2)/len(_L2)),2),flush=True)
    print('TREEC',t.name,'x',round(min(c.x for c in bb),1),round(max(c.x for c in bb),1),'y',round(min(c.y for c in bb),1),round(max(c.y for c in bb),1),'top-g',round(max(c.z for c in bb)-dz(t.matrix_world.translation.x,t.matrix_world.translation.y),1),flush=True)
