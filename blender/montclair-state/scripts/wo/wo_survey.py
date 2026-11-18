# wo: READ-ONLY survey of cameras / world / sun / view settings. No save.
import bpy, json, sys, math
out=sys.argv[sys.argv.index('--')+1]
S=bpy.context.scene
r={'file':bpy.data.filepath,'scenes':[s.name for s in bpy.data.scenes],'objects':len(bpy.data.objects),
   'active_camera':S.camera.name if S.camera else None,'engine':S.render.engine,
   'res':[S.render.resolution_x,S.render.resolution_y,S.render.resolution_percentage],
   'view':{'transform':S.view_settings.view_transform,'look':S.view_settings.look,'exposure':S.view_settings.exposure,'gamma':S.view_settings.gamma},
   'world':S.world.name if S.world else None,'worlds':[w.name for w in bpy.data.worlds],'cycles':{}}
try: r['cycles']={'samples':S.cycles.samples,'denoise':S.cycles.use_denoising}
except Exception: pass
if S.world and S.world.use_nodes:
    r['world_nodes']=[(n.type,n.name,(n.image.name if getattr(n,'image',None) else None)) for n in S.world.node_tree.nodes]
    for n in S.world.node_tree.nodes:
        if n.type=='BACKGROUND': r.setdefault('world_bg_strength',[]).append(n.inputs['Strength'].default_value)
        if n.type=='TEX_SKY': r['sky']={'type':n.sky_type,'sun_el':getattr(n,'sun_elevation',None),'sun_rot':getattr(n,'sun_rotation',None)}
r['lights']=[]
for o in bpy.data.objects:
    if o.type=='LIGHT':
        L=o.data; e=o.matrix_world.to_euler()
        r['lights'].append({'name':o.name,'type':L.type,'energy':L.energy,'color':list(L.color),'angle':getattr(L,'angle',None),
            'rot_deg':[round(math.degrees(a),1) for a in e],'hide_render':o.hide_render,'lib':bool(o.library)})
r['cameras']=[]
for o in bpy.data.objects:
    if o.type=='CAMERA':
        e=o.matrix_world.to_euler(); l=o.matrix_world.translation
        r['cameras'].append({'name':o.name,'loc':[round(l.x,1),round(l.y,1),round(l.z,1)],'rot_deg':[round(math.degrees(a),1) for a in e],
            'lens':round(o.data.lens,1),'colls':[c.name for c in o.users_collection]})
r['collections_top']=[c.name for c in S.collection.children]
json.dump(r,open(out,'w'),indent=1)
print('SURVEY_OK',len(r['cameras']),len(r['lights']))
