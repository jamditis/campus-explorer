import bpy,os,math
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for o in list(bpy.data.objects):
    if o.type=='CAMERA': bpy.data.objects.remove(o)
def gz(x,y):
    ok,loc,*_=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1))); return loc.z if ok else 125
sd=bpy.data.lights.new('sun','SUN'); sd.energy=4; so=bpy.data.objects.new('sun',sd); so.rotation_euler=(math.radians(60),0,math.radians(220)); sc.collection.objects.link(so)
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.5,0.6,0.8,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.8
sc.render.engine='CYCLES'; sc.cycles.samples=12; sc.cycles.device='CPU'; sc.render.resolution_x=640; sc.render.resolution_y=360
specs=[('lane_from_S',(-227,-134),(-229,-96),28,1.7,0.5),('closeup_lane',(-226.2,-130.5),(-228.6,-117),30,1.5,0.0),('grandstand_lawn_SE',(-232,-138),(-248,-118),28,1.7,0.5)]
for nm,e,t,lens,h,th in specs:
    c=bpy.data.cameras.new(nm); c.lens=lens; c.clip_end=2000; o=bpy.data.objects.new(nm,c); sc.collection.objects.link(o)
    E=Vector((e[0],e[1],gz(*e)+h)); T=Vector((t[0],t[1],gz(*t)+th)); o.location=E; o.rotation_euler=(T-E).to_track_quat('-Z','Y').to_euler()
    sc.camera=o; sc.render.filepath='/workspace/nj-scenes/montclair-state/renders/test/ws82L_'+os.environ.get('TAG','x')+'_'+nm+'.jpg'; sc.render.image_settings.file_format='JPEG'
    bpy.ops.render.render(write_still=True); print('WROTE',sc.render.filepath,flush=True)
