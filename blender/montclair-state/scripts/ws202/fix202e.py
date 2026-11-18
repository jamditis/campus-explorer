# ws202 W13: dark lens at the lawn edge just S of the Lot 3 S strip's E end. Probe p202w13: WS191b gap-lawn fill sits 2-4 cm LOW beside the
# WS163 lawn patch (which stands ~3 cm proud) at x -300..-299.3, y -238..-236.3 -> a small lawn cliff casting a shadow. One continuous lawn:
# RAISE-ONLY WS191b verts toward the WS163 patch surface (median of WS163 cells within 0.3 m, -2 mm), full <=0.3 m, linear to 0 at 0.6 m, cap 5 cm.
import bpy, numpy as np
G=np.load('/workspace/nj-scenes/montclair-state/scripts/ws202/p202w13.npz'); Z,O,xs,ys=G['Z'],G['O'],G['xs'],G['ys']; NM=list(G['names'])
kg=NM.index([n for n in NM if n.startswith('WS163_ground_patch')][0])
I,J=np.nonzero(O==kg); AX=xs[I]; AY=ys[J]; AZ=Z[I,J]
X0,X1,Y0,Y1=-300.6,-298.6,-238.4,-236.0
m=(AX>X0-0.7)&(AX<X1+0.7)&(AY>Y0-0.7)&(AY<Y1+0.7); AX,AY,AZ=AX[m],AY[m],AZ[m]
SH=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS191b_Lot3_S_gap_lawn_fill')]
for nme in SH:
    o=bpy.data.objects[nme]; mw=o.matrix_world; mi=mw.inverted(); n=0; mx=0
    for v in o.data.vertices:
        p=mw@v.co
        if not (X0<p.x<X1 and Y0<p.y<Y1): continue
        dd=np.hypot(AX-p.x,AY-p.y)
        if dd.min()>0.6: continue
        t=np.median(AZ[dd<max(0.3,dd.min()+0.08)])-0.002; d=dd.min()
        w=1.0 if d<=0.3 else (0.6-d)/0.3
        lift=(t-p.z)*w
        if 0.001<lift<0.05: p.z+=lift; v.co=mi@p; n+=1; mx=max(mx,lift)
    o.data.update(); print('F202e',nme[:34],'lifted',n,'max',round(mx,3),flush=True)
