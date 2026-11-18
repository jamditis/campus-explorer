# ws208 ultra-low-memory merge: disables show_viewport on EVERY modifier of every object at load_post (before any
# depsgraph eval), runs the CHAIN (all fixes use base-mesh BVHs, same as the modifiers-off subset tests), does a cheap
# view_layer.update, then restores every modifier's Realtime bit by DNA poke (no RNA tag -> no re-eval at save), saves.
import bpy, os, ctypes
from bpy.app.handlers import persistent
def hwm():
    for l in open('/proc/self/status'):
        if l.startswith(('VmHWM','VmRSS')): print('MEM208',l.strip(),flush=True)
_OFF=[]
@persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers:
            if m.show_viewport:
                m.show_viewport=False; _OFF.append((o.name,m.name))
    print('OFF208',len(_OFF),flush=True); hwm()
bpy.app.handlers.load_post.append(_off)
def poke_restore():
    n=0
    for on,mn in _OFF:
        m=bpy.data.objects[on].modifiers[mn]; v=ctypes.c_int.from_address(m.as_pointer()+20)
        exp=(1 if m.show_viewport else 0)|(2 if m.show_render else 0)
        if (v.value&3)!=exp: raise SystemExit(f'POKE208 layout mismatch {on}/{mn} mode={v.value} exp={exp}')
        v.value=v.value|1; n+=1
    bad=[(on,mn) for on,mn in _OFF if not bpy.data.objects[on].modifiers[mn].show_viewport]
    print('POKE208 restored',n,'notback',len(bad),flush=True)
    if bad: raise SystemExit('POKE208 restore failed')
S='/workspace/nj-scenes/montclair-state/scripts/'
bpy.ops.wm.open_mainfile(filepath=os.environ.get('INF','/workspace/nj-scenes/montclair-state/montclair_state.blend'))
for f in os.environ['CHAIN'].split():
    exec(open(S+f).read())
bpy.context.view_layer.update(); hwm()
poke_restore(); hwm()
bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True); hwm(); print('SAVED',flush=True)
