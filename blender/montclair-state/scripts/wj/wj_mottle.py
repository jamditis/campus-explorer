"""wj: verge turf mottle on the shared ortho-tone ground material, gated by a packed 10 cm mask of the
Stone footway / service road verge (x118-148, y248-300). Mask R = verge, G = road-edge proximity."""
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
X0,Y0,WX,WY,RES=116.0,246.0,38.0,68.0,0.1
W,H=int(WX/RES),int(WY/RES)
def flat(names):
    vs=[];fs=[]
    for n in names:
        o=O[n]; m=o.matrix_world; b=len(vs)
        vs+= [Vector(((m@v.co).x,(m@v.co).y,0)) for v in o.data.vertices]
        fs+= [tuple(i+b for i in p.vertices) for p in o.data.polygons]
    return BVHTree.FromPolygons(vs,fs)
F=flat(['QS_footway_546643369_UNVERIFIED','QT_soil_edge_546643369_UNVERIFIED','QW_footway_546643369_ext_UNVERIFIED','QW_soil_edge_546643369_ext_UNVERIFIED'])
R=flat(['QS_service_546643370_UNVERIFIED','QW_service_546643370_ext_UNVERIFIED'])
df=np.zeros((H,W),np.float32); dr=np.zeros((H,W),np.float32); bt=np.zeros((H,W),bool)
for j in range(H):
    y=Y0+(j+0.5)*RES
    for i in range(W):
        p=Vector((X0+(i+0.5)*RES,y,0))
        a=F.find_nearest(p); b=R.find_nearest(p)
        df[j,i]=a[3] if a[0] else 99; dr[j,i]=b[3] if b[0] else 99
        if a[0] and b[0]: bt[j,i]=(a[0]-p).dot(b[0]-p)<0
s=df+dr
verge=((s<5.0)&bt&(df>0.02)&(dr>0.02)).astype(np.float32)
# soften: 3x box blur x2
def blur(a):
    p=np.pad(a,2,mode='edge'); o=np.zeros_like(a)
    for dy in range(-2,3):
        for dx in range(-2,3): o+=p[2+dy:2+dy+a.shape[0],2+dx:2+dx+a.shape[1]]
    return o/25
vm=blur(blur(verge))
# fade out at the mask box edges (1 m) so no seam
yy,xx=np.mgrid[0:H,0:W]*RES
edge=np.clip(np.minimum.reduce([xx,WX-xx,yy,WY-yy])/1.0,0,1)
vm*=edge
road=np.clip(1-dr/0.6,0,1)*(dr>0.02)
print('VERGE m2',round(float(verge.sum())*RES*RES,1))
import os
fp='/workspace/nj-scenes/montclair-state/textures/wj_verge_mask.png'; os.makedirs(os.path.dirname(fp),exist_ok=True)
for im in [i for i in bpy.data.images if i.name.startswith('WJ_verge_mask')]: bpy.data.images.remove(im)
tmp=bpy.data.images.new('WJ_tmp',W,H,alpha=False)
px=np.zeros((H,W,4),np.float32); px[...,0]=vm; px[...,1]=road; px[...,3]=1
tmp.pixels.foreach_set(px.ravel()); tmp.filepath_raw=fp; tmp.file_format='PNG'; tmp.save(); bpy.data.images.remove(tmp)
img=bpy.data.images.load(fp); img.name='WJ_verge_mask'; img.colorspace_settings.name='Non-Color'; img.pack()
chk=np.array(img.pixels[:]).reshape(H,W,4); print('MASKCHK',img.packed_file is not None, round(float(chk[...,0].sum())*0.01,1))
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']; nt=m.node_tree; N=nt.nodes; L=nt.links
for n in [n for n in N if n.name.startswith('WJ_')]: N.remove(n)
bs=N['Principled BSDF']; src=N['TS_final'].outputs['Result']
def nn(t,name,loc):
    n=N.new(t); n.name=name; n.label=name; n.location=loc; return n
