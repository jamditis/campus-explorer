import bpy, os
# oc: + for 1F cutaway cams (no '2F' in the name) the OA/OB 2F furniture is hidden too (ob planter leaves stick out past y 14.1, so the nt bbox rule missed them and they floated over the 1F).
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
_oc=[]
if any('cutaway' in c and '2F' not in c for c in _cn):
    for o in bpy.data.objects:
        if o.name.startswith(('OA 2F','OB 2F')) and not o.hide_render: o.hide_render=True; _oc.append(o)
    print('OC 2F furniture hidden',len(_oc))
exec(NX)
for o in _oc: o.hide_render=False
