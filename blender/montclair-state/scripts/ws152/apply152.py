# ws152 apply: Freeman W/E façades into a loaded main (or ws151b). Run inside Blender with the scene open.
import bpy, resource
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws152/facade152.py').read())
walls=bpy.data.objects.get('Freeman Hall walls')
print('FACADE152 walls', walls and (walls.type, len(walls.data.vertices)))
fre=[o.name for o in bpy.data.objects if 'freeman' in o.name.lower()]
print('FACADE152 freeman objs',len(fre))
obs=run(walls=walls)
# report Freeman meshes NOT retired that still sit within 0.5 m of either façade plane (possible poke-through under the overlay)
for o in bpy.data.objects:
    if 'freeman' in o.name.lower() and o.type=='MESH' and not o.hide_render and not o.name.startswith('WS152'):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        for N,S,sg in [(W_N,W_S,1),(E_N,E_S,-1)]:
            u=(S-N).normalized(); n=Vector((u.y,-u.x))*sg
            if max((p.xy-N).dot(n) for p in bb)>0.035 and min((p.xy-N).dot(n) for p in bb)<0.5 and max(p.z for p in bb)>129:
                print('FACADE152 CHECK near-plane kept:',o.name,round(max((p.xy-N).dot(n) for p in bb),3)); break
# review cameras (ground ~127.3–128.1 on the W lawn, 126–127.5 on the E/Lot 9 side)
mid=(W_N+W_S)/2; u=(W_S-W_N).normalized(); n=Vector((u.y,-u.x))
T=bpy.data.objects.get('Terrain_LiDAR_DTM_1m')
def gz(x,y,dflt):
    if not T: return dflt
    mi=T.matrix_world.inverted(); ok,loc,_,_=T.ray_cast(mi@Vector((x,y,300)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
    return (T.matrix_world@loc).z if ok else dflt
def cam(name,pos,tgt,lens,eye=None):
    if eye is not None: pos=(pos[0],pos[1],gz(pos[0],pos[1],pos[2]-eye)+eye)
    c=bpy.data.objects.get(name) or bpy.data.objects.new(name,bpy.data.cameras.new(name)); c.data.lens=lens; c.location=pos
    c.rotation_euler=(Vector(tgt)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
    if c.name not in bpy.context.scene.collection.objects: bpy.context.scene.collection.objects.link(c)
cam('WS152_CAM_eye_Freeman_W_facade_2019match',(mid.x+n.x*62-u.x*6,mid.y+n.y*62-u.y*6,129.4),(mid.x,mid.y,136.5),30,1.7)
cam('WS152_CAM_closeup_Freeman_W_bay',(mid.x+n.x*9-u.x*2,mid.y+n.y*9-u.y*2,129.6),(mid.x+u.x*3,mid.y+u.y*3,133.5),24,1.6)
cam('WS152_CAM_oblique_Freeman_from_SW',(-150,-262,160),(-95,-200,137),28)
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws152f.blend',copy=True)
print('SAVED_WS152F RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
