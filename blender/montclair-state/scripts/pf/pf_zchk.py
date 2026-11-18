import bpy,mathutils,hashlib
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; te=T.evaluated_get(bpy.context.evaluated_depsgraph_get()); mi=T.matrix_world.inverted()
out=[]
for x in range(-240,241,12):
    for y in range(-240,241,12):
        if -275<x<-186 and 134<y<250: continue
        h,l,n,i=te.ray_cast(mi@mathutils.Vector((x,y,400)),(0,0,-1)); out.append('%d,%d,%s'%(x,y,round((T.matrix_world@l).z,3) if h else None))
open('/tmp/zchk_'+bpy.path.basename(bpy.data.filepath)+'.txt','w').write('\n'.join(out)); print('ZCHK',len(out),hashlib.sha1('\n'.join(out).encode()).hexdigest()[:12])
