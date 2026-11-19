# ws229 W53g: QI patch mesh vs dtm_1m / dsm_1m / 3DEP; where it sits high
import bpy,sys,json,numpy as np,collections
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy');S=np.load('/workspace/nj-scenes/montclair-state/data/dsm_1m.npy')
D=np.load('/workspace/nj-scenes/montclair-state/data/skirt_dem_10m.npy')
def d(x,y,M=A): return float(M[min(499,max(0,int(y+250))),min(499,max(0,int(x+250)))])
def d3(x,y): return float(D[int((2000-y)/10), int((x+2000)/10)])
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; m=t.modifiers['QI_east_edge_LiDAR_patch']
ng=m.node_group
print('P229 QI nodes',[(n.bl_idname,n.name,getattr(n,'operation',''),[ (i.name, getattr(i,'default_value',None) if not hasattr(getattr(i,'default_value',None),'__len__') else None) for i in n.inputs if not i.is_linked][:4]) for n in ng.nodes],flush=True)
for k in m.keys(): print('P229 QI input',k,m[k],flush=True)
for n in ng.nodes:
    if n.bl_idname=='GeometryNodeObjectInfo': print('P229 objinfo',n.inputs[0].default_value.name if n.inputs[0].default_value else None,flush=True)
for nm in ['QI_east_edge_LiDAR_terrain_patch','QI_east_edge_delete_probe']:
    o=bpy.data.objects.get(nm)
    if not o: print('P229 missing',nm); continue
    mw=o.matrix_world; vs=[mw@v.co for v in o.data.vertices]
    print('P229',nm,'v',len(vs),'f',len(o.data.polygons),'x',round(min(v.x for v in vs),1),round(max(v.x for v in vs),1),'y',round(min(v.y for v in vs),1),round(max(v.y for v in vs),1),'mods',[mm.name for mm in o.modifiers],flush=True)
    if 'patch' in nm:
        dz=np.array([v.z-d(v.x,v.y) for v in vs]); ds=np.array([v.z-d(v.x,v.y,S) for v in vs])
        print('P229 dz vs dtm pct',np.percentile(dz,[1,10,50,90,99]).round(2),'n>0.5',int((dz>0.5).sum()),'n>1.5',int((dz>1.5).sum()),flush=True)
        hi=[(round(v.x),round(v.y),round(v.z-d(v.x,v.y),2),round(v.z-d(v.x,v.y,S),2),round(v.z-d3(v.x,v.y),2)) for v in vs if v.z-d(v.x,v.y)>0.5]
        c=collections.Counter((h[0]//10*10,h[1]//10*10) for h in hi); print('P229 hi cells',sorted(c.items())[:60],flush=True)
        print('P229 hi sample (x,y,dtm,dsm,3dep)',hi[:40],flush=True)
        near=[(round(v.x,1),round(v.y,1),round(v.z,2),round(d(v.x,v.y),2),round(d(v.x,v.y,S),2),round(d3(v.x,v.y),2)) for v in vs if abs(v.x-205)<3 and abs(v.y+45)<3]
        print('P229 near205',near[:20],flush=True)
sys.stdout.flush(); import os; os._exit(0)
