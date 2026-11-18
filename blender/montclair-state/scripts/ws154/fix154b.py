# ws154b: thinner fascia read (2019 photo band ~0.6 m): outer-edge bottom verts of the roof ring up to 146.55 (soffit slopes up outward)
import bpy, os, resource
o=[x for x in bpy.data.objects if x.name.startswith('WS154_Freeman_roof_overhang_1m_soffit')][0]
me=o.data; zs=sorted(set(round(v.co.z,3) for v in me.vertices)); print('FIX154B ring z levels',zs)
import mathutils
cx=sum(v.co.x for v in me.vertices)/len(me.vertices); cy=sum(v.co.y for v in me.vertices)/len(me.vertices)
d=[((v.co.x-cx)**2+(v.co.y-cy)**2)**0.5 for v in me.vertices]; dmax=max(d); n=0
for v,dd in zip(me.vertices,d):
    if abs(v.co.z-146.2)<0.01 and dd>dmax-0.5: v.co.z=146.55; n+=1
me.update(); print('FIX154B raised outer soffit verts',n)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state_ws154b.blend',copy=True)
print('SAVED_WS154B RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
