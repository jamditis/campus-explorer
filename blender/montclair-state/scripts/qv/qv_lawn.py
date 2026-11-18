# qv (Nov 3 2026 ~12:40 AM ET, MAIN, day 7 Richardson N/W ground). Shader-only edit of OW2_Context_skirt_ortho_strip_tone_UNVERIFIED
# (the coarse 3DEP skirt, ~36 m triangles, 1k ortho = smeared pale ground N/W of Richardson): inside x -60..170, y 228..362
# (10 m fade) blend in a crisp world-mapped lawn (Grass004 colour + normal, 2 scales of noise tint, ortho kept as low-freq tone),
# masked by data/qv/qv_lawn_mask.png (0 only under Richardson; the Student Center / Health Drop-In (day 8, not built in MAIN yet)
# and Reid Hall (outside boundary) footprints read as lawn placeholder). UNVERIFIED visual approximation (grass type/tone).
# REVERT=1 removes the QV_ nodes and restores the original Base Color / Normal links (material props qv_prev_*).
import bpy,os
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']; nt=m.node_tree; N=nt.nodes; L=nt.links
P=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]
def relink(key,inp):
    if key+'_node' in m:
        L.new(N[m[key+'_node']].outputs[m[key+'_out']],P.inputs[inp]); del m[key+'_node']; del m[key+'_out']
    elif key+'_none' in m:
        for l in list(P.inputs[inp].links): L.remove(l)
        del m[key+'_none']
def revert():
    relink('qv_prev_bc','Base Color'); relink('qv_prev_nrm','Normal')
    for n in [n for n in N if n.name.startswith('QV_')]: N.remove(n)
    im=bpy.data.images.get('QV_lawn_mask_UNVERIFIED')
    if im and im.users==0: bpy.data.images.remove(im)
    print('QVL reverted')
