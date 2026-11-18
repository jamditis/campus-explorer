# oh: third part of the sawtooth fix: the 'roofc' POINT colour (ortho-sampled) is grey on many mansard verts outside the deck
# (the ortho saw the grey membrane at those xy). For verts used only by em_ringforce=1 faces, replace grey roofc with the median
# red tile roofc of the same band. Original kept in 'oh_roofc_orig' (REVERT=1 restores and removes it).
import bpy, os, sys, statistics as st
REV=os.environ.get('REVERT')=='1'
me=bpy.data.objects['Schmitt Hall roof (LiDAR)'].data
rc=me.attributes['roofc']; org=me.attributes.get('oh_roofc_orig')
if org:
    for i,d in enumerate(org.data): rc.data[i].color=d.color
    me.attributes.remove(org); rc=me.attributes['roofc']
if not REV:
    rf=me.attributes['em_ringforce']; ring=set(); inner=set()
    for p in me.polygons:
        (ring if rf.data[p.index].value>0.5 else inner).update(p.vertices)
    only=ring  # oh v2: include verts shared with inner (deck-covered) faces; shared grey verts made the sawtooth via interpolation
    me.attributes.new('oh_roofc_orig','FLOAT_COLOR','POINT'); org=me.attributes['oh_roofc_orig']; rc=me.attributes['roofc']
    for i,d in enumerate(rc.data): org.data[i].color=d.color
    red=[tuple(rc.data[i].color) for i in only if rc.data[i].color[0]>1.35*rc.data[i].color[1]]
    med=tuple(st.median(c[k] for c in red) for k in range(4))
    n=0
    for i in only:
        c=rc.data[i].color
        if not c[0]>1.35*c[1]:
            rc.data[i].color=(med[0],med[1],med[2],c[3]); n+=1
    print('ring-only verts',len(only),'red',len(red),'recoloured',n,'median',[round(x,3) for x in med])
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
