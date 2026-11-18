# Session eg (Oct 21 2026 ~8:45 PM ET): the "moss slashes" under Life Hall's SW eave (junction WIP, open since ec) are faces of
# 'Eave drip / moss streaks on stucco (3g)' on the Life Hall gable wall under the raking eave (tree-skipping ray probe
# data/eg/probe_slash_eg.py: hits at x 29-35, y 5.7-7.0, z 144.3-144.7 on Life Hall walls + decal). On the sloped gable the
# straight drip strip reads as dark diagonal slashes. Faces with centres in the box x 27..37, y 4.5..8.0, z 143.0..145.6 get the
# transparent EC_decal_hidden slot. Orig material index in face attribute eg_orig_mat. Run after the ec decal script. SAVE/REVERT.
import bpy, os
from mathutils import Vector
o=bpy.data.objects['Eave drip / moss streaks on stucco (3g)']; me=o.data; mw=o.matrix_world
fa=me.attributes.get('eg_orig_mat')
if fa is None:
    fa=me.attributes.new('eg_orig_mat','INT','FACE')
    for p in me.polygons: fa.data[p.index].value=-1
for p in me.polygons:
    if fa.data[p.index].value>=0: p.material_index=fa.data[p.index].value; fa.data[p.index].value=-1
if os.environ.get('REVERT')!='1':
    mat=bpy.data.materials['EC_decal_hidden']
    names=[m.name if m else '' for m in me.materials]
    if mat.name not in names: me.materials.append(mat); names.append(mat.name)
    mi=names.index(mat.name); n=0
    for p in me.polygons:
        c=mw@p.center
        if 27<c.x<37 and 4.5<c.y<8.0 and 143.0<c.z<145.6 and p.material_index!=mi:
            fa.data[p.index].value=p.material_index; p.material_index=mi; n+=1
    print('EG_DECAL hidden',n)
me.update()
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('EG_DECAL_SAVED')
