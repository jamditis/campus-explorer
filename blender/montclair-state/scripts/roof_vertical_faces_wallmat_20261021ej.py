# Session ej: vertical faces (|nz|<0.35) of LiDAR roof meshes that use the shared roof material
# (parapet/step walls, high-bay sides) get the building's wall material instead of ribbed roofing.
# Face attr ej_orig_mi keeps the original material index. SAVE=1 saves; REVERT=1 restores.
import bpy, os
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
ROOF='Roof_tile_or_membrane'; NZ=0.35
tot=0
SKIPB=('Schmitt Hall','University Hall')
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.endswith(' roof (LiDAR)') or o.name.startswith(SKIPB): continue
    me=o.data
    if REVERT:
        a=me.attributes.get('ej_orig_mi')
        if a:
            for p in me.polygons:
                v=a.data[p.index].value
                if v>=0: p.material_index=v
            me.attributes.remove(a); print('REVERTED',o.name)
        continue
    mats=[s.material.name if s.material else '' for s in o.material_slots]
    if ROOF not in mats: continue
    bname=o.name[:-len(' roof (LiDAR)')]
    w=bpy.data.objects.get(bname+' walls')
    if not w or not w.material_slots or not w.material_slots[0].material: print('SKIP no walls',o.name); continue
    wm=w.material_slots[0].material
    added=wm.name not in mats
    if not added: wi=mats.index(wm.name)
    else: me.materials.append(wm); wi=len(me.materials)-1
    n3=o.matrix_world.to_3x3()
    a=me.attributes.get('ej_orig_mi') or me.attributes.new('ej_orig_mi','INT','FACE')
    n=0;area=0
    for p in me.polygons:
        a.data[p.index].value=-1
        if p.material_index<len(mats) and mats[p.material_index]==ROOF:
            nz=(n3@p.normal).normalized().z
            if abs(nz)<NZ:
                a.data[p.index].value=p.material_index; p.material_index=wi; n+=1; area+=p.area
    if n==0:
        me.attributes.remove(a)
        if added: me.materials.pop()
        continue
    tot+=n; print('SET',o.name,'->',wm.name,n,'faces',round(area,1),'m2')
print('TOTAL',tot)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
