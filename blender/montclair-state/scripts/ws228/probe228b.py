# ws228: run fix228a (FIX env) in memory, then per-modifier evaluated face counts + VmHWM (SELF_REVIEW ws227 Q)
import bpy,sys,os
S='/workspace/nj-scenes/montclair-state/scripts/ws228/'
def hwm(tag):
    for l in open('/proc/self/status'):
        if l.startswith('VmHWM'): print('P228D',tag,l.strip(),flush=True)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
print('P228D before v/f',len(t.data.vertices),len(t.data.polygons),flush=True)
for f in os.environ.get('FIX','').split(): exec(open(S+f).read())
print('P228D after v/f',len(t.data.vertices),len(t.data.polygons),flush=True); hwm('fix')
for m in t.modifiers:
    m.show_viewport=m.show_render
    if not m.show_render: continue
    dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh(); nn=(len(me.vertices),len(me.polygons)); e.to_mesh_clear()
    print('P228D mod',m.name,nn,flush=True); hwm(m.name)
sys.stdout.flush(); os._exit(0)
