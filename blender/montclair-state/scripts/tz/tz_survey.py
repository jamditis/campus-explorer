"""Survey Cole/College Hall E/N + north addition for session tz."""
import bpy
from mathutils import Vector
out=[]
keys=('cole','college','cupola','bell','bq','br','bu','susan','tw_cole','tz_')
for o in sorted(bpy.data.objects, key=lambda x:x.name):
    n=o.name.lower()
    if any(k in n for k in keys) or o.get('tw_obj') or o.get('tz_obj'):
        cols=[c.name for c in o.users_collection]
        mats=[s.material.name if s.material else '' for s in o.material_slots]
        bb=[o.matrix_world@Vector(c) for c in o.bound_box] if o.type=='MESH' else []
        if bb:
            lo=(min(p.x for p in bb),min(p.y for p in bb),min(p.z for p in bb))
            hi=(max(p.x for p in bb),max(p.y for p in bb),max(p.z for p in bb))
            dx,dy,dz=hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]
        else:
            lo=hi=None; dx=dy=dz=0
        out.append(f"OBJ {o.name!r} type={o.type} hide={o.hide_get()}/{o.hide_render} cols={cols} mats={mats[:8]} bbox={lo}->{hi} size=({dx:.2f},{dy:.2f},{dz:.2f}) loc={tuple(round(x,3) for x in o.location)}")

w=bpy.data.objects.get('Susan A. Cole Hall walls')
if w:
    me=w.data
    names=[m.name if m else '' for m in me.materials]
    out.append(f"WALLS mats={names}")
    buckets={'S':0,'N':0,'E':0,'W':0,'up':0,'dn':0,'other':0}
    cream={'S':0,'N':0,'E':0,'W':0}
    cream_si=None
    for i,n in enumerate(names):
        if n and ('cream' in n.lower() or n=='TW_Cole_stucco_cream_UNVERIFIED'):
            cream_si=i
    mat_counts={}
    for poly in me.polygons:
        nw=(w.matrix_world.to_3x3()@poly.normal).normalized()
        cw=w.matrix_world@poly.center
        mi=poly.material_index
        mn=names[mi] if mi<len(names) else '?'
        mat_counts[mn]=mat_counts.get(mn,0)+1
        if abs(nw.z)>0.55:
            buckets['up' if nw.z>0 else 'dn']+=1; continue
        face=None
        if nw.y<-0.55: face='S'
        elif nw.y>0.55: face='N'
        elif nw.x>0.55: face='E'
        elif nw.x<-0.55: face='W'
        else: buckets['other']+=1; continue
        buckets[face]+=1
        if cream_si is not None and mi==cream_si:
            cream[face]+=1
    out.append(f"WALL face counts {buckets}")
    out.append(f"WALL cream faces by dir {cream} cream_si={cream_si}")
    out.append(f"WALL mat_counts {mat_counts}")
    for want,label in ((('N',), 'north'), (('E',), 'east')):
        samples=[]
        for poly in me.polygons:
            nw=(w.matrix_world.to_3x3()@poly.normal).normalized()
            cw=w.matrix_world@poly.center
            if abs(nw.z)>0.55: continue
            if 'N' in want and nw.y>0.55:
                samples.append((round(cw.x,2),round(cw.y,2),round(cw.z,2),round(nw.x,2),round(nw.y,2),poly.material_index))
            if 'E' in want and nw.x>0.55:
                samples.append((round(cw.x,2),round(cw.y,2),round(cw.z,2),round(nw.x,2),round(nw.y,2),poly.material_index))
        out.append(f"SAMPLE {label} faces n={len(samples)} first12={samples[:12]}")

add=None
for o in bpy.data.objects:
    if 'north addition' in o.name.lower() or '2020 north' in o.name.lower():
        add=o; break
if add:
    out.append(f"ADDITION name={add.name!r}")
    bb=[add.matrix_world@Vector(c) for c in add.bound_box]
    lo=(min(p.x for p in bb),min(p.y for p in bb),min(p.z for p in bb))
    hi=(max(p.x for p in bb),max(p.y for p in bb),max(p.z for p in bb))
    out.append(f"ADDITION bbox {lo}->{hi}")
    out.append(f"ADDITION verts={len(add.data.vertices)} mats={[s.material.name if s.material else '' for s in add.material_slots]}")
    zs=[(add.matrix_world@v.co).z for v in add.data.vertices]
    out.append(f"ADDITION z min/max/mean {min(zs):.3f}/{max(zs):.3f}/{sum(zs)/len(zs):.3f}")
    # corners xy
    xys=sorted(set((round((add.matrix_world@v.co).x,2), round((add.matrix_world@v.co).y,2)) for v in add.data.vertices))
    out.append(f"ADDITION unique xy corners sample {xys[:20]} n={len(xys)}")

for c in sorted(bpy.data.collections, key=lambda x:x.name):
    if any(k in c.name.lower() for k in keys+('tw_cole','tz_')):
        out.append(f"COL {c.name!r} nobj={len(c.objects)}")

for o in bpy.data.objects:
    if o.type!='CAMERA': continue
    if any(k in o.name.lower() for k in ('cole','college','tw_cam','tz_cam')):
        out.append(f"CAM {o.name} loc={tuple(round(x,2) for x in o.matrix_world.translation)}")

print('NOBJ',len(bpy.data.objects))
path='/workspace/nj-scenes/montclair-state/data/tz/survey.txt'
open(path,'w').write('\n'.join(out)+'\n')
print('WROTE',path,'lines',len(out))
for line in out: print(line)
