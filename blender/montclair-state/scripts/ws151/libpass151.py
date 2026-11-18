# ws150 LOW-MEMORY main edit path: append every datablock of main into an empty session WITHOUT making its scene
# active (no depsgraph evaluation -> no GN/modifier memory), apply the mesh-data fixes, save a full copy.
import bpy, resource, os, sys
M='/workspace/nj-scenes/montclair-state/'
SRC=os.environ.get('SRC',M+'montclair_state.blend'); OUT=os.environ.get('OUT',M+'montclair_state_ws151L.blend')
def rss():
    for l in open('/proc/self/status'):
        if l.startswith('VmRSS'): return int(l.split()[1])//1024
bpy.ops.wm.read_factory_settings(use_empty=True)
tmp=bpy.context.window.scene if bpy.context.window else bpy.data.scenes[0]; tmp.name='__tmp150'
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
print("LIB151 empty rss",rss(), [(a,len(getattr(bpy.data,a))) for a in ('scenes','objects','meshes','materials','worlds','workspaces','screens') ])
SKIP={'window_managers','workspaces','screens'}
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    cnt={}
    for a in dir(src):
        if a.startswith('_') or a in SKIP: continue
        v=getattr(src,a)
        if isinstance(v,list): setattr(dst,a,list(v)); cnt[a]=len(v)
print("LIB151 SRC_COUNTS",sorted(cnt.items()))
print("LIB151 appended rss",rss(),"peak",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
SCN=[s for s in bpy.data.scenes if s.name!='__tmp150'][0]
print("LIB151 scene",SCN.name,"objs",len(SCN.objects),"cam",SCN.camera.name if SCN.camera else None, "world",SCN.world.name if SCN.world else None)
if os.environ.get('FIX','1')=='1':
    exec(open(M+'scripts/ws151/fix151.py').read())
print("LIB151 fixed rss",rss())
if bpy.context.window: bpy.context.window.scene=SCN
bpy.data.scenes.remove(tmp)
print("LIB151 scenes now",[s.name for s in bpy.data.scenes])
bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True,compress=True)
print("SAVED_LIB151",OUT,"rss",rss(),"peak",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
