# ws203 W19 near-camera bright sliver: p203A shows WS94 slit-filler cells 2-9 mm PROUD of the lot (45 cells) at the old seam (y~-105.6) -> a
# sun-facing sliver. Raise-only: lot/underlay verts (WS75/WS80/WS81) within 0.35 m of an exposed proud filler vert are lifted toward
# (filler z - 0.3 mm), full within 0.1 m, smoothstep to 0 at 0.35 m -> the filler is swallowed into one gently crowned mat (<=9 mm).
import bpy, numpy as np
X0,X1,Y0,Y1=-234.4,-232.4,-106.4,-104.7
F=[o for o in bpy.data.objects if o.name.startswith('WS94_lot_slit_filler')][0]; mw=F.matrix_world
FP=np.array([tuple(mw@v.co) for v in F.data.vertices]); m=(FP[:,0]>X0)&(FP[:,0]<X1)&(FP[:,1]>Y0)&(FP[:,1]<Y1); FP=FP[m]
print('F203g filler verts in box',len(FP),flush=True)
for pre in ('WS75_sprague_lot_asphalt','WS80_sprague_lot_fill_asphalt','WS81_lot_seam_underlay'):
    for o in [x for x in bpy.data.objects if x.name.startswith(pre)]:
        mw2=o.matrix_world; mi2=mw2.inverted(); n=0; mx=0
        for v in o.data.vertices:
            p=mw2@v.co
            if not (X0<p.x<X1 and Y0<p.y<Y1) or not len(FP): continue
            d=np.hypot(FP[:,0]-p.x,FP[:,1]-p.y); k=d.argmin()
            if d[k]>0.35: continue
            t=FP[k,2]-0.0003; u=min(max((d[k]-0.1)/0.25,0),1); w=1-(3*u*u-2*u*u*u)
            l=(t-p.z)*w
            if 0.0005<l<0.01: p.z+=l; v.co=mi2@p; n+=1; mx=max(mx,l)
        o.data.update(); print('F203g',o.name[:28],'lifted',n,'max %.4f'%mx,flush=True)
