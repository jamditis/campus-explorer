"""Deeper wall/addition survey for tz — normal convention vs tw."""
import bpy, json
from mathutils import Vector
D='/workspace/nj-scenes/montclair-state/'
out=[]
w=bpy.data.objects.get('Susan A. Cole Hall walls')
me=w.data
names=[m.name if m else '' for m in me.materials]
# Compare flipped vs unflipped like tw
for flip in (False, True):
    cream={'S':0,'N':0,'E':0,'W':0,'other':0}
    mission={'S':0,'N':0,'E':0,'W':0,'other':0}
    plain={'S':0,'N':0,'E':0,'W':0,'other':0}
    for poly in me.polygons:
        n=(w.matrix_world.to_3x3()@poly.normal).normalized()
        if flip: n=-n
        cw=w.matrix_world@poly.center
        if abs(n.z)>0.55: continue
        if n.y<-0.55: face='S'
        elif n.y>0.55: face='N'
        elif n.x>0.55: face='E'
        elif n.x<-0.55: face='W'
        else: face='other'
        mn=names[poly.material_index] if poly.material_index<len(names) else '?'
        bucket=cream if 'cream' in mn.lower() else (plain if 'plain' in mn.lower() or 'bq' in mn.lower() else mission)
        # refine
        if 'cream' in mn.lower(): cream[face]+=1
        elif 'plain' in mn.lower() or mn.startswith('COLE_stucco'): plain[face]+=1
        else: mission[face]+=1
    out.append(f"flip={flip} cream={cream} mission={mission} plain={plain}")

# East edge lengths from ring
ring=json.load(open(D+'north/data/day_heroes/day9_cole_hall_levels_prep_20261016be.json'))['footprint']['ring_scene_xy_m']
P=[Vector((x,y)) for x,y in ring]
if P[0]==P[-1]: P=P[:-1]
area=sum(P[i].x*P[(i+1)%len(P)].y-P[(i+1)%len(P)].x*P[i].y for i in range(len(P)))/2
out.append(f"ring n={len(P)} area_sign={area}")
for i in range(len(P)):
    a,b=P[i],P[(i+1)%len(P)]; d=b-a; L=d.length
    if L<3: continue
    t=d/L
    n=Vector((t.y,-t.x)) if area>0 else Vector((-t.y,t.x))
    mid=(a+b)/2
    tag=''
    if n.y<-0.55: tag='SOUTH'
    elif n.y>0.55: tag='NORTH'
    elif n.x>0.55: tag='EAST'
    elif n.x<-0.55: tag='WEST'
    else: tag='diag'
    out.append(f"EDGE {i} L={L:.2f} mid=({mid.x:.1f},{mid.y:.1f}) n=({n.x:.2f},{n.y:.2f}) {tag}")

# addition detail: face normals + z bands
add=None
for o in bpy.data.objects:
    if 'north addition' in o.name.lower():
        add=o; break
out.append(f"ADD={add.name}")
# classify addition faces
bands={'wall_E':0,'wall_W':0,'wall_N':0,'wall_S':0,'roof':0,'other':0}
for poly in add.data.polygons:
    n=(add.matrix_world.to_3x3()@poly.normal).normalized()
    if n.z>0.7: bands['roof']+=1
    elif n.x>0.5: bands['wall_E']+=1
    elif n.x<-0.5: bands['wall_W']+=1
    elif n.y>0.5: bands['wall_N']+=1
    elif n.y<-0.5: bands['wall_S']+=1
    else: bands['other']+=1
out.append(f"ADD face bands {bands}")
# eave/ridge from verts
zs=sorted((add.matrix_world@v.co).z for v in add.data.vertices)
out.append(f"ADD z p10/p50/p90/max {zs[len(zs)//10]:.2f}/{zs[len(zs)//2]:.2f}/{zs[9*len(zs)//10]:.2f}/{zs[-1]:.2f}")
# xy of high verts (ridge)
ridge=[add.matrix_world@v.co for v in add.data.vertices if (add.matrix_world@v.co).z>148.5]
if ridge:
    out.append(f"ADD ridge n={len(ridge)} x[{min(p.x for p in ridge):.2f},{max(p.x for p in ridge):.2f}] y[{min(p.y for p in ridge):.2f},{max(p.y for p in ridge):.2f}] z[{min(p.z for p in ridge):.2f},{max(p.z for p in ridge):.2f}]")
eave=[add.matrix_world@v.co for v in add.data.vertices if 142.5<(add.matrix_world@v.co).z<144.0]
if eave:
    out.append(f"ADD eave-ish n={len(eave)} z[{min(p.z for p in eave):.2f},{max(p.z for p in eave):.2f}]")

# identity rect
ident=json.load(open(D+'north/data/day_heroes/day9_cole_hall_identity_20261016bq.json'))
out.append(f"ident north_addition_rect={ident['lidar_MEASURED']['north_addition_rect']}")
out.append(f"ident eave_ridge={ident['lidar_MEASURED']['north_addition_eave_ridge']}")

# TW windows bbox to see coverage
tw=bpy.data.objects.get('TW_Cole_windows_SW_UNVERIFIED')
if tw:
    bb=[tw.matrix_world@Vector(c) for c in tw.bound_box]
    out.append(f"TW wins bbox x[{min(p.x for p in bb):.1f},{max(p.x for p in bb):.1f}] y[{min(p.y for p in bb):.1f},{max(p.y for p in bb):.1f}]")

path='/workspace/nj-scenes/montclair-state/data/tz/survey2.txt'
open(path,'w').write('\n'.join(out)+'\n')
print('\n'.join(out))
