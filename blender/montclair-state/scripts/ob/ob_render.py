import bpy, os
# oa: ny/nx render chain. For cams with '2F' in the name (render-time only): the nt cutaway hides keep the 2F hallway slab, its
# N/S walls, the balcony rail and the OA furniture (nt hides everything standing on the 2F over the 1F open floor otherwise).
_cn=os.environ['CAMS'].split(',')
NT=open('scripts/nt/nt_render.py').read()
if any('2F' in c for c in _cn):
    b="'NG 2F hallway slab',"; assert NT.count(b)==1; NT=NT.replace(b,"",1)   # (oa fix: do this BEFORE inserting the keep list, which also names the slab)
    a="lo[2]>141.3: _nt.append(o)"; assert a in NT
    NT=NT.replace(a,"lo[2]>141.3 and not o.name.startswith(('OA 2F','OB 2F','NG 2F hallway slab','NG 2F hallway S wall','NG 2F hallway N wall','NG east balcony','NP 2F east balcony','NP horn-strobe 2F hallway')): _nt.append(o)")
NU=open('scripts/nu/nu_render.py').read().replace("exec(open('scripts/nt/nt_render.py').read())","exec(NT)")
NX=open('scripts/nx/nx_render.py').read().replace("exec(open('scripts/nu/nu_render.py').read())","exec(NU)")
exec(NX)
