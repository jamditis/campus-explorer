# ws230 W53j probe c: what fills x 230..250, y 40..250 (QI patch east boundary, base terrain faces, delete probe, apron inner edge)
import bpy,sys,numpy as np
M='/workspace/nj-scenes/montclair-state/'
P=np.load(M+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy'); A=np.load(M+'data/dtm_1m.npy')
def p3(x,y): return float(P[int(y+280),int(x+280)])
def dt(x,y): return float(A[min(499,int(y+250)),min(499,int(x+250))])
NAMES=['QI_east_edge_LiDAR_terrain_patch','Terrain_LiDAR_DTM_1m','QI_east_edge_delete_probe','WS60_terrain_edge_apron_LiDAR_to_skirt','QH_east_fan_LiDAR_terrain_patch']
with bpy.data.libraries.load(M+'montclair_state.blend',link=False) as (src,dst): dst.objects=[n for n in src.objects if n in NAMES]
for o in dst.objects:
    me=o.data; mw=o.matrix_world; V=[mw@v.co for v in me.vertices]
    print('P230C',o.name,'mods',[(m.name,m.type,getattr(m,'node_group',None) and m.node_group.name) for m in o.modifiers],flush=True)
    big=[]
    for p in me.polygons:
        vs=[V[i] for i in p.vertices]; xs=[v.x for v in vs]; ys=[v.y for v in vs]
        if max(xs)>230 and min(xs)<250 and max(ys)>40 and min(ys)<250:
            big.append((p.index,round(p.area,1),[(round(v.x,1),round(v.y,1),round(v.z,2),round(v.z-p3(v.x,v.y),2)) for v in vs]))
    print('P230C',o.name,'faces in box',len(big),flush=True)
    big.sort(key=lambda t:-t[1])
    for b in big[:12]: print('P230C  ',b,flush=True)
    if o.name.startswith('QI_east_edge_LiDAR'):
        # boundary: max x per 4 m y band
        import collections
        mx=collections.defaultdict(lambda:-1e9)
        for v in V:
            if v.y>30: k=int(v.y//4*4); mx[k]=max(mx[k],v.x)
        print('P230C QI max x per 4m band',[(k,round(mx[k],1)) for k in sorted(mx)][::3],flush=True)
sys.stdout.flush(); import os; os._exit(0)
