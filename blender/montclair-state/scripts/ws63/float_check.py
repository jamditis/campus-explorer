import bpy,numpy as np,collections
D=np.load('data/dtm_1m.npy'); dg=bpy.context.evaluated_depsgraph_get()
st=collections.defaultdict(list)
for inst in dg.object_instances:
    o=inst.object; p=inst.matrix_world.translation
    if 97<p.x<139 and -78<p.y<-62 and o.type in('MESH','CURVE'):
        par=inst.parent.name if inst.is_instance and inst.parent else o.name
        st[par].append(p.z-D[int(p.y+250),int(p.x+250)])
for k,v in st.items(): v=np.array(v); print('FC',k,len(v),np.percentile(v,[5,50,95]).round(2))
