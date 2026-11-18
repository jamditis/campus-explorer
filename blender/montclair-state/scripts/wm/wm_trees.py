import bpy, json
out=[]; names=[]
for o in bpy.data.objects:
    if o.type not in('MESH','EMPTY') or o.hide_render or not o.visible_get() or any(c.hide_render for c in o.users_collection): continue
    n=o.name.lower()
    if 'tree' not in n: continue
    from mathutils import Vector
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; t=sum(bb,Vector())/8
    if not(100<t.x<340 and 200<t.y<440): continue
    if o.type=='EMPTY': continue
    r=max(max(b.x for b in bb)-min(b.x for b in bb),max(b.y for b in bb)-min(b.y for b in bb))/2 if o.type=='MESH' else 3
    if r>25 or r<0.5: r=4
    out.append((t.x,t.y,r)); names.append(o.name)
json.dump(out,open('/workspace/nj-scenes/montclair-state/data/wm/trees_xy.json','w')); print('TREES',len(out)); json.dump(names,open('/workspace/nj-scenes/montclair-state/data/wm/trees_names.json','w'))
