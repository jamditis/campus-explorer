
import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read().split('\n')
src='\n'.join(src[:18]).replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1]+[o.name for o in bpy.data.objects if o.name.startswith(('WS113_terrain_fan_fill','WS110_ground_patch','WS133b_','WS134_ground'))])")
exec(src)
camz('WS143_CAM_eye_forecourt_from_N_aisle',(-64.5,-160,0),(-73,-176),26,1.7,0.5)
camz('WS143_CAM_closeup_forecourt_curb_lot_N',(-66.5,-182.5,0),(-71,-177.5),30,1.6,0.0)
sc.render.resolution_x=1280; sc.render.resolution_y=720
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()

oz=bpy.data.objects['OZ_walk_joints_auto_GN_UNVERIFIED']
for m in oz.modifiers:
    print("OZMOD",m.type,m.name, getattr(m,'node_group',None) and m.node_group.name)
    if m.type=='NODES':
        for k,v in m.items(): print("  IN",k,v if not hasattr(v,'name') else v.name)
        for n in m.node_group.nodes:
            if n.type in ('OBJECT_INFO','COLLECTION_INFO'): print("  NODE",n.type, [ (i.name, getattr(i,'default_value',None)) for i in n.inputs])
oz.hide_viewport=True
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
def probe(camname, pts):
    cam=bpy.data.objects[camname]
    fr=[cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]
    o=cam.matrix_world.translation
    for (u,v) in pts:
        tr,br,bl,tl=fr
        p=tl+(tr-tl)*u+(bl-tl)*v
        d=(p-o).normalized()
        hit,loc,n,i,ob,m=sc.ray_cast(dg,o,d)
        mat=None
        if hit:
            try: mat=ob.material_slots[ob.data.polygons[i].material_index].material.name
            except Exception as e: mat=str(e)[:30]
        print("HIT",camname[8:20],(round(u,2),round(v,2)), ob.name[:70] if hit else None, mat, tuple(round(c,2) for c in loc) if hit else None)

probe("WS143_CAM_closeup_forecourt_curb_lot_N",[(400/640,250/360),(500/640,280/360),(380/640,240/360),(600/640,300/360),(560/640,260/360),(450/640,245/360),(520/640,255/360)])
