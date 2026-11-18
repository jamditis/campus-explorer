# Session pe (Nov 1 2026): port the north Dickson Hall detail into MAIN + buff brick walls + flat-roof coping. REVERT=1 undoes. ALL UNVERIFIED except brick/window rhythm/entrance per refs dickson_commons_2007 + mref_04.
import bpy, os, mathutils
NORTH='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
TOP='PE_Dickson_port_20261101pe_UNVERIFIED'
COLLS=['North_Dickson_windows_20261014d','North_Dickson_entry_20261014b','DK_pier_accents_20261015aq']
CAMS={'CAM_eye_dickson_mref04':'PE_CAM_eye_dickson_east_entrance','CAM_oblique_dickson_windows_aq':'PE_CAM_oblique_dickson_from_SW',
      'CAM_eye_dickson_south_windows_aq':'PE_CAM_eye_dickson_south','CAM_closeup_dickson_windows':'PE_CAM_closeup_dickson_east_windows','CAM_eye_dickson_west_windows_aq':'PE_CAM_eye_dickson_west'}
sc=bpy.context.scene
walls=bpy.data.objects['Dickson Hall walls']; roof=bpy.data.objects['Dickson Hall roof (LiDAR)']
def save(): bpy.ops.wm.save_mainfile()
if os.environ.get('REVERT')=='1':
    top=bpy.data.collections.get(TOP)
    if top:
        def walk(c):
            for ch in list(c.children): walk(ch)
            for o in list(c.objects): bpy.data.objects.remove(o)
            bpy.data.collections.remove(c)
        walk(top)
    for o in (walls,roof):
        prev=o.get('pe_prev_slots')
        if prev is not None:
            for s in o.material_slots:
                if s.link=='OBJECT': s.material=None
                s.link='DATA'
            del o['pe_prev_slots']
    for o in bpy.data.objects:
        if o.get('pe_prev_mesh'):
            old=bpy.data.meshes[o['pe_prev_mesh']]; new=o.data; o.data=old; old.use_fake_user=False
            for sl in o.material_slots:
                if sl.link=='OBJECT': sl.material=None
                sl.link='DATA'
            del o['pe_prev_mesh']
            if new.users==0: bpy.data.meshes.remove(new)
    for o in (roof,):
        pass
    for mn in ('PE_Dickson_coping_dark_bronze_UNVERIFIED','PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED','North_wall_Dickson_brick_buff'):
        m=bpy.data.materials.get(mn)
        if m and m.users==0: bpy.data.materials.remove(m)
    save(); print('PE_REVERT_DONE',len(bpy.data.objects)); raise SystemExit
assert TOP not in bpy.data.collections, 'already applied'
with bpy.data.libraries.load(NORTH, link=False) as (src,dst):
    dst.collections=[c for c in COLLS if c in src.collections]
    dst.objects=[c for c in CAMS if c in src.objects]
    dst.materials=[m for m in ['North_wall_Dickson_brick_buff'] if m in src.materials]
top=bpy.data.collections.new(TOP); sc.collection.children.link(top)
for c in dst.collections: top.children.link(c)
for o in dst.objects:
    o.name=CAMS[o.name]; top.objects.link(o)
# drop walk pads onto the MAIN LiDAR roof
dg=bpy.context.evaluated_depsgraph_get()
for c in dst.collections:
    for o in c.all_objects:
        if 'WalkPad' in o.name or 'Roof_Box' in o.name:
            bb=[o.matrix_world@mathutils.Vector(v) for v in o.bound_box]
            zs=[]
            for f in (0.2,0.5,0.8):
                for g in (0.2,0.5,0.8):
                    x=min(v.x for v in bb)*(1-f)+max(v.x for v in bb)*f; y=min(v.y for v in bb)*(1-g)+max(v.y for v in bb)*g
                    hit,loc,n,i,ob,m=sc.ray_cast(dg,(x,y,170),(0,0,-1))
                    if hit and ob and ob.name==roof.name: zs.append(loc.z)
            if zs:
                dz=max(zs)+0.02-min(v.z for v in bb); o.location.z+=dz; o['pe_dz']=dz; print('LIFT',o.name[:30],round(dz,3))
# ground check at the entrance
for (x,y) in [(-131.5,105),(-130.5,110),(-129.6,128)]:
    hit,loc,n,i,ob,m=sc.ray_cast(dg,(x+1.5,y,160),(0,0,-1)); print('GROUND',x,y,round(loc.z,2) if hit else None, ob.name if hit else None)
brick0=bpy.data.materials['North_wall_Dickson_brick_buff']
brick=brick0.copy(); brick.name='PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED'
mx=brick.node_tree.nodes['Mix.002']; fs=mx.inputs[0]
for l in list(fs.links): brick.node_tree.links.remove(l)
fs.default_value=0.0  # photo dickson_commons_2007: no red spandrel panels; red brick only in piers/entry bay (overlays)
brick0.use_fake_user=False; coping=bpy.data.materials['ek_coping_metal']
walls['pe_prev_slots']=','.join(s.link for s in walls.material_slots)
for s in walls.material_slots: s.link='OBJECT'; s.material=brick
roof['pe_prev_slots']=','.join(s.link for s in roof.material_slots)
for idx,m in [(1,coping),(2,coping),(3,brick)]:
    s=roof.material_slots[idx]; s.link='OBJECT'; s.material=m
dark=bpy.data.materials.new('PE_Dickson_coping_dark_bronze_UNVERIFIED'); dark.use_nodes=True
b=dark.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.075,0.065,0.055,1); b.inputs['Metallic'].default_value=0.55; b.inputs['Roughness'].default_value=0.45
import bmesh
for nm in ('ek coping caps Dickson Hall (generic, UNVERIFIED profile)','el coping strips Dickson Hall (generic, UNVERIFIED profile)'):
    o=bpy.data.objects[nm]; old=o.data; new=old.copy(); new.name=old.name+'_pe'
    bm=bmesh.new(); bm.from_mesh(new); mw=o.matrix_world
    kill=[f for f in bm.faces if (lambda c:(c.z<148.0 and c.x<-158.3))(mw@f.calc_center_median())]
    bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(new); bm.free()
    print('COPING',nm[:12],'removed faces',len(kill))
    old.use_fake_user=True; o['pe_prev_mesh']=old.name; o.data=new
    for sl in o.material_slots: sl.link='OBJECT'; sl.material=dark
for idx in (1,2): roof.material_slots[idx].material=dark
# shared campus parapet mesh: the stucco parapet band sat mid-height on Dickson's west face (photo: plain brick, thin dark coping) -> drop its faces inside the Dickson footprint
o=bpy.data.objects['Roof_parapet']; old=o.data; new=old.copy(); new.name=old.name+'_pe'
bm=bmesh.new(); bm.from_mesh(new); mw=o.matrix_world
kill=[f for f in bm.faces if (lambda c:(-183.2<c.x<-129.4 and 76.8<c.y<160.5))(mw@f.calc_center_median())]
bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(new); bm.free(); print('PARAPET removed faces',len(kill))
old.use_fake_user=True; o['pe_prev_mesh']=old.name; o.data=new
save(); print('PE_APPLY_DONE',len(bpy.data.objects))
