# Session pe (Nov 1 2026): Calcia Hall in MAIN -> brick per refs/web/20261101/calcia_web_00..09 (tan/red-brown brick, vertical slot windows, flat roof + thin coping);
# north Calcia brick/slot-window wall shader + coping parapet + 10 RTUs (ortho) ported; stucco parapet band removed; eave ring -> dark coping. REVERT=1 undoes. Sizes/positions UNVERIFIED.
import bpy, os, bmesh, mathutils
NORTH='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
TOP='PE_Calcia_port_20261101pe_UNVERIFIED'; K='pe_calcia_prev'
CAMS={'CAM_eye_calcia_east_windows_as':'PE_CAM_eye_calcia_east','CAM_eye_calcia_west_windows_as':'PE_CAM_eye_calcia_west',
      'CAM_oblique_calcia_windows_as':'PE_CAM_oblique_calcia_from_SE','CAM_closeup_calcia_windows_as':'PE_CAM_closeup_calcia_SE_corner'}
sc=bpy.context.scene
walls=bpy.data.objects['Calcia Hall walls']; roof=bpy.data.objects['Calcia Hall roof (LiDAR)']; skirt=bpy.data.objects['OO_skirt_Calcia Hall walls']
def save(): bpy.ops.wm.save_mainfile()
if os.environ.get('REVERT')=='1':
    top=bpy.data.collections.get(TOP)
    if top:
        def walk(c):
            for ch in list(c.children): walk(ch)
            for o in list(c.objects): bpy.data.objects.remove(o)
            bpy.data.collections.remove(c)
        walk(top)
    for o in bpy.data.objects:
        if o.get(K+'_slots') is not None:
            for s,l in zip(o.material_slots,o[K+'_slots'].split(',')):
                if s.link=='OBJECT' and l=='DATA': s.material=None; s.link='DATA'
            prevm=o.get(K+'_mats')
            if prevm is not None:
                for s,mn in zip(o.material_slots,prevm.split('|')):
                    if s.link=='OBJECT': s.material=bpy.data.materials.get(mn) if mn else None
            del o[K+'_slots']
            if K+'_mats' in o: del o[K+'_mats']
        if o.get(K+'_hidden'): o.hide_render=False; o.hide_viewport=False; del o[K+'_hidden']
        if o.get(K+'_mesh'):
            old=bpy.data.meshes[o[K+'_mesh']]; new=o.data; o.data=old; old.use_fake_user=False; del o[K+'_mesh']
            if new.users==0: bpy.data.meshes.remove(new)
    for mn in ('PE_Calcia_brick_slot_windows_UNVERIFIED','North_wall_Calcia_UNVERIFIED_1958','PE_Calcia_skirt_brick_UNVERIFIED'):
        m=bpy.data.materials.get(mn)
        if m and m.users==0: bpy.data.materials.remove(m)
    save(); print('PE_CALCIA_REVERT_DONE',len(bpy.data.objects)); raise SystemExit
assert TOP not in bpy.data.collections
with bpy.data.libraries.load(NORTH, link=False) as (src,dst):
    dst.collections=['Calcia_20261014c']; dst.objects=list(CAMS); dst.materials=['North_wall_Calcia_UNVERIFIED_1958']
top=bpy.data.collections.new(TOP); sc.collection.children.link(top)
for c in dst.collections: top.children.link(c)
for o in dst.objects: o.name=CAMS[o.name]; top.objects.link(o)
wtop=max((walls.matrix_world@v.co).z for v in walls.data.vertices); dz=wtop-148.98; print('DZ',round(dz,3))
for c in dst.collections:
    for o in c.all_objects: o.location.z+=dz; o['pe_dz']=dz
brick=bpy.data.materials['North_wall_Calcia_UNVERIFIED_1958']; brick.name='PE_Calcia_brick_slot_windows_UNVERIFIED'
nt=brick.node_tree.nodes
nt['Math.001'].inputs[1].default_value=2.4; nt['Math.002'].inputs[1].default_value=0.75; nt['Math.004'].inputs[1].default_value=0.9  # narrow vertical slots (refs 05/07)
b=nt['Brick Texture']; b.inputs['Color1'].default_value=(0.36,0.21,0.14,1); b.inputs['Color2'].default_value=(0.31,0.18,0.12,1); b.inputs['Mortar'].default_value=(0.45,0.42,0.38,1)
dark=bpy.data.materials['PE_Dickson_coping_dark_bronze_UNVERIFIED']
def setslots(o,mats):
    o[K+'_slots']=','.join(s.link for s in o.material_slots); o[K+'_mats']='|'.join((s.material.name if s.material else '') for s in o.material_slots)
    for i,m in mats.items(): s=o.material_slots[i]; s.link='OBJECT'; s.material=m
setslots(walls,{0:brick})
setslots(roof,{1:dark,2:dark})
# skirt: brick copy reading the skirt's own UV
sb=brick.copy(); sb.name='PE_Calcia_skirt_brick_UNVERIFIED'
for n in sb.node_tree.nodes:
    if n.type=='UVMAP': n.uv_map='UVMap'
setslots(skirt,{0:sb})
o=bpy.data.objects['Roof_parapet']; old=o.data; new=old.copy(); new.name=old.name+'_pe_calcia'
bm=bmesh.new(); bm.from_mesh(new); mw=o.matrix_world
kill=[f for f in bm.faces if (lambda c:(-108.6<c.x<-74.9 and 141.9<c.y<220.9))(mw@f.calc_center_median())]
bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(new); bm.free(); print('PARAPET removed',len(kill))
old.use_fake_user=True; o[K+'_mesh']=old.name; o.data=new
for nm in [n for n in bpy.data.objects.keys() if n.startswith(('ek coping caps Calcia','el coping strips Calcia','OR_skirt_win_Calcia'))]:
    ob=bpy.data.objects[nm]; ob[K+'_slots']=','.join(s.link for s in ob.material_slots); ob[K+'_mats']='|'.join((s.material.name if s.material else '') for s in ob.material_slots)
    ob.hide_render=True; ob.hide_viewport=True; ob[K+'_hidden']=1; print('HID',nm[:40])
save(); print('PE_CALCIA_APPLY_DONE',len(bpy.data.objects))
