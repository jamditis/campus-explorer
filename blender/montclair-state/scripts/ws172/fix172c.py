# ws172c (review fixes): (1) yard-tree autumn tone toned down to match the green campus street trees N of the road (scene season = early/mid Oct,
# asset 'v2Oct'); ws172b values read peak-autumn orange in the oblique. (2) dark '<' wedges at the S walk back lip in the E eye view = the
# WS163_walk_back_lawn_lip_S strip sitting 0.10-0.13 below the LiDAR DTM behind the walk -> raise only lip verts BEHIND the walk back edge
# (s < sback-0.02) to DTM172-0.03 (never above the walk; never lowers).
import bpy, math, numpy as np
OB=bpy.data.objects
AU={'S_yard_A':0.18,'S_yard_B':0.10,'S_yard_C':0.24,'S_yard_D':0.15,'S_yard_E':0.12,'S_yard_H':0.30,'S_yard_I':0.20,'S_yard_K':0.08}
for o in OB:
    if o.name.startswith('WS171_tree_S_yard_'):
        lab='S_yard_'+o.name.split('S_yard_')[1][0]; o['autumn']=AU.get(lab,0.15)
print('FIX172c autumn',{o.name[11:20]:o.get('autumn') for o in OB if o.name.startswith('WS171_tree_S_yard_')},flush=True)
D=np.load('/workspace/nj-scenes/montclair-state/prep/ws172_s77/dtm172.npy')[0]; X0,Y0,R=-360.0,-315.0,0.5
def dz(x,y):
    fi=(x-X0)/R-0.5; fj=(y-Y0)/R-0.5
    i=int(min(max(math.floor(fi),0),D.shape[1]-2)); j=int(min(max(math.floor(fj),0),D.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty)
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N)
sw=OB['WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED']
sback=min(float(np.dot(np.array(((sw.matrix_world@v.co).x,(sw.matrix_world@v.co).y))-A,N)) for v in sw.data.vertices)
lip=OB.get('WS163_walk_back_lawn_lip_S_UNVERIFIED'); n=0; mx=0
if lip:
    mw=lip.matrix_world; mi=mw.inverted()
    for v in lip.data.vertices:
        w=mw@v.co
        if not (-345<w.x<-262): continue
        s=float(np.dot(np.array((w.x,w.y))-A,N))
        if s>=sback-0.02: continue
        zt=dz(w.x,w.y)-0.03
        if zt>w.z+0.005: mx=max(mx,zt-w.z); w.z=zt; v.co=mi@w; n+=1
    lip.data.update()
print('FIX172c lip verts raised',n,'max',round(mx,3),'sback',round(sback,2),flush=True)
