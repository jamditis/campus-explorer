import bpy, json
from mathutils import Vector
E=json.load(open('data/ti/east_levels.json'))
def pip(x,y,poly):
    ins=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
P={w:E[w]['outer'] for w in ('313028565','313029108')}
trees={}; others={}
for o in bpy.data.objects:
    if 'ti_obj' in o or o.type not in ('MESH','EMPTY','CURVE'): continue
    n=o.name
    if any(k in n.lower() for k in ('terrain','skirt','grass','ground_','context','bd_')): continue
    for w,poly in P.items():
        if o.name.startswith('T_') or o.type=='EMPTY':
            t=o.matrix_world.translation
            if pip(t.x,t.y,poly): trees.setdefault(w,[]).append(n)
        elif o.type=='MESH' and len(o.data.vertices)<200000:
            mw=o.matrix_world; c=sum(1 for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//3000)] if pip(*(mw@v.co).xy,poly))
            if c: others.setdefault(w,[]).append((n,c,len(o.data.vertices)))
for w in P:
    print('CHK',w,'trees inside',len(trees.get(w,[])),trees.get(w,[])[:8]); print('CHK',w,'meshes inside',others.get(w,[])[:30])
print('CHK grass',[(o.name,o['ti_culled']) for o in bpy.data.objects if 'ti_culled' in o])
print('CHK objs',len(bpy.data.objects))
