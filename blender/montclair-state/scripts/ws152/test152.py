import bpy, sys, math
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws152/facade152.py').read())
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc=bpy.context.scene
ring=[(-92.966,-168.958),(-105.022,-220.367),(-90.374,-223.781),(-78.293,-172.383)]
me=bpy.data.meshes.new('pw'); vs=[(x,y,125.0) for x,y in ring]+[(x,y,146.9) for x,y in ring]
me.from_pydata(vs,[],[(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]); me.update()
walls=bpy.data.objects.new('Freeman Hall walls',me); sc.collection.objects.link(walls)
wm=bpy.data.materials.new('wallproxy'); wm.use_nodes=True; wm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.62,0.58,0.47,1); me.materials.append(wm)
g=bpy.data.meshes.new('g'); g.from_pydata([(-200,-300,127.7),(0,-300,127.7),(0,-100,127.7),(-200,-100,127.7)],[],[(0,1,2,3)])
go=bpy.data.objects.new('ground',g); sc.collection.objects.link(go)
gm=bpy.data.materials.new('lawn'); gm.use_nodes=True; gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.09,0.2,0.05,1); g.materials.append(gm)
obs=run(walls=walls)
sun=bpy.data.objects.new('sun',bpy.data.lights.new('sun','SUN')); sun.data.energy=3.0; sun.rotation_euler=(math.radians(50),0,math.radians(-60)); sc.collection.objects.link(sun)
w=bpy.data.worlds.new('w'); w.use_nodes=True; w.node_tree.nodes['Background'].inputs['Color'].default_value=(0.75,0.78,0.82,1); w.node_tree.nodes['Background'].inputs['Strength'].default_value=0.9; sc.world=w
sc.render.engine='CYCLES'; sc.cycles.samples=24; sc.cycles.device='CPU'; sc.render.resolution_x=1024; sc.render.resolution_y=640
sc.view_settings.view_transform='AgX'
mid=(W_N+W_S)/2; u=(W_S-W_N).normalized(); n=Vector((u.y,-u.x))
def cam(name,pos,tgt,lens):
    c=bpy.data.objects.new(name,bpy.data.cameras.new(name)); c.data.lens=lens; c.location=pos
    c.rotation_euler=(Vector(tgt)-Vector(pos)).to_track_quat('-Z','Y').to_euler(); sc.collection.objects.link(c); return c
shots=[('eye_W_2019match',(mid.x+n.x*62-u.x*6,mid.y+n.y*62-u.y*6,129.3),(mid.x,mid.y,136.5),30),
       ('closeup_W_pier_brick',(mid.x+n.x*4.5+u.x*10,mid.y+n.y*4.5+u.y*10,129.4),(mid.x+u.x*11.3,mid.y+u.y*11.3,130.6),35),
       ('closeup_W_doors',(mid.x+n.x*16+u.x*16,mid.y+n.y*16+u.y*16,129.4),(mid.x+u.x*16,mid.y+u.y*16,129.6),28),
       ('closeup_W_bay',(mid.x+n.x*9-u.x*2,mid.y+n.y*9-u.y*2,129.4),(mid.x+u.x*3,mid.y+u.y*3,133.5),24)]
out=sys.argv[sys.argv.index('--')+1]
for nm,p,t,l in shots:
    sc.camera=cam(nm,p,t,l); sc.render.filepath=out+'_'+nm+'.jpg'; sc.render.image_settings.file_format='JPEG'
    bpy.ops.render.render(write_still=True); print('WROTE',sc.render.filepath)
bpy.ops.wm.save_as_mainfile(filepath=M+'scripts/ws152/test152_facade.blend')
