# ws86d: WS60 terrain-edge apron W of the grandstand lawn (x -285..-249, y -165..-125) sat 2-3 m above the north LiDAR dtm_filled -> big faceted planes in the SW oblique. Lower-only to the DTM, 3 m feather.
import bpy,numpy as np,math,os,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
g=np.load('/workspace/nj-scenes/montclair-state/north/data/grid_1m.npz'); N=g['dtm_filled']
def dtm(x,y):
    fx=x+600-0.5; fy=y+260-0.5; i=int(math.floor(fx)); j=int(math.floor(fy)); a=fx-i; b=fy-j
    return float((N[j,i]*(1-a)+N[j,i+1]*a)*(1-b)+(N[j+1,i]*(1-a)+N[j+1,i+1]*a)*b)
A=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt'];print('A86 apron mods',[(m.name,m.type) for m in A.modifiers])
X0,X1,Y0,Y1,F=-285.0,-249.0,-165.0,-125.0,3.0
mw=A.matrix_world;mi=mw.inverted();n=0;mx=0
for v in A.data.vertices:
    p=mw@v.co
    dx=max(X0-p.x,0,p.x-X1);dy=max(Y0-p.y,0,p.y-Y1);d=math.hypot(dx,dy)
    if d>=F: continue
    w=1-d/F;w=w*w*(3-2*w)
    t=dtm(p.x,p.y);z=min(p.z,p.z+(t-p.z)*w)
    if z<p.z-0.01: mx=max(mx,p.z-z);v.co=mi@Vector((p.x,p.y,z));n+=1
A.data.update();print('A86 apron verts lowered',n,'max',round(mx,2))
dg=bpy.context.evaluated_depsgraph_get();dg.update()
m=A.evaluated_get(dg).to_mesh();bm=bmesh.new();bm.from_mesh(m);bm.transform(mw);BV=BVHTree.FromBMesh(bm)
for x,y in[(-260,-140),(-255,-150),(-270,-145),(-252,-130),(-265,-160)]:
    h=BV.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0];print('V86 apron eval',x,y,round(h.z,2) if h else None,'dtm',round(dtm(x,y),2))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A86 saved apron')
