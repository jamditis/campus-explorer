# ws263 pale soil under the police-lawn grass (merge208 CHAIN). The merged gd_grass_police_lawn_points (ws262) stand on
# WS68_RHD_ground_northDTM (WS68_Ground_ortho_grass_north2020) and the M3b west-rail-corridor DTM (North_ground_ortho2020.001);
# both drape the 2020 NJ ortho, which there is a pale spring-thaw / leaf-litter tone, so the ground between blades reads whitish
# (ws262 close-up). Real mown lawn shows dark olive thatch between blades. Add a last colour layer to both materials (1 user each):
# mask = blurred grass-point density (0.25 m grid, sigma 0.6 m, packed 'W263_police_grass_density' image, so it fades exactly with
# ws262's 3 m edge feather) -> Base Color multiplied toward olive and mixed a little toward a dark thatch tone. Outside the mask
# box the image is clipped (0) -> no change anywhere else.
import bpy, numpy as np
TAG='F263C'; G=bpy.data.objects['gd_grass_police_lawn_points']
P=np.array([G.matrix_world@v.co for v in G.data.vertices])[:,:2]
R=0.25; pad=3.0; x0,y0=P.min(0)-pad; x1,y1=P.max(0)+pad
NX=int(np.ceil((x1-x0)/R)); NY=int(np.ceil((y1-y0)/R)); x1=x0+NX*R; y1=y0+NY*R
H=np.zeros((NY,NX)); ii=((P[:,0]-x0)/R).astype(int); jj=((P[:,1]-y0)/R).astype(int); np.add.at(H,(jj,ii),1)
def blur(a,s):
    r=int(3*s); k=np.exp(-0.5*(np.arange(-r,r+1)/s)**2); k/=k.sum()
    a=np.apply_along_axis(lambda v:np.convolve(v,k,'same'),0,a); return np.apply_along_axis(lambda v:np.convolve(v,k,'same'),1,a)
B=blur(H,0.6/R); core=np.percentile(B[H>0],60); M=np.clip(B/core,0,1); M=M*M*(3-2*M)
img=bpy.data.images.get('W263_police_grass_density') or bpy.data.images.new('W263_police_grass_density',NX,NY,alpha=False,float_buffer=False)
px=np.ones((NY,NX,4),np.float32); px[...,0]=px[...,1]=px[...,2]=M; img.pixels.foreach_set(px.ravel()); img.colorspace_settings.name='Non-Color'; img.pack()
print(TAG,'mask',NX,NY,'box x %.2f..%.2f y %.2f..%.2f'%(x0,x1,y0,y1),'cells>0.5',int((M>0.5).sum()),'points',len(P),flush=True)
for mn in ('WS68_Ground_ortho_grass_north2020','North_ground_ortho2020.001'):
    m=bpy.data.materials[mn]; nt=m.node_tree; N=nt.nodes; L=nt.links
    if 'W263_soil_mix' in N: print(TAG,'already',mn); continue
    bsdf=[n for n in N if n.type=='BSDF_PRINCIPLED' and n.outputs['BSDF'].is_linked and n.inputs['Base Color'].is_linked]; print(TAG,mn,'bsdfs',[(n.name,[l.to_node.name for l in n.outputs['BSDF'].links]) for n in bsdf],flush=True); bsdf=bsdf[0]
    lk=bsdf.inputs['Base Color'].links[0]; src=lk.from_socket; L.remove(lk)
    geo=N.new('ShaderNodeNewGeometry'); geo.name='W263_geo'; sep=N.new('ShaderNodeSeparateXYZ'); sep.name='W263_sep'; L.new(geo.outputs['Position'],sep.inputs[0])
    def lin(sock,a,b,name):
        mr=N.new('ShaderNodeMapRange'); mr.name=name; mr.clamp=False; mr.inputs['From Min'].default_value=a; mr.inputs['From Max'].default_value=b; L.new(sock,mr.inputs['Value']); return mr
    u=lin(sep.outputs['X'],x0,x1,'W263_u'); v=lin(sep.outputs['Y'],y0,y1,'W263_v')
    cmb=N.new('ShaderNodeCombineXYZ'); cmb.name='W263_uv'; L.new(u.outputs['Result'],cmb.inputs['X']); L.new(v.outputs['Result'],cmb.inputs['Y'])
    tx=N.new('ShaderNodeTexImage'); tx.name='W263_mask'; tx.image=img; tx.extension='CLIP'; tx.interpolation='Linear'; L.new(cmb.outputs['Vector'],tx.inputs['Vector'])
    k1=N.new('ShaderNodeMath'); k1.name='W263_fac'; k1.operation='MULTIPLY'; k1.inputs[1].default_value=0.85; L.new(tx.outputs['Color'],k1.inputs[0])
    mul=N.new('ShaderNodeMix'); mul.name='W263_olive_mul'; mul.data_type='RGBA'; mul.blend_type='MULTIPLY'
    L.new(k1.outputs[0],mul.inputs['Factor']); L.new(src,mul.inputs['A']); mul.inputs['B'].default_value=(0.46,0.56,0.30,1)
    k2=N.new('ShaderNodeMath'); k2.name='W263_fac_thatch'; k2.operation='MULTIPLY'; k2.inputs[1].default_value=0.35; L.new(k1.outputs[0],k2.inputs[0])
    mx=N.new('ShaderNodeMix'); mx.name='W263_soil_mix'; mx.data_type='RGBA'; mx.blend_type='MIX'
    L.new(k2.outputs[0],mx.inputs['Factor']); L.new(mul.outputs['Result'],mx.inputs['A']); mx.inputs['B'].default_value=(0.050,0.058,0.026,1)
    L.new(mx.outputs['Result'],bsdf.inputs['Base Color'])
    print(TAG,'layer added',mn,'was fed by',src.node.name,flush=True)
