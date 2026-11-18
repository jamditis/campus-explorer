import bpy, json, math
from mathutils import Vector
th=math.radians(76.8); A=Vector((math.cos(th),math.sin(th),0)); B=Vector((math.cos(th-math.pi/2),math.sin(th-math.pi/2),0)); O=Vector((-238.1,-180.2,0))
def P(a,b,z=0): return O+A*a+B*b+Vector((0,0,z))
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
out={'grid':[], 'objs':{}}
names={}
a=-18.0
while a<=32:
    b=-3.0
    while b<=13:
        o=P(a,b,170); d=Vector((0,0,-1)); hs=[]
        for k in range(4):
            r,loc,n,i,ob,mw=sc.ray_cast(dg,o,d)
            if not r: break
            hs.append((ob.name,round(loc.z,2))); names[ob.name]=names.get(ob.name,0)+1
            o=loc+d*0.01
        out['grid'].append((a,b,hs)); b+=0.5
    a+=0.5
for n in names:
    ob=bpy.data.objects[n]
    out['objs'][n]={'type':ob.type,'mods':[(m.type,m.name) for m in ob.modifiers],'data':ob.data.name if ob.data else None,'users':ob.data.users if ob.data else 0,
      'nv':len(ob.data.vertices) if ob.type=='MESH' else 0,'coll':[c.name for c in ob.users_collection],'hidden':ob.hide_render,'mats':[m.name for m in ob.data.materials if m] if ob.type=='MESH' else [], 'parent':ob.parent.name if ob.parent else None,
      'loc':tuple(round(v,2) for v in ob.location),'rot':tuple(round(v,3) for v in ob.rotation_euler),'scale':tuple(round(v,3) for v in ob.scale)}
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws159/insp159.json','w'))
print('INSP159 done',len(names))
