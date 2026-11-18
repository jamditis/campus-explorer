# po (Nov 1 2026): Feliciano flat tier tops -> seamed membrane material (seams 3 m along the building axis, tone/ponding
# patches, darker drain sumps), plus RTUs on curbs + roof drains on the biggest flat tops (clear of hips/edges).
# ALL UNVERIFIED (no roof-equipment source; counts/positions guessed). REVERT=1 restores slot 2 + removes objects.
import bpy, bmesh, os, sys, math, json, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv; OUT=os.environ.get('SAVEAS')
CN='PN_Feliciano_remass_20261101pn_UNVERIFIED'; col=bpy.data.collections[CN]
MN='PO_Feliciano_membrane_seamed_UNVERIFIED'; ON='PO_Feliciano_RTUs_drains_UNVERIFIED'
tiers=[o for o in col.objects if o.name.startswith('PN_Feliciano_tier_')]
# revert
for o in tiers:
    me=o.data
    if 'po_prev_slot2' in me.keys():
        me.materials[2]=bpy.data.materials[me['po_prev_slot2']]; del me['po_prev_slot2']
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
for n in (MN,'PO_RTU_galv_grey_UNVERIFIED'):
    if n in bpy.data.materials: bpy.data.materials.remove(bpy.data.materials[n])
