# ws189: restore skirt_under show_viewport WITHOUT an RNA update (no depsgraph tag -> no 6 GB eval at save).
# ModifierData DNA: next*, prev*, int type, int mode  -> mode at byte offset 20; eModifierMode_Realtime = 1.
import ctypes, bpy
def poke_restore():
    o=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; n=0
    for name in _OFF:
        m=o.modifiers[name]; addr=m.as_pointer()+20
        v=ctypes.c_int.from_address(addr)
        exp=(1 if m.show_viewport else 0)|(2 if m.show_render else 0)
        if (v.value&3)!=exp: raise SystemExit(f'POKE189 layout mismatch {name} mode={v.value} exp={exp}')
        v.value=v.value|1; n+=1
    print('POKE189 restored',n,'now',[m.show_viewport for m in o.modifiers],flush=True)
