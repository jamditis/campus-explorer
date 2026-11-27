# ws263 (merge208 CHAIN, after f263c/f263d): f263c's generated+packed density image came back empty after save (test263r: not
# packed, max 0), so the W263 layers did nothing. Rebuild the same mask (0.25 m grid, sigma 0.6 m, smoothstep of density / p60),
# write it as an 8-bit PNG to //data/ws263/police_grass_density263.png and point both W263_mask nodes at that file.
import bpy, numpy as np, os
TAG='F263E'; G=bpy.data.objects['gd_grass_police_lawn_points']
P=np.array([G.matrix_world@v.co for v in G.data.vertices])[:,:2]
R=0.25; pad=3.0; x0,y0=P.min(0)-pad; x1,y1=P.max(0)+pad
NX=int(np.ceil((x1-x0)/R)); NY=int(np.ceil((y1-y0)/R)); x1=x0+NX*R; y1=y0+NY*R
H=np.zeros((NY,NX)); ii=((P[:,0]-x0)/R).astype(int); jj=((P[:,1]-y0)/R).astype(int); np.add.at(H,(jj,ii),1)
def blur(a,s):
    r=int(3*s); k=np.exp(-0.5*(np.arange(-r,r+1)/s)**2); k/=k.sum()
    a=np.apply_along_axis(lambda v:np.convolve(v,k,'same'),0,a); return np.apply_along_axis(lambda v:np.convolve(v,k,'same'),1,a)
B=blur(H,0.6/R); core=np.percentile(B[H>0],60); M=np.clip(B/core,0,1); M=M*M*(3-2*M)
fn='/workspace/nj-scenes/montclair-state/data/ws263/police_grass_density263.png'
tmp=bpy.data.images.new('W263_tmp',NX,NY,alpha=False); px=np.ones((NY,NX,4),np.float32); px[...,0]=px[...,1]=px[...,2]=M
tmp.pixels.foreach_set(px.ravel()); tmp.filepath_raw=fn; tmp.file_format='PNG'; tmp.save(); bpy.data.images.remove(tmp)
old=bpy.data.images.get('W263_police_grass_density')
img=bpy.data.images.load(fn); img.name='W263_police_grass_density263'; img.filepath='//data/ws263/police_grass_density263.png'; img.colorspace_settings.name='Non-Color'
px2=np.array(img.pixels[:]).reshape(NY,NX,4)[...,0]
print(TAG,'png',os.path.getsize(fn),'size',img.size[:],'max %.3f mean %.3f'%(px2.max(),px2.mean()),'box x %.2f..%.2f y %.2f..%.2f'%(x0,x1,y0,y1),flush=True)
for mn in ('WS68_Ground_ortho_grass_north2020','North_ground_ortho2020.001'):
    nt=bpy.data.materials[mn].node_tree; n=nt.nodes['W263_mask']; n.image=img
    assert abs(nt.nodes['W263_u'].inputs['From Min'].default_value-x0)<1e-3 and abs(nt.nodes['W263_v'].inputs['From Max'].default_value-y1)<1e-3
    print(TAG,'mask node ->',img.name,'in',mn,flush=True)
if old and old.users==0: bpy.data.images.remove(old)
