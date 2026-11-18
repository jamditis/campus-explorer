# ws175c: UNIFY #82 — the diagonal light/dark bands on the front yards S of Normal Ave W are NOT geometry: the lawn shaders
# (COLE_lawn_post2020_bs on the lip, WS172_lawn_fade on the front yards) carry deliberate mowing-stripe terms
# (MULTIPLY(sin(1.745*(-0.391x+0.921y)), 0.13), period 3.6 m, plus a second sine term x0.10) meant for campus turf.
# Private front yards are not striped in one continuous diagonal across property lines, so the residential S-side lawn meshes
# get copies with every sine-stripe amplitude set to 0 (all else identical). Campus lawns keep their stripes.
import bpy
SRCN=('COLE_lawn_post2020_bs','WS172_lawn_fade')
def nostripe(src):
    nm=src.name+'_nostripe_WS175'
    m=bpy.data.materials.get(nm)
    if m: return m
    m=src.copy(); m.name=nm; nt=m.node_tree
    for l in list(nt.links):
        fn,tn=l.from_node,l.to_node
        if fn.bl_idname=='ShaderNodeMath' and fn.operation=='SINE' and tn.bl_idname=='ShaderNodeMath' and tn.operation=='MULTIPLY':
            for i in tn.inputs:
                if not i.is_linked and abs(i.default_value)>1e-6: print('STRIPE175',nm,tn.name,i.default_value,'-> 0',flush=True); i.default_value=0.0
    return m
k=0
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith(('WS172_frontyards_S_of_NormalAve_W','WS163_walk_back_lawn_lip_S')):
        for j,ms in enumerate(o.data.materials):
            if ms and ms.name in SRCN: o.data.materials[j]=nostripe(ms); k+=1
print('STRIPE175 slots',k,flush=True)