if REV: print('REVERTED_PO')
else:
    th=json.load(open('data/pn/polys.json'))['th']
    # --- membrane material
    m=bpy.data.materials.new(MN); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; Lk=nt.links
    bs=N['Principled BSDF']; bs.inputs['Roughness'].default_value=0.82
    geo=N.new('ShaderNodeNewGeometry'); vr=N.new('ShaderNodeVectorRotate'); vr.rotation_type='Z_AXIS'; vr.inputs['Angle'].default_value=-th
    Lk.new(geo.outputs['Position'],vr.inputs['Vector']); sx=N.new('ShaderNodeSeparateXYZ'); Lk.new(vr.outputs['Vector'],sx.inputs[0])
    def math(op,a,b=None):
        n=N.new('ShaderNodeMath'); n.operation=op
        for i,v in enumerate((a,b)):
            if v is None: continue
            if isinstance(v,(int,float)): n.inputs[i].default_value=v
            else: Lk.new(v,n.inputs[i])
        return n.outputs[0]
    fu=math('FRACT',math('DIVIDE',sx.outputs['X'],3.0))
    seam=math('LESS_THAN',math('ABSOLUTE',math('SUBTRACT',fu,0.5)),0.014)   # 8 cm lap line mid-roll
    fv=math('FRACT',math('DIVIDE',sx.outputs['Y'],12.0)); seam2=math('LESS_THAN',math('ABSOLUTE',math('SUBTRACT',fv,0.5)),0.004)
    sm=math('MAXIMUM',seam,seam2)
    nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.09; nz.inputs['Detail'].default_value=4; Lk.new(geo.outputs['Position'],nz.inputs['Vector'])
    nz2=N.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value=1.7; nz2.inputs['Detail'].default_value=2; Lk.new(geo.outputs['Position'],nz2.inputs['Vector'])
    cr=N.new('ShaderNodeValToRGB'); Lk.new(nz.outputs['Fac'],cr.inputs[0])
    cr.color_ramp.elements[0].position=0.42; cr.color_ramp.elements[0].color=(0.20,0.198,0.192,1)
    cr.color_ramp.elements[1].position=0.62; cr.color_ramp.elements[1].color=(0.34,0.34,0.335,1)
    mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'
    Lk.new(math('MULTIPLY',nz2.outputs['Fac'],0.35),mx.inputs['Factor']); Lk.new(cr.outputs['Color'],mx.inputs[6]); mx.inputs[7].default_value=(0.8,0.8,0.78,1)
    mx2=N.new('ShaderNodeMix'); mx2.data_type='RGBA'; Lk.new(math('MULTIPLY',sm,0.6),mx2.inputs['Factor']); Lk.new(mx.outputs[2],mx2.inputs[6]); mx2.inputs[7].default_value=(0.09,0.09,0.09,1)
    Lk.new(mx2.outputs[2],bs.inputs['Base Color'])
    bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.25; bp.inputs['Distance'].default_value=0.01
    Lk.new(math('ADD',sm,math('MULTIPLY',nz2.outputs['Fac'],0.3)),bp.inputs['Height']); Lk.new(bp.outputs['Normal'],bs.inputs['Normal'])
    for o in tiers:
        me=o.data; me['po_prev_slot2']=me.materials[2].name; me.materials[2]=m
    # --- RTUs + drains on flat tops
    V=[];F=[]
    occ=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and o.visible_get() and ('Feliciano' in o.name or o.name.startswith('PN_'))]
    for o in occ:
        mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]; F+=[[b+i for i in p.vertices] for p in o.data.polygons]
    T=BVHTree.FromPolygons(V,F)

    ux=Vector((__import__('math').cos(th),__import__('math').sin(th),0)); uy=Vector((-ux.y,ux.x,0))
    rng=random.Random(20261101)
    cands=[]
    for o in tiers:
        mw=o.matrix_world; zt=max((mw@v.co).z for v in o.data.vertices)
        xs=[(mw@v.co) for v in o.data.vertices if abs((mw@v.co).z-zt)<0.01]
        if not xs: continue
        mnx=min(p.x for p in xs); mxx=max(p.x for p in xs); mny=min(p.y for p in xs); mxy=max(p.y for p in xs)
        for _ in range(400):
            p=Vector((rng.uniform(mnx,mxx),rng.uniform(mny,mxy),zt))
            h=T.ray_cast(p+Vector((0,0,30)),Vector((0,0,-1)),40)
            if h[0] is None or abs(h[0].z-zt)>0.02: continue
            ok=True   # 8 radial clearance probes: flat top for 3.2 m around, nothing above
            for k in range(8):
                a=k*0.785398
                q=p+(ux*__import__('math').cos(a)+uy*__import__('math').sin(a))*3.2
                hh=T.ray_cast(q+Vector((0,0,30)),Vector((0,0,-1)),40)
                if hh[0] is None or abs(hh[0].z-zt)>0.02: ok=False; break
            if ok: cands.append((zt,p))
    print('CANDS',len(cands))
    # pick spaced units: 1 per ~120 m2 equivalent, min 7 m apart, cap 12
    pick=[]
    for zt,p in cands:
        if all((p-q).length>7.0 for _,q in pick): pick.append((zt,p))
        if len(pick)>=12: break
    bm=bmesh.new()
    def obox(c,w,d,h,mi):
        vs=[]
        for a in (-w/2,w/2):
            for b in (-d/2,d/2):
                for z in (0,h): vs.append(bm.verts.new(c+ux*a+uy*b+Vector((0,0,z))))
        for q in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]: bm.faces.new([vs[i] for i in q]).material_index=mi
    drains=0
    for i,(zt,p) in enumerate(pick):
        if i%3==2:   # roof drain: dark dome on a small sump ring
            obox(p+Vector((0,0,-0.005)),0.7,0.7,0.02,1); obox(p,0.28,0.28,0.09,1); drains+=1; continue
        w,d=(2.6,1.6) if i%2==0 else (1.9,1.3)
        obox(p+Vector((0,0,-0.02)),w+0.3,d+0.3,0.32,0)      # curb (galv)
        obox(p+Vector((0,0,0.30)),w,d,1.05,0)                # cabinet
        obox(p+ux*(w*0.22)+Vector((0,0,1.35)),w*0.38,d*0.7,0.06,1)  # fan deck (dark)
        for s in (-1,1): obox(p+uy*(s*(d/2+0.02))+Vector((0,0,0.55)),w*0.7,0.03,0.5,1)  # louvre panels
        obox(p-ux*(w/2+0.6)+Vector((0,0,0)),1.2,0.25,0.25,0)  # duct/conduit sleeper run
    me=bpy.data.meshes.new(ON); bm.to_mesh(me); bm.free()
    g=bpy.data.materials.new('PO_RTU_galv_grey_UNVERIFIED'); g.use_nodes=True; pb=g.node_tree.nodes['Principled BSDF']
    pb.inputs['Base Color'].default_value=(0.47,0.48,0.48,1); pb.inputs['Metallic'].default_value=0.6; pb.inputs['Roughness'].default_value=0.45
    me.materials.append(g); me.materials.append(bpy.data.materials['Roof_vent_dark_metal'])
    o=bpy.data.objects.new(ON,me); col.objects.link(o)
    print('PO units',len(pick)-drains,'drains',drains,[ (round(z,1)) for z,_ in pick])
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED_AS',OUT)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
