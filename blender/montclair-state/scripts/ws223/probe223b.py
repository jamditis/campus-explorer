import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']
others=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS215','WS69'))]
print('P223 others',[o.name for o in others])
def bvh(o):
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
TL=bvh(L); TO={o.name:bvh(o) for o in others}
def top(T,p):
    h=T.ray_cast(Vector((p.x,p.y,130)),Vector((0,0,-1)))
    return h[0].z if h[0] else None
for name,n,b,f,t in (('WS220_CollegeAve_curb_jog_return_UNVERIFIED',5,3,1,2),('WS27_CollegeAve_curb_left_UNVERIFIED',6,3,1,2)):
    o=bpy.data.objects[name]; M=o.matrix_world; V=[M@v.co for v in o.data.vertices]
    print('P223',name,'mods',[m.name for m in o.modifiers],'rings',len(V)//n)
    for k in range(len(V)//n):
        bk=V[n*k+b]; fr=V[n*k+f]
        if not (-250<bk.x<-245 and -55<bk.y<-52): continue
        d=(bk.xy-fr.xy).normalized(); p=bk.xy+d*0.04
        zl=top(TL,p); zo={nm:top(T,p) for nm,T in TO.items()}
        zo={a:round(z,3) for a,z in zo.items() if z}
        print('P223 %s k%d back(%.3f,%.3f) curb %.3f landing %s lip %s other %s'%(name[:5],k,bk.x,bk.y,bk.z,'%.3f'%zl if zl else '-', '%.1fcm'%((zl-bk.z)*100) if zl else '-',zo))
