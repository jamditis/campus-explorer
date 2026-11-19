# ws233 fix c (on ws233b): W-R7b Granite_Curb base tone. The material's base colour = Mix(fac 1) of the granite image and a flat
# B colour, which reads near-white (viewer round 7: #e7e7e7, linear ~0.8). No granite has ~80 % albedo; grey curb granite is
# ~0.25-0.35 linear (tone UNVERIFIED for this campus, physical range only). Target mean base colour 0.30 linear, slightly warm.
import bpy, json, numpy as np
MS='/workspace/nj-scenes/montclair-state/'; rep={}
m=bpy.data.materials['Granite_Curb']; N=m.node_tree.nodes; mx=N['Mix']
rep['blend_type']=mx.blend_type; rep['data_type']=mx.data_type
fac=mx.inputs[0] if mx.data_type=='FLOAT' else mx.inputs['Factor']
cin=[i for i in mx.inputs if i.type=='RGBA']
rep['fac']=[round(x,3) for x in (mx.inputs[0].default_value,)] ; rep['rgba_inputs']=[(i.identifier,i.is_linked,tuple(round(c,3) for c in i.default_value)) for i in cin]
im=N['Image Texture'].image; rep['image']=im.name if im else None
mean=None
if im and im.size[0]:
    px=np.empty(im.size[0]*im.size[1]*4,dtype=np.float32); im.pixels.foreach_get(px); px=px.reshape(-1,4)[:,:3]
    mean=float(px.mean()); rep['image_mean']=round(mean,3); rep['image_colorspace']=im.colorspace_settings.name
B=[i for i in cin if not i.is_linked][-1]
old=tuple(B.default_value); rep['B_old']=[round(c,3) for c in old]
fv=[i for i in mx.inputs if i.name=='Factor' and not i.is_linked]; f=fv[-1].default_value if fv else None
f=f if not hasattr(f,'__len__') else f[0]
if mx.blend_type=='MIX' and f is not None and f>=0.999:
    B.default_value=(0.305,0.298,0.285,1.0); rep['action']='flat B set to linear 0.30 warm grey (fac 1 -> B is the colour)'
elif mx.blend_type=='MULTIPLY' and mean:
    k=min(1.0,0.30/max(mean*old[0],1e-3))*old[0]; B.default_value=(k,k*0.98,k*0.94,1.0); rep['action']=f'multiply tint -> {k:.3f}'
else:
    rep['action']='none (unexpected node setup)'
rep['B_new']=[round(c,3) for c in B.default_value]
print('F233C',json.dumps(rep),flush=True)
json.dump(rep,open(MS+'scripts/ws233/fix233c_report.json','w'))
