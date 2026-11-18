# world-aligned crop of what the ground shaders' ortho sample shows, x -350..-240, y -165..-55 @0.5m
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to):
    to.objects=[n for n in fr.objects if n.startswith('WS68_RHD_ground') or n=='Terrain_LiDAR_DTM_1m']
out={}
for o in to.objects:
    print('OBJ',o.name[:40],len(o.data.polygons),[m.name for m in o.data.materials][:4],o.data.uv_layers.keys(),flush=True)
    for m in o.data.materials[:3]:
        imgs=[(n.name,n.image.filepath,tuple(n.image.size)) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
        print('  MAT',m.name,imgs[:12])
        uvn=[(n.name,n.uv_map) for n in m.node_tree.nodes if n.type=='UVMAP']; print('  UVN',uvn)
from mathutils.geometry import barycentric_transform
X0,X1,Y0,Y1,S=-350,-240,-165,-55,0.5
nx=int((X1-X0)/S); ny=int((Y1-Y0)/S)
res=np.zeros((ny,nx,3)); src_id=np.zeros((ny,nx),int)
for k,o in enumerate(sorted(to.objects,key=lambda o:o.name.startswith('Terrain'))):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.faces.ensure_lookup_table()
    uvl=bm.loops.layers.uv['ortho']; T=BVHTree.FromBMesh(bm)
    m=o.data.materials[0]; img=[n.image for n in m.node_tree.nodes if n.name=='Image Texture.003'][0]
    W,H=img.size; px=np.array(img.pixels[:],dtype=np.float32).reshape(H,W,4)
    print('img',img.name,W,H,flush=True)
    for j in range(ny):
        for i in range(nx):
            if src_id[j,i]: continue
            x=X0+(i+.5)*S; y=Y0+(j+.5)*S
            h=T.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if not h[0]: continue
            f=bm.faces[h[2]]; ls=f.loops
            if len(ls)<3: continue
            # triangle fan pick
            p=h[0]; best=None
            for t in range(1,len(ls)-1):
                a,b,c=ls[0],ls[t],ls[t+1]
                from mathutils.geometry import intersect_point_tri_2d
                if intersect_point_tri_2d(p.xy,a.vert.co.xy,b.vert.co.xy,c.vert.co.xy): best=(a,b,c);break
            if not best: best=(ls[0],ls[1],ls[2])
            a,b,c=best
            uv=barycentric_transform(p,a.vert.co,b.vert.co,c.vert.co,a[uvl].uv.to_3d(),b[uvl].uv.to_3d(),c[uvl].uv.to_3d())
            u=min(max(uv.x%1.0 if uv.x>1 or uv.x<0 else uv.x,0),0.9999); v=min(max(uv.y,0),0.9999)
            res[j,i]=px[int(v*H),int(u*W),:3]; src_id[j,i]=k+1
    bm.free()
np.save('/workspace/nj-scenes/montclair-state/scripts/ws75/crop_rgb.npy',res); np.save('/workspace/nj-scenes/montclair-state/scripts/ws75/crop_src.npy',src_id)
print('DONE',flush=True)
