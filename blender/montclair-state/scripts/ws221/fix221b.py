# ws221b W40: WS72 Kasser landing S outline over the WS70 verge (x -251.5...-248.9) was a rounded bulge (poured-blob edge).
# Straightened: the S boundary columns (top + bottom vert of each, slab thickness kept) moved onto the straight chord from
# where the landing leaves the WS69 curb back (-251.503,-54.911) to its corner on the W39 curb-return back (-248.93,-54.455),
# so the verge reads as a clean grass triangle (curb / straight walk edge / curb return). Exposed grass at the new edge
# raised to landing top - 3 cm (raise-only). Exact walk edge line UNVERIFIED (2020 ortho: verge tip, edge not resolvable).
import bpy
from mathutils import Vector
A=Vector((-251.503,-54.911)); B=Vector((-248.93,-54.455))
ld=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; MW=ld.matrix_world; MI=MW.inverted()
TOP=[]; n=0
for i in (90,91,100,101,110,111,120,121):
    v=ld.data.vertices[i]; w=MW@v.co
    assert -251.1<w.x<-249.4 and w.y<-54.7, ('F221B unexpected vert',i,tuple(w))
    t=(w.x-A.x)/(B.x-A.x); y=A.y+(B.y-A.y)*t
    print('F221B v%d x %.3f y %.3f -> %.3f'%(i,w.x,w.y,y),flush=True)
    w.y=y; v.co=MI@w; n+=1
    if i%2==0: TOP.append((w.x,w.z))
ld.data.update()
TOP=sorted(TOP+[(A.x,(MW@ld.data.vertices[80].co).z),(B.x,(MW@ld.data.vertices[130].co).z)])
def ztop(x):
    for (x0,z0),(x1,z1) in zip(TOP,TOP[1:]):
        if x0<=x<=x1: return z0+(z1-z0)*(x-x0)/(x1-x0)
    return TOP[0][1] if x<TOP[0][0] else TOP[-1][1]
g=bpy.data.objects['WS70_gap_strip_grass_berms']; GM=g.matrix_world; GI=GM.inverted(); nr=0
for i in (103,104,109,98,92):
    v=g.data.vertices[i]; w=GM@v.co; zt=ztop(w.x)-0.03
    if w.z<zt: print('F221B grass v%d %.3f %.3f z %.3f -> %.3f'%(i,w.x,w.y,w.z,zt),flush=True); w.z=zt; v.co=GI@w; nr+=1
g.data.update(); print('F221B landing verts',n,'grass raised',nr,flush=True)
