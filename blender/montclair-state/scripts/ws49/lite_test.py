import bpy, runpy, random
from mathutils import Vector
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F,link=False) as (s,d): d.objects=['MID_street_tree_proto_20261015ag']
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/ws49/crown.py')
sc=bpy.context.scene
for o in list(sc.objects): bpy.data.objects.remove(o)
p=bpy.data.objects['MID_street_tree_proto_20261015ag']; random.seed(3)
bpy.ops.mesh.primitive_plane_add(size=400); g=bpy.context.active_object
gm=bpy.data.materials.new('g'); gm.use_nodes=True; gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.06,0.09,0.04,1); g.data.materials.append(gm)
for i in range(30):
    o=p.copy(); o.hide_render=False; o.hide_viewport=False; sc.collection.objects.link(o); s=3.8*random.uniform(.8,1.15); o.scale=(s,s,s*1.15); o.location=(random.uniform(-60,60),random.uniform(0,150),0.8*s); o.rotation_euler=(0,0,random.uniform(0,6.3))
sun=bpy.data.objects.new('sun',bpy.data.lights.new('sun','SUN')); sc.collection.objects.link(sun); sun.rotation_euler=(1.25,0,2.2); sun.data.energy=4; sun.data.color=(1,0.85,0.65)
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.35,0.4,0.5,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.8
c=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(c); sc.camera=c; c.location=(0,-120,60); c.data.lens=50
c.rotation_euler=(Vector((0,70,3))-c.location).to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.render.resolution_x=960; sc.render.resolution_y=540; sc.render.threads_mode='FIXED'; sc.render.threads=4
sc.render.filepath='/workspace/nj-scenes/montclair-state/renders/test/ws49_lite_crowns.png'; bpy.ops.render.render(write_still=True); print('C49 WROTE')
