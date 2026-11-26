# ws254 read-only M4 probe (CHAIN via merge208, exits before save): NORTH_MERGE objects vs main objects -> likely duplicates
# (overlapping world bbox IoU > 0.5, a shared material, bbox dims within 20%); plus the Sprague L0 east-strip box vs Cafe Diem.
import bpy, os
from mathutils import Vector
NM=bpy.data.collections.get('NORTH_MERGE')
def allobjs(c):
    s=set(c.objects)
    for ch in c.children: s|=allobjs(ch)
    return s
north=allobjs(NM) if NM else set()
print('M4P north objs',len(north),flush=True)
def bbw(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; return [min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb)]
B={o.name:bbw(o) for o in bpy.data.objects if o.type=='MESH'}
def vol(b): return max(b[1]-b[0],0.05)*max(b[3]-b[2],0.05)*max(b[5]-b[4],0.05)
def iou(a,b):
    i=[max(a[0],b[0]),min(a[1],b[1]),max(a[2],b[2]),min(a[3],b[3]),max(a[4],b[4]),min(a[5],b[5])]
    if i[1]<=i[0] or i[3]<=i[2] or i[5]<i[4]: return 0.0
    vi=vol(i); return vi/(vol(a)+vol(b)-vi)
mains=[o for o in bpy.data.objects if o.type=='MESH' and o not in north]
hits=0
for n in sorted(north,key=lambda o:o.name):
    if n.type!='MESH' or n.name not in B: continue
    a=B[n.name]; mn=set(m.name for m in n.data.materials if m)
    for m in mains:
        b=B[m.name]
        if b[1]<a[0] or b[0]>a[1] or b[3]<a[2] or b[2]>a[3]: continue
        u=iou(a,b)
        if u<0.5: continue
        mm=set(x.name for x in m.data.materials if x)
        dims=all(abs((a[2*k+1]-a[2*k])-(b[2*k+1]-b[2*k]))<=0.2*max(a[2*k+1]-a[2*k],b[2*k+1]-b[2*k],0.3) for k in range(3))
        if (mn&mm) and dims:
            hits+=1; print('M4P DUP? north',repr(n.name),'main',repr(m.name),'IoU %.2f'%u,'verts',len(n.data.vertices),len(m.data.vertices),'mats',sorted(mn&mm)[:2],'hide_r',n.hide_render,m.hide_render,flush=True)
print('M4P candidate pairs',hits,flush=True)
for o in bpy.data.objects:
    if o.type!='MESH' or o.name not in B: continue
    b=B[o.name]
    if ('L0' in o.name or 'Sprague' in o.name) and b[0]<-43 and b[1]>-112 and b[2]<77 and b[3]>-16 and (b[1]-b[0])>30:
        cov=not (b[1]<-60 or b[0]>-43 or b[3]<35 or b[2]>71)
        print('M4P SpragueL0?',repr(o.name),'x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f'%tuple(b),'covers cafe bbox',cov,'hide_r',o.hide_render,flush=True)
os._exit(0)
