# ws194 low-memory WIP render: far-field skirt (Context_skirt_3DEP_ortho_4km + its skirt_under GN stack, ~5 GB of the 8.2 GB peak)
# excluded from the render; everything else as render193.py.
import bpy
o=bpy.data.objects.get('Context_skirt_3DEP_ortho_4km')
if o:
    o.hide_render=True
    for m in o.modifiers: m.show_render=False; m.show_viewport=False
    print('LM194 skirt hidden',flush=True)
exec(compile(open('/workspace/nj-scenes/montclair-state/scripts/ws193/render193.py').read(),'render193','exec'))
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM194',l.strip(),flush=True)
