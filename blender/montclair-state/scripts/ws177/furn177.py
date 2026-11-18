import bpy, numpy as np, re
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
kw=re.compile(r'lamp|light|pole|tree|sign|hydrant|bench|bollard|post|hedge|shrub|bush|bin|meter|util|crosswalk|stop|ramp|grate|inlet|drain',re.I)
with bpy.data.libraries.load(p) as (a,b):
    sel=[n for n in a.objects if kw.search(n) and not n.startswith(('QQ','PP','RR'))]
    b.objects=sel
print('SEL',len(sel),flush=True)
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
face=lambda t: -0.01462*t+0.292
for o in b.objects:
    if o is None: continue
    pts=[]
    if o.type=='MESH' and len(o.data.vertices)<200000:
        M=np.array(o.matrix_world); V=np.array([v.co[:] for v in o.data.vertices]) if len(o.data.vertices) else np.zeros((0,3))
        if len(V): W=V@M[:3,:3].T+M[:3,3]; pts=W
    if len(pts)==0: pts=np.array([o.matrix_world.translation[:]])
    d=pts[:,:2]-A; t=d@T; s=d@N; u=s-face(t)
    k=(t>54)&(t<192)&(u>-1.0)&(u<4.0)
    if k.any(): print('FURN',o.name[:70],o.type,'n',k.sum(),'t %.1f..%.1f u %.2f..%.2f z %.1f..%.1f'%(t[k].min(),t[k].max(),u[k].min(),u[k].max(),pts[k,2].min(),pts[k,2].max()),flush=True)
