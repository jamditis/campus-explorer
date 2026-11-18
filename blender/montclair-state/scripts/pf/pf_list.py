import bpy,mathutils,collections
X0,X1,Y0,Y1=-280,-183,132,250
cnt=collections.Counter(); big=[]
for o in bpy.context.scene.objects:
    if o.type not in('MESH','CURVE','EMPTY','LIGHT'): continue
    bb=[o.matrix_world@mathutils.Vector(v) for v in o.bound_box]
    x0=min(v.x for v in bb);x1=max(v.x for v in bb);y0=min(v.y for v in bb);y1=max(v.y for v in bb)
    if x1<X0 or x0>X1 or y1<Y0 or y0>Y1: continue
    inside = x0>=X0 and x1<=X1 and y0>=Y0 and y1<=Y1
    key=(o.users_collection[0].name if o.users_collection else '-')
    if inside and (x1-x0)<20 and (y1-y0)<20: cnt[key]+=1
    else: big.append((o.name[:50],key[:30],o.type,round(x0),round(x1),round(y0),round(y1),round(min(v.z for v in bb),1),inside))
for k,v in cnt.most_common(): print('SMALL',v,k)
for b in big: print('BIG',b)
