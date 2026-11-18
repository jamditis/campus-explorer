import bpy, bmesh
from mathutils import Vector
print('MATS',[m.name for m in bpy.data.materials if 'Dickson' in m.name or 'PV' in m.name[:3] or 'plain' in m.name.lower()])
o=bpy.data.objects['Dickson Hall walls']; me=o.data; mw=o.matrix_world
print('SLOTS',[(i,s.link,s.material.name if s.material else None) for i,s in enumerate(o.material_slots)])
print('UV',[u.name for u in me.uv_layers],'ATTR',[a.name for a in me.attributes if not a.name.startswith('.')])
for p in me.polygons:
    c=mw@p.center
    if abs(c.x+182.3)<3 and abs(c.y-79)<6 and abs(p.normal.z)<0.3:
        vs=[mw@me.vertices[v].co for v in p.vertices]
        xs=[v.x for v in vs]; ys=[v.y for v in vs]; zs=[v.z for v in vs]
        w=max(((Vector((a.x,a.y,0))-Vector((b.x,b.y,0))).length for a in vs for b in vs))
        print('F',p.index,'mat',p.material_index,'n',tuple(round(x,2) for x in p.normal),'c',tuple(round(x,2) for x in c),'w %.2f'%w,'z %.1f-%.1f'%(min(zs),max(zs)),'area %.1f'%p.area)
# what about the right strip: probe south-face east end near tree; list narrow wall faces anywhere on Dickson with shader-window material
import collections
cnt=collections.Counter()
nar=[]
for p in me.polygons:
    if abs(p.normal.z)>0.3: continue
    vs=[mw@me.vertices[v].co for v in p.vertices]
    w=max(((Vector((a.x,a.y,0))-Vector((b.x,b.y,0))).length for a in vs for b in vs))
    h=max(v.z for v in vs)-min(v.z for v in vs)
    if w<1.6 and h>4: nar.append((p.index,p.material_index,round(w,2),round(h,1),tuple(round(x,1) for x in (mw@p.center))))
print('NARROW',len(nar)); [print(' ',n) for n in nar[:60]]
