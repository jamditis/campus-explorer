"""ws17: flood-fill the planar LiDAR patch on Morehead's west slope around the pale-lens hit faces
(same normal within 0.02) and set em_ringforce=1 there. APPLY=1 saves. Test: renders border crop of sign cam."""
import bpy,bmesh,os
from mathutils import Vector
o=bpy.data.objects['Morehead Hall roof (LiDAR)']; me=o.data
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
seeds=[1029,1812,4570,4574,3059,3055,560]; N0=bm.faces[1029].normal.copy()
seen=set(seeds); st=list(seeds)
while st:
    f=bm.faces[st.pop()]
    for e in f.edges:
        for g in e.link_faces:
            if g.index not in seen and g.material_index==0 and (g.normal-N0).length<0.02: seen.add(g.index); st.append(g.index)
A=sum(bm.faces[i].calc_area() for i in seen)
cs=[bm.faces[i].calc_center_median() for i in seen]
print('PATCH faces',len(seen),'area',round(A,1),'x',round(min(c.x for c in cs),1),round(max(c.x for c in cs),1),'y',round(min(c.y for c in cs),1),round(max(c.y for c in cs),1))
bm.free()
at=me.attributes.get('em_ringforce') or me.attributes.new('em_ringforce','FLOAT','FACE')
vals=[0.0]*len(me.polygons); at.data.foreach_get('value',vals)
for i in seen: vals[i]=1.0
at.data.foreach_set('value',vals); me.update()
if os.environ.get('APPLY')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')
else:
    sc=bpy.context.scene
    import sys; sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws5'); import cams
    cams.CAMS.update({'WS10_CAM_eye_walk_from_sign_E':((-80.5,-57.6,136.5),(-50,-54,135.6),28)}); cams.ensure(sc)
    sc.world=bpy.data.worlds['WP2_World_GOLDEN']
    for k in ('MORNING','GOLDEN','OVERCAST'):
        s=bpy.data.objects.get('WP2_Sun_'+k)
        if s: s.hide_render=(k!='GOLDEN')
    b=bpy.data.objects.get('Sun')
    if b: b.hide_render=True
    sc.camera=bpy.data.objects['WS10_CAM_eye_walk_from_sign_E']
    sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.cycles.use_denoising=True
    sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=80
    sc.render.use_border=True; sc.render.use_crop_to_border=True
    sc.render.border_min_x=0.42; sc.render.border_max_x=0.86; sc.render.border_min_y=1-0.26; sc.render.border_max_y=1-0.08
    sc.render.image_settings.file_format='JPEG'; sc.render.threads_mode='FIXED'; sc.render.threads=4
    sc.render.filepath='/workspace/nj-scenes/montclair-state/renders/wip/20261110-0140_ws17_probe_morehead_patch_ringforce.jpg'
    bpy.ops.render.render(write_still=True); print('WROTE')
