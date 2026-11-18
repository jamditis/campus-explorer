# Session ec (Oct 21 2026 ~5:45 PM ET): drip/moss decal faces with no wall behind them float as faint streaks in the sky
# (eb junction WIP: thin lines above Life Hall/SCM). Generic: for every decal face, cast from its centre (+2 cm out) back along
# -normal and +normal up to 0.35 m (decal hidden); faces with no surface behind are collapsed to their centre.
# Originals in point attribute ec_orig_pos; REVERT=1 restores. SAVE=1 saves.
import bpy, os
from mathutils import Vector
sc=bpy.context.scene
o=sc.objects['Eave drip / moss streaks on stucco (3g)']; me=o.data; mw=o.matrix_world; inv=mw.inverted(); n3=mw.to_3x3()
if 'ec_orig_pos' not in me.attributes:
    a=me.attributes.new('ec_orig_pos','FLOAT_VECTOR','POINT')
    for v in me.vertices: a.data[v.index].vector=v.co
a=me.attributes['ec_orig_pos']
for v in me.vertices: v.co=a.data[v.index].vector
if 'ec_orig_mat' not in me.attributes:
    fa=me.attributes.new('ec_orig_mat','INT','FACE')
    for p in me.polygons: fa.data[p.index].value=-1
fa=me.attributes['ec_orig_mat']
for p in me.polygons:
    if fa.data[p.index].value>=0: p.material_index=fa.data[p.index].value; fa.data[p.index].value=-1
if os.environ.get('REVERT')!='1':
    o.hide_set(True); dg=bpy.context.evaluated_depsgraph_get()
    kill=[]
    for p in me.polygons:
        c=mw@p.center; nn=(n3@p.normal).normalized()
        ok=False
        for s in (1,-1):
            hit,l,_,_,ob,_=sc.ray_cast(dg,c+nn*0.02*s,-nn*s,distance=0.37)
            if hit: ok=True; break
        if not ok: kill.append(p)
    # hide via a fully transparent material slot (no vertex moves, so neighbouring valid faces stay intact)
    mat=bpy.data.materials.get('EC_decal_hidden') or bpy.data.materials.new('EC_decal_hidden')
    mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); tr=nt.nodes.new('ShaderNodeBsdfTransparent')
    nt.links.new(tr.outputs[0],out.inputs[0])
    if mat.name not in [m.name for m in me.materials if m]: me.materials.append(mat)
    mi=[m.name if m else '' for m in me.materials].index(mat.name)
    for p in kill: fa.data[p.index].value=p.material_index if fa.data[p.index].value<0 else fa.data[p.index].value; p.material_index=mi
    o.hide_set(False)
    print("EC_DRIP faces",len(me.polygons),"collapsed",len(kill))
me.update()
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print("EC_SAVED")
