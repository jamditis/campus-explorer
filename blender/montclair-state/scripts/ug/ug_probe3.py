import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
def mk(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); mw=o.matrix_world; iw=mw.inverted(); d=(iw.to_3x3()@Vector((0,0,-1))).normalized()
    def f(x,y):
        r=e.ray_cast(iw@Vector((x,y,400)),d); return (mw@r[1]).z if r[0] else None
    return f
T=mk('Terrain_LiDAR_DTM_1m'); S=mk('SA_ground_lower_patch_UNVERIFIED'); K=mk('Context_skirt_3DEP_ortho_4km')
rows=[]
for y in range(240,262):
    s=''
    for x in range(-70,-38,1):
        t=T(x+.5,y+.5); a=S(x+.5,y+.5)
        z=t if t is not None else a
        s+= ('  .' if z is None else ('%3d'%int(round((z-137)*10))))
    print('UGH %d %s'%(y,s))
# objects with verts in region x -70..-40 y 244..258 below 139.0
sc=bpy.context.scene
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    if len(o.data.vertices)>400000: continue
    mw=o.matrix_world; n=0
    for v in o.data.vertices:
        p=mw@v.co
        if -70<p.x<-40 and 246<p.y<254 and 137<p.z<139.0: n+=1
    if n: print('UGO',o.name,n,len(o.data.vertices))