revert()
if os.environ.get('REVERT')=='1':
    if os.environ.get('QVSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
def remember(key,inp):
    if P.inputs[inp].links:
        s=P.inputs[inp].links[0].from_socket; m[key+'_node']=s.node.name; m[key+'_out']=list(s.node.outputs).index(s); return s
    m[key+'_none']=1; return None
bc=remember('qv_prev_bc','Base Color'); nr=remember('qv_prev_nrm','Normal')
def nn(t,nm,**kw):
    n=N.new(t); n.name='QV_'+nm; n.label=n.name
    for k,v in kw.items(): setattr(n,k,v)
    return n
def MN(op,a,b=None,nm='m'):
    n=nn('ShaderNodeMath',nm,operation=op)
    for i,v in enumerate((a,b)):
        if v is None: continue
        if isinstance(v,(int,float)): n.inputs[i].default_value=v
        else: L.new(v,n.inputs[i])
    return n.outputs[0]
def MR(v,a,b,nm):
    n=nn('ShaderNodeMapRange',nm,interpolation_type='SMOOTHSTEP'); L.new(v,n.inputs[0]); n.inputs[1].default_value=a; n.inputs[2].default_value=b; return n.outputs[0]
X0,X1,Y0,Y1=-60.,170.,228.,362.
g=nn('ShaderNodeNewGeometry','geo'); ps=nn('ShaderNodeSeparateXYZ','psep'); L.new(g.outputs['Position'],ps.inputs[0])
F=10.
gate=MN('MULTIPLY',MN('MULTIPLY',MR(ps.outputs['X'],X0,X0+F,'x0'),MR(ps.outputs['X'],X1,X1-F,'x1'),'bx'),MN('MULTIPLY',MR(ps.outputs['Y'],Y0,Y0+F,'y0'),MR(ps.outputs['Y'],Y1,Y1-F,'y1'),'by'),'gate')
# mask image in world xy
u=MN('MULTIPLY',MN('SUBTRACT',ps.outputs['X'],X0,'ux'),1/(X1-X0),'u'); v=MN('MULTIPLY',MN('SUBTRACT',ps.outputs['Y'],Y0,'vy'),1/(Y1-Y0),'v')
cx=nn('ShaderNodeCombineXYZ','uv'); L.new(u,cx.inputs[0]); L.new(v,cx.inputs[1])
mim=bpy.data.images.load(os.path.abspath('data/qv/qv_lawn_mask.png'),check_existing=True); mim.name='QV_lawn_mask_UNVERIFIED'; mim.colorspace_settings.name='Non-Color'
try: mim.pack()
except Exception as e: print('pack fail',e)
mt=nn('ShaderNodeTexImage','mask',image=mim,extension='EXTEND',interpolation='Linear'); L.new(cx.outputs[0],mt.inputs[0])
# review fix: soften the hard lawn/ortho line at the core-box edge -> 35 m outer ring where the lawn only goes on ortho cells
# that already read green (green minus mean(red,blue)), so roads/roofs out there keep the ortho
O=35.
outer=MN('MULTIPLY',MN('MULTIPLY',MR(ps.outputs['X'],X0-O,X0,'ox0'),MR(ps.outputs['X'],X1+O,X1,'ox1'),'obx'),MR(ps.outputs['Y'],Y1+O,Y1,'oy1'),'outer')
if bc is not None:
    sr=nn('ShaderNodeSeparateColor','bcsep'); L.new(bc,sr.inputs[0])
    grn=MN('SUBTRACT',sr.outputs[1],MN('MULTIPLY',MN('ADD',sr.outputs[0],sr.outputs[2],'rb'),0.5,'rbm'),'grn')
    gf=MR(grn,0.004,0.03,'gf')
else: gf=1.0
ring=MN('MULTIPLY',MN('MULTIPLY',MN('SUBTRACT',1.0,gate,'ngate'),outer,'ro'),gf,'ring')
amt=MN('MULTIPLY',MN('MULTIPLY',MN('ADD',gate,ring,'gr'),mt.outputs['Color'],'gm'),0.92,'amt')
# lawn colour: Grass004 world-mapped at 1.7 m, plus a rotated 4.3 m copy to break tiling
gi=bpy.data.images.get('Grass004_1K-JPG_Color.jpg'); gn=bpy.data.images.get('Grass004_1K-JPG_NormalGL.jpg')
def tex(img,scale,rot,nm,noncolor=False):
    mp=nn('ShaderNodeMapping',nm+'_map'); mp.inputs['Scale'].default_value=(1/scale,1/scale,1); mp.inputs['Rotation'].default_value=(0,0,rot)
    L.new(g.outputs['Position'],mp.inputs[0]); t=nn('ShaderNodeTexImage',nm,image=img,interpolation='Linear'); L.new(mp.outputs[0],t.inputs[0]); return t
t1=tex(gi,1.7,0.0,'g1'); t2=tex(gi,4.3,0.9,'g2')
mixg=nn('ShaderNodeMix','gmix',data_type='RGBA'); mixg.inputs[0].default_value=0.45; L.new(t1.outputs['Color'],mixg.inputs[6]); L.new(t2.outputs['Color'],mixg.inputs[7])
# tone: patchy dry/green variation (noise 9 m + 2.5 m) like the Lawn_Varied terrain material; late-Oct green-yellow
nz=nn('ShaderNodeTexNoise','nz'); nz.inputs['Scale'].default_value=0.11; nz.inputs['Detail'].default_value=4; L.new(g.outputs['Position'],nz.inputs['Vector'])
nz2=nn('ShaderNodeTexNoise','nz2'); nz2.inputs['Scale'].default_value=0.4; nz2.inputs['Detail'].default_value=3; L.new(g.outputs['Position'],nz2.inputs['Vector'])
cr=nn('ShaderNodeValToRGB','ramp'); L.new(MN('MULTIPLY',MN('ADD',nz.outputs['Fac'],nz2.outputs['Fac'],'nza'),0.5,'nzm'),cr.inputs[0])
cr.color_ramp.elements[0].position=0.38; cr.color_ramp.elements[0].color=(0.58,0.60,0.36,1)
cr.color_ramp.elements[1].position=0.66; cr.color_ramp.elements[1].color=(1.05,0.92,0.58,1)
tint=nn('ShaderNodeMix','tint',data_type='RGBA',blend_type='MULTIPLY'); tint.inputs[0].default_value=1.0; L.new(mixg.outputs[2],tint.inputs[6]); L.new(cr.outputs[0],tint.inputs[7])
hsv=nn('ShaderNodeHueSaturation','hsv'); hsv.inputs['Value'].default_value=0.70; hsv.inputs['Saturation'].default_value=0.60; L.new(tint.outputs[2],hsv.inputs['Color'])
# keep a little of the ortho's low-frequency tone (worn paths, shade) via soft light
lawn=hsv.outputs['Color']
if bc is not None:
    sl=nn('ShaderNodeMix','ortho_tone',data_type='RGBA',blend_type='SOFT_LIGHT'); sl.inputs[0].default_value=0.55; L.new(lawn,sl.inputs[6]); L.new(bc,sl.inputs[7]); lawn=sl.outputs[2]
fm=nn('ShaderNodeMix','final',data_type='RGBA',clamp_factor=True); L.new(amt,fm.inputs[0])
if bc is not None: L.new(bc,fm.inputs[6])
else: fm.inputs[6].default_value=P.inputs['Base Color'].default_value
L.new(lawn,fm.inputs[7]); L.new(fm.outputs[2],P.inputs['Base Color'])
# normal: Grass004 normal map (1.7 m) blended by amt over the previous normal
nt1=tex(gn,1.7,0.0,'gnrm'); nt1.image.colorspace_settings.name='Non-Color'
nmap=nn('ShaderNodeNormalMap','nmap'); nmap.inputs['Strength'].default_value=0.6; L.new(nt1.outputs['Color'],nmap.inputs['Color'])
nm_=nn('ShaderNodeMix','nmix',data_type='VECTOR'); L.new(amt,nm_.inputs[0])
if nr is not None: L.new(nr,nm_.inputs[4])
else: L.new(g.outputs['Normal'],nm_.inputs[4])
L.new(nmap.outputs[0],nm_.inputs[5]); L.new(nm_.outputs[1],P.inputs['Normal'])
print('QVL lawn nodes added', len([n for n in N if n.name.startswith('QV_')]), 'prev bc', m.get('qv_prev_bc_node'), 'nrm', m.get('qv_prev_nrm_node'))
if os.environ.get('QVSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
