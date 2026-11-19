# ws230 W53j probe d: QJ / QI / QH node groups on the terrain (inputs, object refs)
import bpy,sys
M='/workspace/nj-scenes/montclair-state/'
with bpy.data.libraries.load(M+'montclair_state.blend',link=False) as (src,dst): dst.objects=['Terrain_LiDAR_DTM_1m']
o=dst.objects[0]
f=bpy.data.objects.get('QJ_NE_seam_ramp_field')
if f:
    W=f.matrix_world; vs=[W@v.co for v in f.data.vertices]
    import collections
    print('P230D field v',len(vs),'f',len(f.data.polygons),'zmin',min(v.z for v in vs),flush=True)
    c=collections.defaultdict(list)
    for v in vs: c[(int(v.x//4*4),int(v.y//8*8))].append(v.z)
    print('P230D field low cells',sorted([(k,round(min(z),2)) for k,z in c.items() if min(z)<-0.3]),flush=True)
for m in o.modifiers:
    if m.name[:2] in ('QJ',):
        ng=m.node_group
        print('P230D',m.name,'show',m.show_viewport,m.show_render,flush=True)
        for n in ng.nodes:
            ins=[]
            for i in n.inputs:
                if not i.is_linked and hasattr(i,'default_value'):
                    dv=i.default_value
                    if hasattr(dv,'name'): ins.append((i.name,dv.name))
                    elif isinstance(dv,(int,float)) and not isinstance(dv,bool): ins.append((i.name,round(dv,3)))
                    elif hasattr(dv,'__len__') and not isinstance(dv,str) and len(dv)<=4: ins.append((i.name,tuple(round(x,2) for x in dv)))
            print('P230D   ',n.bl_idname,n.name,getattr(n,'operation',getattr(n,'data_type','')),ins[:6],flush=True)
        for k in m.keys(): 
            v=m[k]; print('P230D   in',k,getattr(v,'name',v),flush=True)
sys.stdout.flush(); import os; os._exit(0)
