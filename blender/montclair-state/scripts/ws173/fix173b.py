# ws173b review fix: green specks/triangles poking through the drives (lawn/lip faces 8-12 mm under the drive top, GN grass on them)
# + ws173c: ground patches under the lowered walk front/wings poked through (green triangle at the D2 mouth) -> sink 0.16 in the walk band
# -> sink every lawn-family vertex strictly inside a drive footprint (inset 0.05 m) by 0.07 m; drive skirts (8 cm) hide the edge slope.
import bpy, numpy as np
OB=bpy.data.objects
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
DR=[('D1',-75.5,-71.0,-77.0,-70.75,-17.5,-20.8),('D2',-57.0,-52.75,-57.0,-52.75,-17.5,-20.8),('D3',-42.0,-37.5,-42.5,-35.0,-15.5,-21.5)]
def inside(s,t,e=0.05,band=True):
    for nm,a,b,a2,b2,sfl,send in DR:
        if band and -13.12 <= s < -11.2 and a-1.0 < t < b+1.0: return True   # walk band incl. 1 m wings (walk front lowered there)
        if not (send+e < s < -13.08-0.0): continue
        if s>=sfl+1.0: ta,tb=a,b
        elif s<=sfl: ta,tb=a2,b2
        else: u=(sfl+1.0-s); ta,tb=a+(a2-a)*u,b+(b2-b)*u
        if ta+e<t<tb-e: return True
    return False
for n in ['WS172_frontyards_S_of_NormalAve_W_DTM2023_J5D5','WS163_walk_back_lawn_lip_S_UNVERIFIED','WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED','WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED']:
    o=OB.get(n)
    if not o: continue
    mw=o.matrix_world; mi=mw.inverted(); k=0
    for v in o.data.vertices:
        w=mw@v.co; d=np.array((w.x,w.y))-A; s=float(d@N); t=float(d@T)
        if inside(s,t,band=('lip' not in n)): w.z-=(0.16 if s>-13.12 else 0.07); v.co=mi@w; k+=1
    o.data.update(); print('FIX173b sunk',n,k,flush=True)
