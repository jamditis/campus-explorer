# og: Schmitt mansard band outside the 3.0 m membrane deck -> tile-only copy of Roof_tile_or_membrane
# (removes the grey sawtooth where the normal-z switch flips per triangle). REVERT=1 restores.
import bpy, json, os
o=bpy.data.objects['Schmitt Hall roof (LiDAR)']; me=o.data
REV=os.environ.get('REVERT')=='1'
if REV:
    a=me.attributes.get('og_orig_mat')
    if a:
        for p in me.polygons: p.material_index=a.data[p.index].value
        me.attributes.remove(a)
    m=bpy.data.materials.get('Roof_tile_only_schmitt_og')
    if m:
        i=me.materials.find(m.name)
        if i>=0: me.materials.pop(index=i)
        bpy.data.materials.remove(m)
    bpy.ops.wm.save_mainfile(); print('REVERTED'); raise SystemExit
src=bpy.data.materials['Roof_tile_or_membrane']
m=bpy.data.materials.get('Roof_tile_only_schmitt_og') or src.copy(); m.name='Roof_tile_only_schmitt_og'
for n in m.node_tree.nodes:
    if n.type=='MAP_RANGE': n.inputs[1].default_value=2.0; n.inputs[2].default_value=2.1; print('maprange',n.name)
if me.materials.find(m.name)<0: me.materials.append(m)
mi=me.materials.find(m.name)
d=json.load(open('data/og/schmitt_deck_inset3_og.json'))
rings=[pg[0] for pg in d]
def inside(x,y):
    for r in rings:
        n=len(r); j=n-1; ins=False
        for i in range(n):
            xi,yi=r[i]; xj,yj=r[j]
            if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi: ins=not ins
            j=i
        if ins: return True
    return False
a=me.attributes.get('og_orig_mat') or me.attributes.new('og_orig_mat','INT','FACE')
mw=o.matrix_world; c=0
for p in me.polygons:
    a.data[p.index].value=a.data[p.index].value if p.material_index==mi else p.material_index
    if p.material_index in (0,mi):
        w=mw@p.center
        if not inside(w.x,w.y): p.material_index=mi; c+=1
print('tile faces',c,'of',len(me.polygons))
bpy.ops.wm.save_mainfile(); print('SAVED')
