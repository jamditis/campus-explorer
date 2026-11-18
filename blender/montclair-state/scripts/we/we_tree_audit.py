import bpy, json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
bbs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith('TL_tree') or o.hide_render or o.name=='Context_ground_beyond_data': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    bbs.append((o,min(p.x for p in bb),max(p.x for p in bb),min(p.y for p in bb),max(p.y for p in bb),o.matrix_world.inverted()))
ev={}
def hits(x,y):
    H=[]
    for o,x0,x1,y0,y1,inv in bbs:
        if not(x0<=x<=x1 and y0<=y<=y1): continue
        e=ev.get(o.name) or ev.setdefault(o.name,o.evaluated_get(dg))
        lo=inv@Vector((x,y,500)); ld=(inv@Vector((x,y,0))-lo).normalized()
        r=e.ray_cast(lo,ld)
        if r[0]: H.append((round((o.matrix_world@r[1]).z,3),o.name))
    H.sort(reverse=True); return H
out=[]
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree') or o.type!='MESH': continue
    mw=o.matrix_world; p0=mw.translation
    P=[ (mw@v.co).z for v in o.data.vertices if ((mw@v.co).xy-p0.xy).length<0.3]
    if not P: continue
    tb=min(P); H=hits(p0.x,p0.y)
    out.append(dict(n=o.name,x=round(p0.x,2),y=round(p0.y,2),oz=round(p0.z,3),tb=round(tb,3),H=H[:4]))
json.dump(out,open('data/we/tree_audit.json','w'))
print('AUD',len(out))
