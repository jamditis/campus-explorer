# ws203 W13a: WS163 S-drive cross-slope KINK at x~-306.4 (last facet column -306.4..-305.5 is ~flat after 5-7 % -> convex break = wavy dark line in the W eye).
# Designer call: a drive cross-slope eases out toward its edge, it doesn't fold flat in the last metre. RAISE-ONLY: per vertex row, if the
# edge facet slope < 0.6 x the previous facet slope, lift the edge vert so the edge facet carries 0.6 x the previous slope (progressive easing
# ~7 -> 5 -> 3 %); mid-row verts (x~-305.93) lifted by the interpolated half; lawn (WS163/WS110 patches) east of the edge raised with the
# edge lift, linear to 0 over 0.9 m, so the mow edge stays ~1 cm under the pavement edge. Cap 5 cm.
import bpy, numpy as np
Y0,Y1=-243.2,-237.4
def ob(p): return [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(p)][0]
D=ob('WS163_Lot3_aisle_S_drive'); mw=D.matrix_world; mi=mw.inverted()
V=[(v,mw@v.co) for v in D.data.vertices]
rows={}
for v,p in V:
    if Y0<p.y<Y1 and -309.0<p.x<-305.3: rows.setdefault(round(p.y,1),[]).append((p.x,v,p))
EL=[]  # (y, xedge, lift, znew)
for y,r in rows.items():
    r.sort(key=lambda t:t[0])
    if len(r)<3 or r[-1][0]<-305.8: continue
    (xp,_,pp),(xm,_,pm),(xe,ve,pe)=r[-3],r[-2],r[-1]
    sp=(pm.z-pp.z)/(xm-xp); se=(pe.z-pm.z)/(xe-xm)
    if sp>0.01 and se<0.6*sp:
        t=pm.z+0.6*sp*(xe-xm); lift=min(t-pe.z,0.05)
        if lift>0.001: pe.z+=lift; ve.co=mi@pe; EL.append((y,xe,lift,pe.z)); print('F203a edge y',y,'sp %.3f se %.3f lift %.3f'%(sp,se,lift),flush=True)
EL.sort()
ely=np.array([e[0] for e in EL]); ell=np.array([e[2] for e in EL]); elz=np.array([e[3] for e in EL]); elx=np.array([e[1] for e in EL])
def L(y): return float(np.interp(y,ely,ell,left=0,right=0)) if len(EL) else 0.0
def ZE(y): return float(np.interp(y,ely,elz))
def XE(y): return float(np.interp(y,ely,elx))
nm=0
for y,r in rows.items():
    for x,v,p in r:
        if -306.2<x<-305.75 and all(abs(p.y-e[0])>0.05 for e in EL):
            l=L(p.y)*0.5
            if l>0.001: p.z+=l; v.co=mi@p; nm+=1
D.data.update(); print('F203a edges',len(EL),'mid',nm,flush=True)
for pre in ('WS163_ground_patch_W_of_WS110','WS110_ground_patch_S'):
    o=ob(pre); mw2=o.matrix_world; mi2=mw2.inverted(); n=0; mx=0
    for v in o.data.vertices:
        p=mw2@v.co
        if not (ely.min()-0.5<p.y<ely.max()+0.5) if len(EL) else True: continue
        xe=XE(p.y); d=p.x-xe
        if d<-0.05 or d>0.9: continue
        l=L(p.y)*(1-max(d,0)/0.9)
        if d<0.15: l=min(l,ZE(p.y)-0.008-p.z)
        if 0.001<l<0.05: p.z+=l; v.co=mi2@p; n+=1; mx=max(mx,l)
    o.data.update(); print('F203a lawn',pre[:20],'lifted',n,'max %.3f'%mx,flush=True)
