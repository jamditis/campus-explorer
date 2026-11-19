import bpy, bmesh, sys, os
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def dtm(x,y):
    gx=x+250-0.5; gy=y+250-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(498,max(0,i)); j=min(498,max(0,j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; o=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']
print('P228 terrain mw ident',t.matrix_world.is_identity,'apron ident',o.matrix_world.is_identity,flush=True)
print('P228 terrain mods',[(m.name,m.type,m.show_render) for m in t.modifiers],flush=True)
print('P228 apron mods',[(m.name,m.type,m.show_render) for m in o.modifiers],'v/f',len(o.data.vertices),len(o.data.polygons),flush=True)
bm=bmesh.new(); bm.from_mesh(t.data)
bv=[v for v in bm.verts if v.is_boundary and v.co.x>240 and v.co.y<-25]
bv.sort(key=lambda v:v.co.y)
for v in bv: print('P228 TB',round(v.co.x,2),round(v.co.y,2),round(v.co.z,2),'dz',round(v.co.z-dtm(v.co.x,v.co.y),2),'deg',len(v.link_edges),flush=True)
ab=bmesh.new(); ab.from_mesh(o.data)
av=[v for v in ab.verts if v.co.x>238 and v.co.y<-25]
av.sort(key=lambda v:v.co.y)
for v in av: print('P228 AV',round(v.co.x,2),round(v.co.y,2),round(v.co.z,2),'nf',len(v.link_faces),[len(f.verts) for f in v.link_faces],flush=True)
# apron faces touching the region
fs=set(f for v in av for f in v.link_faces)
print('P228 apron faces in region',len(fs),flush=True)
for f in list(fs)[:12]: print('P228 AF',[tuple(round(c,1) for c in v.co) for v in f.verts],flush=True)
sys.stdout.flush(); os._exit(0)
