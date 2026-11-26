# ws247 W62d: undo the f246a per-vertex UV jumps (each pale vertex took the UV of the nearest green texel up to 20 m away,
# so 271 terrain faces stretched 2-37 m of ortho across 1 m -> pale ribbons/streaks along the bank foot N of the east stand)
# and give the same vertices a smooth lawn tint instead: point attribute 'ws247_lawn' (1 on the f246a vertices, 0.5 on
# their 1-ring) mixes the ortho texel toward a constant lawn colour (mean of green texels 6-20 m around the bank) in
# Ground_ortho_grass right after WS75_lawn_mix. Objects without the attribute read 0 -> unchanged. Geometry unchanged.
import bpy, os, numpy as np
TAG='F247A'; DRY=os.environ.get('DRY')=='1'
REF=os.environ.get('F247REF','/workspace/nj-scenes/montclair-state/montclair_state_pre_20261126ws246.blend')
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; M=T.matrix_world; uvl=me.uv_layers['ortho'].data
with bpy.data.libraries.load(REF) as (a,b): b.meshes=[me.name]
R=b.meshes[0]; ru=R.uv_layers['ortho'].data
assert len(R.loops)==len(me.loops) and len(R.vertices)==len(me.vertices), 'topology differs'
cur=np.empty(len(me.loops)*2,np.float32); uvl.foreach_get('uv',cur); ref=np.empty_like(cur); ru.foreach_get('uv',ref)
d=np.abs(cur-ref).reshape(-1,2).max(1)>1e-7; chg=np.where(d)[0]
lv=np.empty(len(me.loops),np.int32); me.loops.foreach_get('vertex_index',lv)
V=set(lv[chg].tolist())
print(TAG,'loops differing from ws245a',len(chg),'verts',len(V),flush=True)
# 3 pale verts f246a could not remap: add verts in the bank box whose ws245a texel is pale and that touch V's ring
ring=set()
for p in me.polygons:
    vs=p.vertices[:]
    if any(v in V for v in vs): ring.update(v for v in vs if v not in V)
xs=[(M@me.vertices[v].co) for v in V]
print(TAG,'ring verts',len(ring),'V bbox x',round(min(p.x for p in xs),1),round(max(p.x for p in xs),1),'y',round(min(p.y for p in xs),1),round(max(p.y for p in xs),1),flush=True)
# lawn colour: mean ortho texel (ws245a UV) of verts 6-20 m outside V's bbox that are green
img=next(n.image for n in bpy.data.materials['Ground_ortho_grass'].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'ortho' in n.image.name.lower())
w,h=img.size; px=np.empty(w*h*4,np.float32); img.pixels.foreach_get(px); px=px.reshape(h,w,4)
def col(u,v): return px[min(h-1,max(0,int(v*h))),min(w-1,max(0,int(u*w))),:3]
def green(c): return c[1]>=c[0]*1.01 and c[1]>c[2]*1.04 and c.sum()<1.5
x0=min(p.x for p in xs);x1=max(p.x for p in xs);y0=min(p.y for p in xs);y1=max(p.y for p in xs)
refuv=ref.reshape(-1,2); G=[]
for li in range(len(me.loops)):
    p=M@me.vertices[lv[li]].co
    dx=max(x0-p.x,0,p.x-x1); dy=max(y0-p.y,0,p.y-y1); dd=(dx*dx+dy*dy)**.5
    if 6<=dd<=20:
        c=col(*refuv[li])
        if green(c): G.append(c)
G=np.array(G); lawn=G.mean(0)
print(TAG,'green texels around',len(G),'mean (display)',lawn.round(3),flush=True)
mat=bpy.data.materials['Ground_ortho_grass']; nt=mat.node_tree; N=nt.nodes
w75=N['WS75_lawn_mix']; print(TAG,'WS75 out links',[(l.to_node.name,l.to_socket.name) for l in w75.outputs['Result'].links],flush=True)
if not DRY:
    uvl.foreach_set('uv',ref)  # restore ws245a UVs (only the f246a loops differ)
    at=me.attributes.get('ws247_lawn') or me.attributes.new('ws247_lawn','FLOAT','POINT')
    f=np.zeros(len(me.vertices),np.float32); f[list(ring)]=0.5; f[list(V)]=1.0; at.data.foreach_set('value',f)
    me.update()
    bpy.data.meshes.remove(R)
    if 'WS247_lawn_mix' not in N:
        a_=N.new('ShaderNodeAttribute'); a_.name='WS247_lawn_attr'; a_.attribute_type='GEOMETRY'; a_.attribute_name='ws247_lawn'; a_.location=(w75.location.x+200,w75.location.y-250)
        mx=N.new('ShaderNodeMix'); mx.name='WS247_lawn_mix'; mx.data_type='RGBA'; mx.blend_type='MIX'; mx.location=(w75.location.x+200,w75.location.y)
        outs=[l.to_socket for l in w75.outputs['Result'].links]
        lin=[c**2.2 if False else (c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4) for c in lawn.tolist()]
        mx.inputs['B'].default_value=(lin[0],lin[1],lin[2],1.0) if img.colorspace_settings.name=='sRGB' and not img.is_float else (*lawn.tolist(),1.0)
        nt.links.new(a_.outputs['Fac'],mx.inputs['Factor']); nt.links.new(w75.outputs['Result'],mx.inputs['A'])
        for s in outs: nt.links.new(mx.outputs['Result'],s)
        print(TAG,'node added; B',tuple(round(v,4) for v in mx.inputs['B'].default_value),'relinked',len(outs),flush=True)
    cur2=np.empty_like(cur); uvl.foreach_get('uv',cur2); print(TAG,'restored; loops still differing',int((np.abs(cur2-ref).reshape(-1,2).max(1)>1e-7).sum()),'attr ones',int((f==1).sum()),'halves',int((f==.5).sum()),flush=True)
