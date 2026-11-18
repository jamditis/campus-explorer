# Session ej: SCM roof 35-deg hip tile rings rendered grey (roofc alpha < 0.02 -> membrane branch).
# Ortho2020 at those faces: 65% red-ish area (same as Morehead's red rings, 64%), so make SCM's ring
# faces (geometry normal z 0.70-0.93) consistent red clay tile: roofc alpha -> 1 on their vertices.
# Original alpha in point attr ej_orig_a. SAVE=1 saves; REVERT=1 restores. Life Hall left alone (ortho 16% red).
import bpy, os
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
o=bpy.data.objects['School of Communication and Media roof (LiDAR)']; me=o.data
a=me.attributes['roofc']; print('roofc',a.domain,a.data_type)
if REVERT:
    oa=me.attributes['ej_orig_a']
    for i,d in enumerate(oa.data):
        c=list(a.data[i].color); c[3]=d.value; a.data[i].color=c
    me.attributes.remove(oa); print('REVERTED')
else:
    assert a.domain=='POINT'
    oa=me.attributes.get('ej_orig_a') or me.attributes.new('ej_orig_a','FLOAT','POINT')
    a=me.attributes['roofc']; oa=me.attributes['ej_orig_a']
    for i in range(len(me.vertices)): oa.data[i].value=a.data[i].color[3]
    n3=o.matrix_world.to_3x3(); vs=set(); low=0; nf=0
    for p in me.polygons:
        nz=(n3@p.normal).normalized().z
        if 0.70<=nz<0.93: nf+=1; vs.update(p.vertices)
    for v in vs:
        c=list(a.data[v].color)
        if c[3]<0.02: low+=1
        c[3]=1.0; a.data[v].color=c
    print('ring faces',nf,'verts',len(vs),'previously grey',low)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
