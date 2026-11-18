# pw (Nov 2 2026): faint run-off/drip staining under each Dickson window sill (197 pv2 openings). ALL UNVERIFIED (no photo;
# typical weathering on buff brick under cast-stone sills). One decal per opening, 3 mm proud of the wall face, top tucked 1 cm
# behind the pu sill, seeded length 0.45-0.9 m, streak alpha from stretched noise x vertical fade; shadows off.
# New object PW_Dickson_sill_drip_stains_UNVERIFIED + material; REVERT=1 removes both.
import bpy, bmesh, os, random
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='PW_Dickson_sill_drip_stains_UNVERIFIED'; MN='PW_sill_drip_stain_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m2=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m2); print('REVERTED_PW_DRIPS')
if REV:
    m=bpy.data.materials.get(MN)
    if m and m.users==0: bpy.data.materials.remove(m)
else:
    rv=bpy.data.objects['PV2_Dickson_window_reveals_glass_UNVERIFIED']; mw=rv.matrix_world; V=[mw@v.co for v in rv.data.vertices]
    rnd=random.Random(202611022); bm=bmesh.new(); uvl=bm.loops.layers.uv.new('UVMap'); nd=0
    for s in range(len(V)//40):
        A,B,C,D=V[40*s+16:40*s+20]; R0=V[40*s+0]   # reveal quad 0 starts at the wall-face corner A
        bc=sum(V[40*s+20:40*s+24],Vector())/4; gc=(A+B+C+D)/4; n=(gc-bc).normalized()
        ex=B-A; W=ex.length; eu=ex/W; ev=(D-A).normalized()
        face=R0+n*0.003                                  # wall-face corner (u0,v0) + 3 mm
        L=rnd.uniform(0.45,0.9); top=face-ev*0.13; seed=rnd.uniform(0,100)
        p0=top-eu*0.08; p1=top+eu*(W+0.08); p2=p1-ev*L; p3=p0-ev*L
        vs=[bm.verts.new(p) for p in (p3,p2,p1,p0)]; f=bm.faces.new(vs)
        for lp,(u,v) in zip(f.loops,((seed,0),(seed+1,0),(seed+1,1),(seed,1))): lp[uvl].uv=(u,v)
        nd+=1
    m2=bpy.data.meshes.new(ON); bm.to_mesh(m2); bm.free()
    m=bpy.data.materials.get(MN)
    if m is None:
        m=bpy.data.materials.new(MN); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']; L_=nt.links.new
        b.inputs['Base Color'].default_value=(0.16,0.13,0.10,1); b.inputs['Roughness'].default_value=0.95
        tc=nt.nodes.new('ShaderNodeTexCoord'); sx=nt.nodes.new('ShaderNodeSeparateXYZ'); L_(tc.outputs['UV'],sx.inputs[0])
        cmb=nt.nodes.new('ShaderNodeCombineXYZ'); mu=nt.nodes.new('ShaderNodeMath'); mu.operation='MULTIPLY'; mu.inputs[1].default_value=22.0
        L_(sx.outputs['X'],mu.inputs[0]); L_(mu.outputs[0],cmb.inputs['X']); mv=nt.nodes.new('ShaderNodeMath'); mv.operation='MULTIPLY'; mv.inputs[1].default_value=0.8
        L_(sx.outputs['Y'],mv.inputs[0]); L_(mv.outputs[0],cmb.inputs['Y'])
        nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=1.0; nz.inputs['Detail'].default_value=4.0; L_(cmb.outputs[0],nz.inputs['Vector'])
        cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position=0.36; cr.color_ramp.elements[1].position=0.62; L_(nz.outputs['Fac'],cr.inputs['Fac'])
        # vertical fade: strong at the sill (v=1), gone at the bottom (v=0), plus soft side fade
        pw=nt.nodes.new('ShaderNodeMath'); pw.operation='POWER'; pw.inputs[1].default_value=1.5; L_(sx.outputs['Y'],pw.inputs[0])
        fx=nt.nodes.new('ShaderNodeMath'); fx.operation='PINGPONG'; fx.inputs[1].default_value=0.5; L_(sx.outputs['X'],fx.inputs[0])
        fs=nt.nodes.new('ShaderNodeMapRange'); fs.inputs['From Max'].default_value=0.12; L_(fx.outputs[0],fs.inputs['Value'])
        m1=nt.nodes.new('ShaderNodeMath'); m1.operation='MULTIPLY'; L_(cr.outputs['Color'],m1.inputs[0]); L_(pw.outputs[0],m1.inputs[1])
        m2_=nt.nodes.new('ShaderNodeMath'); m2_.operation='MULTIPLY'; L_(m1.outputs[0],m2_.inputs[0]); L_(fs.outputs['Result'],m2_.inputs[1])
        m3=nt.nodes.new('ShaderNodeMath'); m3.operation='MULTIPLY'; m3.inputs[1].default_value=0.6; L_(m2_.outputs[0],m3.inputs[0])
        L_(m3.outputs[0],b.inputs['Alpha'])
    m2.materials.append(m)
    o=bpy.data.objects.new(ON,m2); o.visible_shadow=False; o['source_note']='UNVERIFIED: sill drip staining invented (pw, Nov 2 2026)'
    rv.users_collection[0].objects.link(o); print('PW_DRIPS',nd)
