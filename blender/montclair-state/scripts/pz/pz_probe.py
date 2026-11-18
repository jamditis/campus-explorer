import bpy, bmesh, collections
from mathutils import Vector
def inwing(p): return p.x<-157.5 and 77.0<p.y<160.5+1.5
out=[]
for on in ('Dickson Hall walls','PX_Dickson_wing_parapet_infill_UNVERIFIED','PY_Dickson_wing_parapet_raise_UNVERIFIED','PY_Dickson_wing_parapet_coping_UNVERIFIED','PY_Dickson_wing_parapet_back_roofstrip_UNVERIFIED'):
    o=bpy.data.objects[on]; me=o.data; mw=o.matrix_world; WV=[mw@v.co for v in me.vertices]
    ec=collections.Counter()
    for p in me.polygons:
        for k in p.edge_keys: ec[k]+=1
    n=0
    for k,c in ec.items():
        if c!=1: continue
        a=WV[k[0]]; b=WV[k[1]]; m=(a+b)/2
        if not inwing(m): continue
        if 'coping' in on or 'back' in on:
            if m.x<-185 and m.y>150: out.append('%s OPEN %.2f %.2f %.2f -> %.2f %.2f %.2f'%(on[:20],a.x,a.y,a.z,b.x,b.y,b.z)); n+=1
            continue
        if (a.xy-b.xy).length<0.02 and abs(a.z-b.z)>0.2 and m.z>140:
            out.append('%s VERT %.2f %.2f z%.2f-%.2f'%(on[:20],a.x,a.y,min(a.z,b.z),max(a.z,b.z))); n+=1
    out.append('%s n=%d bbox x %.1f..%.1f'%(on,n,min(v.x for v in WV),max(v.x for v in WV)))
# coping corner region verts
o=bpy.data.objects['PY_Dickson_wing_parapet_coping_UNVERIFIED']
for v in o.data.vertices:
    c=o.matrix_world@v.co
    if c.z>153.0 and c.y>155 and c.x<-180: out.append('COPV %.2f %.2f'%(c.x,c.y))
open('data/pz/probe.txt','w').write('\n'.join(out)); print('PROBE',len(out))
