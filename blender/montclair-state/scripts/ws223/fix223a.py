# ws223a: the WS72 Kasser landing top stood 0.5-6.5 cm above the curb top along the W39 curb return back
# (WS220 return rings k15..k29) and the WS27 curb_left start (rings 0-1): a visible step/fold where the walk meets the
# curb. Raise-only fix (AGENTS.md rule 6): each affected curb ring's top verts are RAISED so the curb back sits 3 mm under
# the landing edge (a tooled joint); the landing and road are not touched. The resulting profile rises monotonically into
# the existing curb_left grade (ring 2 at 125.913). Reveal over the gutter grows by the same amount (printed).
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']
TL=BVHTree.FromPolygons([L.matrix_world@v.co for v in L.data.vertices],[p.vertices[:] for p in L.data.polygons])
def top(p):
    h=TL.ray_cast(Vector((p.x,p.y,130)),Vector((0,0,-1))); return h[0].z if h[0] else None
JOINT=0.003; MIN=0.006
tot=0
for name,n,b,f,tops,rings in (('WS220_CollegeAve_curb_jog_return_UNVERIFIED',5,3,1,(1,2,3),range(15,30)),
                              ('WS27_CollegeAve_curb_left_UNVERIFIED',6,3,1,(1,2,3,4),range(0,2))):
    o=bpy.data.objects[name]; M=o.matrix_world; MI=M.inverted()
    for k in rings:
        bk=M@o.data.vertices[n*k+b].co; fr=M@o.data.vertices[n*k+f].co
        zl=top(bk.xy+(bk.xy-fr.xy).normalized()*0.04)
        if zl is None: continue
        d=zl-JOINT-bk.z
        if zl-bk.z<MIN or d<=0: continue
        for j in tops:
            v=o.data.vertices[n*k+j]; w=M@v.co; w.z+=d; v.co=MI@w
        tot+=1
        print('F223A %s k%d raised %.1f cm -> back %.3f (landing %.3f)'%(name[:5],k,d*100,bk.z+d,zl),flush=True)
    o.data.update()
print('F223A rings raised',tot,flush=True)
