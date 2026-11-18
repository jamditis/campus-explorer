# tq (Nov 5 2026 ~1:45 AM ET, MAIN, day 8 Student Center east edge). ALL UNVERIFIED, reversible (REVERT=1).
# Stone Hall restyled after the 1965/1966 MSU slides (refs/stone/): cream/buff brick in running bond (was plain stucco),
# light aluminium window frames with a transom (2x2 lites), projecting light roof fascia/coping ring on both roof levels.
# Stone-only material copy (Blanton keeps TM_dorm_wall_streaked_UNVERIFIED); original slot kept (fake user) for revert.
import bpy, bmesh, os, json, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
D='/workspace/nj-scenes/montclair-state/'
SRC='TM_dorm_wall_streaked_UNVERIFIED'; NEW='TQ_Stone_buff_brick_UNVERIFIED'; CN='TQ_Stone_fascia_UNVERIFIED'
STONE=['TI_Stone_Hall_313028565_lower_UNVERIFIED','TI_Stone_Hall_313028565_upper0_UNVERIFIED']
def revert():
    for n in STONE:
        o=bpy.data.objects.get(n)
        if o and 'tq_orig_mat' in o:
            for i,s in enumerate(o.material_slots):
                if s.material and s.material.name==NEW: s.material=bpy.data.materials[o['tq_orig_mat']]
            del o['tq_orig_mat']
    for o in bpy.data.objects:
        if 'tq_orig_mesh' in o:
            cur=o.data; o.data=bpy.data.meshes[o['tq_orig_mesh']]; o.data.use_fake_user=False; del o['tq_orig_mesh']; del o['tq_snapped']
            if cur.users==0: bpy.data.meshes.remove(cur)
    for o in [o for o in bpy.data.objects if 'tq_obj' in o]:
        me=o.data; t=o.type; bpy.data.objects.remove(o)
        if me and me.users==0: (bpy.data.meshes if t=='MESH' else bpy.data.cameras).remove(me)
    c=bpy.data.collections.get(CN)
    if c: bpy.data.collections.remove(c)
    for n in (NEW,'TQ_Stone_fascia_paint_UNVERIFIED'):
        m=bpy.data.materials.get(n)
        if m: bpy.data.materials.remove(m)
    print('TQ reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene
src=bpy.data.materials[SRC]; m=src.copy(); m.name=NEW; nt=m.node_tree; N=nt.nodes; L=nt.links
def M(op,a,b=None):
    n=N.new('ShaderNodeMath'); n.operation=op
    for i,v in enumerate((a,b)):
        if v is None: continue
        if isinstance(v,(int,float)): n.inputs[i].default_value=v
        else: L.new(v,n.inputs[i])
    return n.outputs[0]
tc=[n for n in N if n.type=='TEX_COORD'][0]
ad=N.new('ShaderNodeAttribute'); ad.attribute_name='ti_dir'
a0=N.new('ShaderNodeAttribute'); a0.attribute_name='ti_z0'; af=N.new('ShaderNodeAttribute'); af.attribute_name='ti_floor'
sep=N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'],sep.inputs[0])
dp=N.new('ShaderNodeVectorMath'); dp.operation='DOT_PRODUCT'; L.new(tc.outputs['Object'],dp.inputs[0]); L.new(ad.outputs['Vector'],dp.inputs[1])
cmb=N.new('ShaderNodeCombineXYZ'); L.new(dp.outputs['Value'],cmb.inputs[0]); L.new(sep.outputs['Z'],cmb.inputs[1])
br=N.new('ShaderNodeTexBrick'); br.offset=0.5; br.offset_frequency=2; br.squash=1.0; br.squash_frequency=2
br.inputs['Scale'].default_value=1.0; br.inputs['Brick Width'].default_value=0.205; br.inputs['Row Height'].default_value=0.068
br.inputs['Mortar Size'].default_value=0.009; br.inputs['Mortar Smooth'].default_value=0.2; br.inputs['Bias'].default_value=0.0
br.inputs['Color1'].default_value=(0.56,0.46,0.31,1); br.inputs['Color2'].default_value=(0.49,0.40,0.27,1); br.inputs['Mortar'].default_value=(0.63,0.61,0.55,1)
L.new(cmb.outputs['Vector'],br.inputs['Vector'])
# large-scale tone from the original base ramp (soft multiply) -> feeds where the ramp used to
cr=N['Color Ramp']; mixA=N['Mix']
tone=N.new('ShaderNodeMix'); tone.data_type='RGBA'; tone.blend_type='OVERLAY'; tone.inputs['Factor'].default_value=0.35
L.new(br.outputs['Color'],tone.inputs['A']); L.new(cr.outputs['Color'],tone.inputs['B'])
L.new(tone.outputs['Result'],mixA.inputs['A'])
# window frames: light anodised aluminium instead of near-black; transom (2x2 lites) across the glass
fr=N['Mix.003']; fr.inputs['B'].default_value=(0.50,0.50,0.48,1)
win=N['Mix.004']; wl=[l for l in L if l.to_node==win and l.to_socket.name=='Factor'][0]; wsrc=wl.from_socket
zr=M('SUBTRACT',sep.outputs['Z'],a0.outputs['Fac']); fz=M('FRACT',M('DIVIDE',M('SUBTRACT',zr,0.95),af.outputs['Fac']))
tr=M('GREATER_THAN',M('ABSOLUTE',M('SUBTRACT',fz,0.25)),0.008)
nf=M('MULTIPLY',wsrc,tr); L.remove(wl); L.new(nf,win.inputs['Factor'])
for nm in ('Mix.005','Mix.006'):
    x=N[nm]; xl=[l for l in L if l.to_node==x and l.to_socket.name=='Factor']
    if xl and xl[0].from_socket==wsrc: L.remove(xl[0]); L.new(nf,x.inputs['Factor'])
# soften the vertical streaks (brick weathers less than precast)
for nm in ('Mix.007','Mix.008'):
    x=N[nm]
    if not [l for l in L if l.to_node==x and l.to_socket.name=='Factor']: x.inputs['Factor'].default_value*=0.6
# mortar relief chained after the window-recess bump
bp=N['Bump']; pb=N['Principled BSDF']
b2=N.new('ShaderNodeBump'); b2.inputs['Strength'].default_value=0.25; b2.inputs['Distance'].default_value=0.006
L.new(M('SUBTRACT',1.0,br.outputs['Fac']),b2.inputs['Height']); L.new(bp.outputs['Normal'],b2.inputs['Normal']); L.new(b2.outputs['Normal'],pb.inputs['Normal'])
for n in STONE:
    o=bpy.data.objects[n]
    for s in o.material_slots:
        if s.material==src: s.material=m; o['tq_orig_mat']=SRC
src.use_fake_user=True
# fascia ring (light painted metal/concrete coping, projecting 0.30 m, 0.44 m deep)
fm=bpy.data.materials.new('TQ_Stone_fascia_paint_UNVERIFIED'); fm.use_nodes=True; FN=fm.node_tree.nodes; FL=fm.node_tree.links; fb=FN['Principled BSDF']
ftc=FN.new('ShaderNodeTexCoord'); fnz=FN.new('ShaderNodeTexNoise'); fnz.inputs['Scale'].default_value=3.0; fnz.inputs['Detail'].default_value=6
FL.new(ftc.outputs['Object'],fnz.inputs['Vector']); fcr=FN.new('ShaderNodeValToRGB'); fcr.color_ramp.elements[0].color=(0.50,0.50,0.47,1); fcr.color_ramp.elements[1].color=(0.60,0.60,0.57,1)
FL.new(fnz.outputs['Fac'],fcr.inputs[0]); FL.new(fcr.outputs['Color'],fb.inputs['Base Color']); fb.inputs['Roughness'].default_value=0.6; fb.inputs['Specular IOR Level'].default_value=0.3
col=bpy.data.collections.new(CN); sc.collection.children.link(col); col['tq_obj']=1
F=json.load(open(D+'data/tq/fascia.json'))
for k,f in F.items():
    top=f['top']; bm=bmesh.new()
    def loop(P,z):
        vs=[bm.verts.new((x,y,z)) for x,y in P]; es=[bm.edges.new((vs[i],vs[(i+1)%len(vs)])) for i in range(len(vs))]; return es
    es=loop(f['outer'],top+0.04)+loop(f['inner'],top+0.04)
    r=bmesh.ops.triangle_fill(bm,use_beauty=True,use_dissolve=True,edges=es)
    fcs=[g for g in r['geom'] if isinstance(g,bmesh.types.BMFace)]
    for fc in fcs: 
        if fc.normal.z<0: fc.normal_flip()
    ex=bmesh.ops.extrude_face_region(bm,geom=fcs)
    nv=[g for g in ex['geom'] if isinstance(g,bmesh.types.BMVert)]
    bmesh.ops.translate(bm,verts=nv,vec=(0,0,-0.44))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    nm='TQ_Stone_fascia_%s_UNVERIFIED'%k; me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free(); me.materials.append(fm)
    for p in me.polygons: p.use_smooth=False
    o=bpy.data.objects.new(nm,me); o['tq_obj']=1; o['UNVERIFIED']='projecting roof edge after 1965/66 slides; depth/projection guessed'; col.objects.link(o)
    print('TQ fascia',k,len(me.polygons),'faces top',round(top,2))
# close-up camera on the brick + windows + fascia (NW corner of Stone, from the north walk)
def cam(name,loc,tgt,lens):
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=30000; o=bpy.data.objects.new(name,cd); col.objects.link(o); o['tq_obj']=1
    o.location=Vector(loc); o.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); return o
cam('TQ_CAM_closeup_Stone_brick_fascia',(float(os.environ.get('CX',150)),float(os.environ.get('CY',312)),float(os.environ.get('CZ',138.5))),(float(os.environ.get('TX',146)),float(os.environ.get('TY',300)),float(os.environ.get('TZ',139.5))),35)
print('TQ applied; objects',len(bpy.data.objects))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
