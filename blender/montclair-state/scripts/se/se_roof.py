# se (Nov 4 2026): Student Center roof detail, ALL UNVERIFIED. Coping trims on L0/L1 edges (LiDAR edge lip ~0.06-0.12 m),
# 2 penthouses from DSM items (~155.5), AHU + small units/fans from DSM blobs (data/se/sc_roof_blobs.json), membrane seam/dirt overlay
# (copy of the membrane material), close-up camera. REVERT=1 removes everything and restores the original material. SAVE=1 saves.
import bpy, bmesh, json, os, math
from mathutils import Vector
C='SE_StudentCenter_roof_detail_UNVERIFIED'; MEM='North_StudentCenter_membrane_UNVERIFIED'; NEWM='SE_SC_membrane_seams_dirt_UNVERIFIED'
L0=[o for o in bpy.data.objects if o.name.startswith('StudentCenter L0_low')][0]; L1=[o for o in bpy.data.objects if o.name.startswith('StudentCenter L1_high')][0]
def revert():
    if MEM not in bpy.data.materials:
        with bpy.data.libraries.load('montclair_state_pre_20261104se.blend',link=False) as (a,b): b.materials=[MEM]
        print('SE_MEM_RESTORED_FROM_BACKUP')
    bpy.data.materials[MEM].use_fake_user=False
    col=bpy.data.collections.get(C)
    if col:
        for o in list(col.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(col)
    for ob in (L0,L1):
        for i,s in enumerate(ob.material_slots):
            if s.material and s.material.name==NEWM: ob.data.materials[i]=bpy.data.materials[MEM]
    for n in (NEWM,'SE_coping_metal_lightgrey_UNVERIFIED','SE_louver_dark_UNVERIFIED'):
        m=bpy.data.materials.get(n)
        if m: bpy.data.materials.remove(m)
    for cn in ('SE_CAM_closeup_SC_roof','SE_CAM_eye_SC_from_N'):
        c=bpy.data.objects.get(cn)
        if c: bpy.data.objects.remove(c,do_unlink=True)
    rc=bpy.data.objects.get('RZ_CAM_eye_SC_from_E')
    if rc and 'se_old' in rc: rc.location=rc['se_old'][:3]; rc.rotation_euler[2]=rc['se_old'][3]; rc.data.lens=rc['se_old'][4]; del rc['se_old']
revert()
if os.environ.get('REVERT')!='1':
    D=json.load(open('data/se/sc_roof_blobs.json'))
    lv=json.load(open('north/data/day_heroes/student_center_levels_20261014.json'))['levels']
    col=bpy.data.collections.new(C); bpy.context.scene.collection.children.link(col)
    def mat(n,c,r,met=0.0):
        m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=r; b.inputs['Metallic'].default_value=met; return m
    MCOP=mat('SE_coping_metal_lightgrey_UNVERIFIED',(0.62,0.62,0.6),0.4,0.35)
    MLOU=mat('SE_louver_dark_UNVERIFIED',(0.08,0.085,0.09),0.6,0.2)
    MW=bpy.data.materials['RZ2_North_SC_precast_ribbed_white']; MG=bpy.data.materials['KM_RTU_housing_galv_UNVERIFIED']; MK=bpy.data.materials['KM_RTU_curb_dark_UNVERIFIED']
    # membrane copy with seams + dirt
    bpy.data.materials[MEM].use_fake_user=True  # keep the original for exact revert
    nm=bpy.data.materials[MEM].copy(); nm.name=NEWM; nt=nm.node_tree; N=nt.nodes; Lk=nt.links
    bsdf=N['Principled BSDF']; src=bsdf.inputs['Base Color'].links[0].from_socket if bsdf.inputs['Base Color'].is_linked else None
    geo=N.new('ShaderNodeNewGeometry'); rot=N.new('ShaderNodeVectorRotate'); rot.rotation_type='Z_AXIS'; rot.inputs['Angle'].default_value=math.radians(-23)
    Lk.new(geo.outputs['Position'],rot.inputs['Vector'])
    sep=N.new('ShaderNodeSeparateXYZ'); Lk.new(rot.outputs['Vector'],sep.inputs[0])
    # seams every 3.05 m (10 ft rolls, UNVERIFIED): frac distance -> thin line
    d=N.new('ShaderNodeMath'); d.operation='DIVIDE'; d.inputs[1].default_value=3.05; Lk.new(sep.outputs['X'],d.inputs[0])
    f=N.new('ShaderNodeMath'); f.operation='PINGPONG'; f.inputs[1].default_value=0.5; Lk.new(d.outputs[0],f.inputs[0])
    s=N.new('ShaderNodeMath'); s.operation='LESS_THAN'; s.inputs[1].default_value=0.02; Lk.new(f.outputs[0],s.inputs[0])
    # dirt: large noise
    nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.09; nz.inputs['Detail'].default_value=6; Lk.new(geo.outputs['Position'],nz.inputs['Vector'])
    mr=N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=0.45; mr.inputs['From Max'].default_value=0.75; mr.inputs['To Min'].default_value=0; mr.inputs['To Max'].default_value=0.5
    Lk.new(nz.outputs['Fac'],mr.inputs['Value'])
    base=N.new('ShaderNodeRGB'); base.outputs[0].default_value=(0.78,0.78,0.76,1)
    m1=N.new('ShaderNodeMix'); m1.data_type='RGBA'; m1.blend_type='MULTIPLY'; m1.inputs['B'].default_value=(0.62,0.6,0.56,1)
    Lk.new(mr.outputs['Result'],m1.inputs['Factor']); Lk.new(src if src else base.outputs[0],m1.inputs['A'])
    m2=N.new('ShaderNodeMix'); m2.data_type='RGBA'; m2.blend_type='MULTIPLY'; m2.inputs['B'].default_value=(0.5,0.5,0.48,1)
    sf=N.new('ShaderNodeMath'); sf.operation='MULTIPLY'; sf.inputs[1].default_value=0.8; Lk.new(s.outputs[0],sf.inputs[0])
    Lk.new(sf.outputs[0],m2.inputs['Factor']); Lk.new(m1.outputs['Result'],m2.inputs['A']); m3=N.new('ShaderNodeMix'); m3.data_type='RGBA'; m3.blend_type='MULTIPLY'; m3.inputs['Factor'].default_value=1.0; m3.inputs['B'].default_value=(0.86,0.86,0.85,1)
    Lk.new(m2.outputs['Result'],m3.inputs['A']); Lk.new(m3.outputs['Result'],bsdf.inputs['Base Color'])
    for ob in (L0,L1):
        for i,sl in enumerate(ob.material_slots):
            if sl.material and sl.material.name==MEM: ob.data.materials[i]=nm
    def add(name,bm,mats):
        me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for m in mats: me.materials.append(m)
        ob=bpy.data.objects.new(name,me); col.objects.link(ob); return ob
    def box(bm,x0,y0,z0,x1,y1,z1,mi=0,ang=0,cx=None,cy=None):
        r=bmesh.ops.create_cube(bm,size=1.0)['verts']
        for v in r:
            v.co=Vector(((v.co.x+.5)*(x1-x0)+x0,(v.co.y+.5)*(y1-y0)+y0,(v.co.z+.5)*(z1-z0)+z0))
        if ang:
            cx=(x0+x1)/2 if cx is None else cx; cy=(y0+y1)/2 if cy is None else cy
            bmesh.ops.rotate(bm,verts=r,cent=(cx,cy,0),matrix=__import__('mathutils').Matrix.Rotation(ang,3,'Z'))
        for fc in {f for v in r for f in v.link_faces}: fc.material_index=mi
    # coping: ribbon 0.30 wide inward, 0.10 above top (LiDAR edge lip p50 +0.06 m) with 2 cm overhang outward
    def bounds(pts):
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]; return min(xs),min(ys),max(xs),max(ys)
    bm=bmesh.new()
    for li in (0,1):
        top=lv[li]['top']; pts=lv[li]['polys'][0]['outer']
        vs=[bm.verts.new((x,y,top-0.04)) for x,y in pts]; f=bm.faces.new(vs); f.normal_update()
        if f.normal.z<0: f.normal_flip()
        r=bmesh.ops.inset_region(bm,faces=[f],thickness=0.30,use_even_offset=True)
        bmesh.ops.delete(bm,geom=[f],context='FACES')
    ex=bmesh.ops.extrude_face_region(bm,geom=list(bm.faces))
    for v in [e for e in ex['geom'] if isinstance(e,bmesh.types.BMVert)]: v.co.z+=0.14
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002); bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    add('SE_SC_roof_coping_L0_L1 (LiDAR edge lip ~+0.06 m; profile UNVERIFIED)',bm,[MCOP])
    # penthouses (DSM items ~155.5 = L1 + ~2.8 m)
    ang=math.radians(-23)
    bm=bmesh.new()
    for li in (2,3):
        x0,y0,x1,y1=bounds(lv[li]['polys'][0]['outer'])
        box(bm,x0,y0,152.75,x1,y1,155.45,0,ang)
        box(bm,x0-0.05,y0-0.05,155.45,x1+0.05,y1+0.05,155.6,1,ang)
        # louver band on the long sides (front), slightly proud
        box(bm,x0+0.6,y0-0.04,153.6,x1-0.6,y0+0.02,154.6,2,ang,(x0+x1)/2,(y0+y1)/2)
        box(bm,x0+0.6,y1-0.02,153.0,x0+1.6,y1+0.04,155.0,3,ang,(x0+x1)/2,(y0+y1)/2)  # door
    add('SE_SC_roof_penthouses x2 (DSM ~155.5; use/type UNVERIFIED)',bm,[MW,MCOP,MLOU,MG])
    # AHU + small units
    bm=bmesh.new(); n=0
    for li,key in ((0,'L0_low'),(1,'L1_high')):
        top=lv[li]['top']
        for b in D[key]['blobs']:
            if b['h']<0.55: continue
            x,y=b['x'],b['y']; n+=1
            if b['cells']>=8:
                w,l=b['x1']-b['x0']-0.8,b['y1']-b['y0']-0.8; hh=min(b['h'],2.0)
                box(bm,x-w/2-0.15,y-l/2-0.15,top,x+w/2+0.15,y+l/2+0.15,top+0.35,1,ang)
                box(bm,x-w/2,y-l/2,top+0.35,x+w/2,y+l/2,top+hh,0,ang)
                for k in range(3): box(bm,x-w/2+0.4+k*(w-0.8)/2-0.45,y+l/2-0.02,top+0.6,x-w/2+0.4+k*(w-0.8)/2+0.45,y+l/2+0.03,top+hh-0.2,2,ang,x,y)
            elif b['h']>=1.0:
                s=0.6+0.25*min(b['cells'],4); hh=min(b['h'],1.6)
                box(bm,x-s/2-0.1,y-s/2-0.1,top,x+s/2+0.1,y+s/2+0.1,top+0.3,1,ang)
                box(bm,x-s/2,y-s/2,top+0.3,x+s/2,y+s/2,top+hh,0,ang)
            else:
                # exhaust fan: curb + mushroom hood
                box(bm,x-0.35,y-0.35,top,x+0.35,y+0.35,top+0.35,1,ang)
                r=bmesh.ops.create_cone(bm,cap_ends=True,segments=16,radius1=0.42,radius2=0.18,depth=0.32)['verts']
                for v in r: v.co+=Vector((x,y,top+0.55))
                for fc in {f for v in r for f in v.link_faces}: fc.material_index=0
    add('SE_SC_roof_units AHU+RTU+fans (DSM blobs; types UNVERIFIED)',bm,[MG,MK,MLOU])
    # roof drains: 2 per L1 bay, UNVERIFIED (generic), as dark discs
    print('SE_UNITS',n)
    cam=bpy.data.cameras.new('SE_CAM_closeup_SC_roof'); cam.lens=30; co=bpy.data.objects.new('SE_CAM_closeup_SC_roof',cam)
    bpy.context.scene.collection.objects.link(co); co.location=(-22,276,171); co.rotation_euler=(math.radians(57),0,math.radians(-42)); cam.lens=35
    cam2=bpy.data.cameras.new('SE_CAM_eye_SC_from_N'); cam2.lens=26; c2=bpy.data.objects.new('SE_CAM_eye_SC_from_N',cam2); bpy.context.scene.collection.objects.link(c2)
    c2.location=(10,372,141.1); c2.rotation_euler=(math.radians(93),0,math.radians(169))
    # (E camera move tried and dropped: (52,285) is also inside scene geometry)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SE_SAVED')
print('SE_SIG',len(bpy.data.objects))
