# ws264 probe (NO SAVE): NaN proxy + empty mesh stubs — who references them; 12 absolute paths list.
import bpy, os, numpy as np
T='P264A'
sc=bpy.context.scene
# object references from modifiers (GN inputs, object fields), nodegroups (Object Info / object sockets), constraints, parents
ref={}
def add(o,why):
    if o is not None: ref.setdefault(o.name,set()).add(why)
for ob in bpy.data.objects:
    if ob.parent: add(ob.parent,'parent_of:'+ob.name[:30])
    for m in ob.modifiers:
        for p in dir(m):
            if p.startswith('_'): continue
            try: v=getattr(m,p)
            except Exception: continue
            if isinstance(v,bpy.types.Object): add(v,'mod:'+ob.name[:30]+'/'+m.name)
        if m.type=='NODES':
            for k in m.keys():
                v=m[k]
                if isinstance(v,bpy.types.Object): add(v,'gnin:'+ob.name[:30])
    for c in ob.constraints:
        t=getattr(c,'target',None)
        if isinstance(t,bpy.types.Object): add(t,'con:'+ob.name[:30])
for ng in bpy.data.node_groups:
    for n in ng.nodes:
        for s in n.inputs:
            v=getattr(s,'default_value',None)
            if isinstance(v,bpy.types.Object): add(v,'ng:'+ng.name[:30])
        for a in ('object',):
            v=getattr(n,a,None)
            if isinstance(v,bpy.types.Object): add(v,'ngobj:'+ng.name[:30])
o=bpy.data.objects.get('WS113_paving_tops_proxy')
if o:
    me=o.data; n=len(me.vertices); a=np.empty(n*3,np.float32); me.vertices.foreach_get('co',a); a=a.reshape(-1,3)
    bad=~np.isfinite(a).all(1)
    fv=[set(p.vertices) for p in me.polygons]; badset=set(np.where(bad)[0].tolist())
    print(T,'proxy verts',n,'nan',int(bad.sum()),'faces',len(me.polygons),'faces touching nan',sum(1 for s in fv if s&badset),
          'hide_render',o.hide_render,'hide_vp',o.hide_viewport,'mods',[m.name for m in o.modifiers],'refs',sorted(ref.get(o.name,[])),'meshusers',me.users,flush=True)
    good=a[~bad]; print(T,'proxy bbox',good.min(0).round(2).tolist(),good.max(0).round(2).tolist(),flush=True)
emp=[]
for ob in sc.objects:
    if ob.type!='MESH' or ob.library or len(ob.data.vertices): continue
    emp.append((ob.name,len(ob.modifiers),[m.type for m in ob.modifiers][:3],len(ob.children),sorted(ref.get(ob.name,[]))[:3],ob.data.users,ob.hide_render,[c.name for c in ob.users_collection][:2]))
safe=[e for e in emp if e[1]==0 and e[3]==0 and not e[4]]
print(T,'empty',len(emp),'withmods',sum(1 for e in emp if e[1]),'withchildren',sum(1 for e in emp if e[3]),'referenced',sum(1 for e in emp if e[4]),'safe',len(safe),flush=True)
for e in emp: print(T,'E',e,flush=True)
for coll in ('images','libraries'):
    for i in getattr(bpy.data,coll):
        fp=getattr(i,'filepath','')
        if coll=='images' and i.packed_file: continue
        if fp and not fp.startswith('//'): print(T,'ABS',coll,i.name,fp,'lib',getattr(i,'library',None),flush=True)
os._exit(0)
