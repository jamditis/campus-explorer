import bpy,os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws72/lite_load.py').read())
sc=bpy.context.scene
with bpy.data.libraries.load(src,link=False) as (fr,to): to.worlds=['WP2_World_GOLDEN']; to.objects=['WP2_Sun_GOLDEN']
for m in bpy.data.objects['Terrain_LiDAR_DTM_1m'].modifiers:
    if m.name.startswith('WS64'): m.show_viewport=False; m.show_render=False
s=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
ground=['Terrain_LiDAR_DTM_1m']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1]
s=s.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')",repr(tuple(ground)),1)
cut=s.index("camz('WS49"); end=s.index("base=bpy.data.objects.get('Sun')")
s=s[:cut]+os.environ.get('CAMDEF',"camz('WS78_CAM_eye_lot_from_E',(-207,-97,0),(-246,-84),28,1.7,0.8)\n")+s[end:]
pre=s.split("ts=datetime.now()",1)[0]
exec(compile(pre,'pre','exec'))
dg=bpy.context.evaluated_depsgraph_get()
c=bpy.data.objects[os.environ.get('PCAM','WS78_CAM_eye_lot_from_E')]
sc.render.resolution_x=1280; sc.render.resolution_y=720
TR,BR,BL,TL=[c.matrix_world@v for v in c.data.view_frame(scene=sc)]
o=c.matrix_world.translation
print('CAMLOC',tuple(round(x,2) for x in o))
for t in os.environ['PX'].split(';'):
    px,py=map(float,t.split(','))
    u=px/704; v=py/396
    p=TL.lerp(TR,u).lerp(BL.lerp(BR,u),v) if False else (TL.lerp(TR,u)).lerp(BL.lerp(BR,u),v)
    d=(p-o).normalized(); org=o.copy(); hits=[]
    for k in range(4):
        ok,loc,n,i,ob,m=sc.ray_cast(dg,org,d)
        if not ok: break
        mat=ob.material_slots[ob.data.polygons[i].material_index].material.name if ob.type=='MESH' and ob.material_slots and i<len(ob.data.polygons) else None
        hits.append((ob.name,mat,tuple(round(x,2) for x in loc))); org=loc+d*0.01
    print('WS79PX',px,py,hits,flush=True)
