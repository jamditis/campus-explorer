import bpy
from mathutils import Vector
dg = bpy.context.evaluated_depsgraph_get()
for k in range(3):
    o = bpy.data.objects.get('VV_Blanton_entrance_%d_path_link_UNVERIFIED'%k)
    L = bpy.data.objects.get('TU_Blanton_entrance_%d_landing_UNVERIFIED'%k)
    if not o: print('missing link',k); continue
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    xs=[v.x for v in vs]; ys=[v.y for v in vs]; zs=[v.z for v in vs]
    print('LINK',k,'nvert',len(vs),'xy',[round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2)],'z',[round(min(zs),2),round(max(zs),2)],'hide',o.hide_render,o.hide_viewport,'mats',[m.name for m in o.data.materials])
    if L:
        lv=[L.matrix_world@v.co for v in L.data.vertices]
        print('  LAND z',[round(min(v.z for v in lv),2),round(max(v.z for v in lv),2)],'xy',[round(min(v.x for v in lv),2),round(max(v.x for v in lv),2),round(min(v.y for v in lv),2),round(max(v.y for v in lv),2)])
# cams
for nm in ['VV_CAM_closeup_Blanton_landing_path_join','VV_CAM_eye_Blanton_W_path_continuity','TU_CAM_eye_Blanton_W_entrances']:
    c=bpy.data.objects.get(nm)
    if c: print('CAM',nm,[round(x,1) for x in c.location], 'lens', c.data.lens)
# check grass points near door 0
g=bpy.data.objects.get('TJ_Webster_lawn_grass_points_UNVERIFIED')
if g:
    # count points near link 0 bbox
    o=bpy.data.objects['VV_Blanton_entrance_0_path_link_UNVERIFIED']
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    x0,x1,y0,y1=min(v.x for v in vs)-0.5,max(v.x for v in vs)+0.5,min(v.y for v in vs)-0.5,max(v.y for v in vs)+0.5
    pts=g.data.vertices
    n=0
    for v in pts:
        p=g.matrix_world@v.co
        if x0<=p.x<=x1 and y0<=p.y<=y1: n+=1
    print('grass pts near link0', n, 'of', len(pts))
print('OBJS', len(bpy.data.objects))
