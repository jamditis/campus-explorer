# ws188: memory-safe merge helper. Disables viewport eval of the far-field skirt_under_* GN stack
# on Context_skirt_3DEP_ortho_4km right after load (load_post, before depsgraph eval), and restores it before save.
import bpy, os
from bpy.app.handlers import persistent
SK='Context_skirt_3DEP_ortho_4km'
_OFF=[]
def hwm():
    for l in open('/proc/self/status'):
        if l.startswith(('VmHWM','VmRSS')): print('MEM188',l.strip(),flush=True)
@persistent
def _off(*a):
    o=bpy.data.objects.get(SK)
    if not o: print('SKIRT188 object missing',flush=True); return
    for m in o.modifiers:
        if 'skirt_under' in m.name and m.show_viewport:
            m.show_viewport=False; _OFF.append(m.name)
    print('SKIRT188 OFF',len(_OFF),_OFF,flush=True); hwm()
def restore():
    o=bpy.data.objects.get(SK)
    for n in _OFF: o.modifiers[n].show_viewport=True
    print('SKIRT188 RESTORED',len(_OFF),flush=True)
bpy.app.handlers.load_post.append(_off)
