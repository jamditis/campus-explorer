# ws224b (W45b): after fix224a the slab edge on the arc (ring v260..v266, 125.85-125.90) stands up to ~4 cm over the
# curb back (rings k19..k29 125.845-125.892). Raise-only (AGENTS.md rule 6): curb top verts of each ring RAISED so the
# curb back sits 3 mm under the slab measured 2 cm inside the back; landing/road untouched. Reveal grows the same (printed).
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']
TL=BVHTree.FromPolygons([L.matrix_world@v.co for v in L.data.vertices],[p.vertices[:] for p in L.data.polygons])
def top(p):
    h=TL.ray_cast(Vector((p.x,p.y,130)),Vector((0,0,-1))); return h[0].z if h[0] else None
JOINT=0.003; MIN=0.006; tot=0
for name,n,b,f,tops,rings in (('WS220_CollegeAve_curb_jog_return_UNVERIFIED',5,3,1,(1,2,3),range(15,30)),
                              ('WS27_CollegeAve_curb_left_UNVERIFIED',6,3,1,(1,2,3,4),range(0,2))):
    o=bpy.data.objects[name]; M=o.matrix_world; MI=M.inverted()
    for k in rings:
        bk=M@o.data.vertices[n*k+b].co; fr=M@o.data.vertices[n*k+f].co
        zl=top(bk.xy+(bk.xy-fr.xy).normalized()*0.02)
        if zl is None: print('F224B k%d no slab'%k); continue
        d=zl-JOINT-bk.z
        if zl-bk.z<MIN or d<=0: print('F224B %s k%d ok lip %.1f cm'%(name[:5],k,(zl-bk.z)*100)); continue
        for j in tops:
            v=o.data.vertices[n*k+j]; w=M@v.co; w.z+=d; v.co=MI@w
        tot+=1
        print('F224B %s k%d raised %.1f cm -> back %.3f front %.3f (slab %.3f)'%(name[:5],k,d*100,bk.z+d,fr.z+d,zl),flush=True)
    o.data.update()
print('F224B rings raised',tot,flush=True)
