import bpy, json, numpy as np
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws107/chapin_in107.py').read().split("# 1) existing")[0])
for o in [o for o in bpy.data.objects if o.name.startswith('WS107_Chapin_')]: bpy.data.objects.remove(o)
D='/workspace/nj-scenes/montclair-state/'
with bpy.data.libraries.load(D+'prep/ws107_Chapin_roofplanes/chapin_massing_ws107.blend') as (src,dst):
    dst.objects=[n for n in src.objects if n.startswith('WS107_Chapin_')]
col=bpy.data.collections['WS107_Chapin_Hall_massing_LiDAR2023_OSM_UNVERIFIED']
stucco=bpy.data.materials['COLE_stucco_plain_bq']; tile=bpy.data.materials['bx2_rhd_tile_roof_darker']
for o in dst.objects:
    col.objects.link(o)
    for s in o.material_slots:
        if s.material and 'stucco' in s.material.name: s.material=stucco
        if s.material and 'tile' in s.material.name: s.material=tile
# trees whose canopy pokes into the walls
segs=np.array([[O[i],O[(i+1)%len(O)]] for i in range(len(O))])
def nearest(px,py):
    a=segs[:,0];b=segs[:,1];ab=b-a;t=np.clip(((px-a[:,0])*ab[:,0]+(py-a[:,1])*ab[:,1])/(ab**2).sum(1),0,1)
    q=a+ab*t[:,None]; dd=np.hypot(q[:,0]-px,q[:,1]-py); i=dd.argmin(); return q[i],dd[i]
for o in [o for o in bpy.data.objects if o.name.startswith('T_') and not o.hide_render]:
    me=o.data
    if o.type!='MESH': continue
    co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); M=np.array(o.matrix_world); w=co@M[:3,:3].T+M[:3,3]
    k=infp(w[:,0],w[:,1])&(w[:,2]>127.5)
    if k.sum()<50: continue
    x,y=o.matrix_world.translation.x,o.matrix_world.translation.y
    q,dist=nearest(x,y)
    # radius of canopy toward the wall: max distance of inside verts past the wall line
    inside_depth=max(nearest(px,py)[1] for px,py in w[k][::max(1,k.sum()//400),:2])
    v=np.array([x-q[0],y-q[1]]); v=v/np.linalg.norm(v); mv=inside_depth+0.3
    if mv<=3.0:
        o.location.x+=v[0]*mv; o.location.y+=v[1]*mv; print('TREE107 moved',o.name,'out by %.2f m'%mv,'(canopy %d verts inside walls)'%k.sum())
    else:
        o.hide_render=True; o.hide_viewport=True; print('TREE107 hidden',o.name,'depth %.2f'%inside_depth)
print('R107 objs',len(dst.objects)); bpy.ops.wm.save_mainfile(); print('R107 SAVED')