g=nn('ShaderNodeNewGeometry','WJ_geo',(-600,-1400)); sp=nn('ShaderNodeSeparateXYZ','WJ_sep',(-400,-1400))
L.new(g.outputs['Position'],sp.inputs[0])
u=nn('ShaderNodeMapRange','WJ_u',(-200,-1300)); u.clamp=False; u.inputs[1].default_value=X0; u.inputs[2].default_value=X0+WX
v=nn('ShaderNodeMapRange','WJ_v',(-200,-1500)); v.clamp=False; v.inputs[1].default_value=Y0; v.inputs[2].default_value=Y0+WY
L.new(sp.outputs[0],u.inputs[0]); L.new(sp.outputs[1],v.inputs[0])
cb=nn('ShaderNodeCombineXYZ','WJ_uv',(0,-1400)); L.new(u.outputs[0],cb.inputs[0]); L.new(v.outputs[0],cb.inputs[1])
tx=nn('ShaderNodeTexImage','WJ_mask',(200,-1400)); tx.image=img; tx.extension='CLIP'; tx.interpolation='Linear'
L.new(cb.outputs[0],tx.inputs[0])
sc=nn('ShaderNodeSeparateColor','WJ_msep',(450,-1400)); L.new(tx.outputs['Color'],sc.inputs[0])
n1=nn('ShaderNodeTexNoise','WJ_nz1',(0,-1700)); n1.inputs['Scale'].default_value=0.35; n1.inputs['Detail'].default_value=3; n1.inputs['Roughness'].default_value=0.55
n2=nn('ShaderNodeTexNoise','WJ_nz2',(0,-1950)); n2.inputs['Scale'].default_value=2.6; n2.inputs['Detail'].default_value=2
L.new(g.outputs['Position'],n1.inputs['Vector']); L.new(g.outputs['Position'],n2.inputs['Vector'])
f1=nn('ShaderNodeMapRange','WJ_f1',(200,-1700)); f1.inputs[1].default_value=0.36; f1.inputs[2].default_value=0.64; f1.inputs[3].default_value=0.78; f1.inputs[4].default_value=1.06
f2=nn('ShaderNodeMapRange','WJ_f2',(200,-1950)); f2.inputs[1].default_value=0.3; f2.inputs[2].default_value=0.7; f2.inputs[3].default_value=0.9; f2.inputs[4].default_value=1.06
L.new(n1.outputs['Fac'],f1.inputs[0]); L.new(n2.outputs['Fac'],f2.inputs[0])
mf=nn('ShaderNodeMath','WJ_f12',(400,-1800)); mf.operation='MULTIPLY'; L.new(f1.outputs[0],mf.inputs[0]); L.new(f2.outputs[0],mf.inputs[1])
rd=nn('ShaderNodeMapRange','WJ_road',(600,-1600)); rd.inputs[3].default_value=1.0; rd.inputs[4].default_value=0.84
L.new(sc.outputs['Green'],rd.inputs[0])
mf2=nn('ShaderNodeMath','WJ_f',(800,-1800)); mf2.operation='MULTIPLY'; L.new(mf.outputs[0],mf2.inputs[0]); L.new(rd.outputs[0],mf2.inputs[1])
sv=nn('ShaderNodeVectorMath','WJ_scale',(1000,-1600)); sv.operation='SCALE'; L.new(src,sv.inputs[0]); L.new(mf2.outputs[0],sv.inputs['Scale'])
tn=nn('ShaderNodeMix','WJ_tint',(1200,-1600)); tn.data_type='RGBA'; tn.blend_type='MULTIPLY'; tn.inputs['Factor'].default_value=0.6
L.new(sv.outputs[0],tn.inputs['A']); tn.inputs['B'].default_value=(0.95,1.0,0.88,1)
mx=nn('ShaderNodeMix','WJ_final',(1400,-1400)); mx.data_type='RGBA'
L.new(sc.outputs['Red'],mx.inputs['Factor']); L.new(src,mx.inputs['A']); L.new(tn.outputs['Result'],mx.inputs['B'])
L.new(mx.outputs['Result'],bs.inputs['Base Color'])
print('WJ nodes',len([n for n in N if n.name.startswith('WJ_')]))
bpy.ops.wm.save_mainfile(compress=False) if False else bpy.ops.wm.save_mainfile()
print('SAVED')
