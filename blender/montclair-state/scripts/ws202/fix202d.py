# ws202 W13: dark dash at the lawn edge by the W end of the Lot 3 S concrete strip. Probe p202w13 (0.03 m, real terrain): along a diagonal
# (-305.0,-237.0)->(-303.85,-236.1) the WS163 S-drive asphalt edge stands 3.5-7 cm ABOVE the WS162 apron feather / WS163 lawn patch -> a riser
# in shadow = dark dash. Designer call: drive edge meets the apron flush and the lawn sits ~1 cm under the pavement edge (normal mow edge), no open
# riser. RAISE-ONLY: low-side verts within 0.5 m of the drive edge get lifted toward (drive edge z - off), full within 0.15 m, linear to 0 at 0.5 m.
import bpy, numpy as np, os
G=np.load('/workspace/nj-scenes/montclair-state/scripts/ws202/p202w13.npz'); Z,O,xs,ys=G['Z'],G['O'],G['xs'],G['ys']; NM=list(G['names'])
ka=NM.index([n for n in NM if n.startswith('WS163_Lot3_aisle_S_drive')][0])
X0,X1,Y0,Y1=-305.4,-303.5,-237.4,-235.85
I,J=np.nonzero(O==ka); AX=xs[I]; AY=ys[J]; AZ=Z[I,J]
m=(AX>X0-0.6)&(AX<X1+0.6)&(AY>Y0-0.6)&(AY<Y1+0.6); AX,AY,AZ=AX[m],AY[m],AZ[m]
OFF={'WS162_Lot3_S_end_apron_feather':0.001,'WS162_Lot3_asphalt':0.001,'WS163_ground_patch_W_of_WS110':0.012}
tot=0
for o in bpy.data.objects:
    if o.type!='MESH': continue
    off=[v for k,v in OFF.items() if o.name.startswith(k)]
    if not off: continue
    off=off[0]; mw=o.matrix_world; mi=mw.inverted(); n=0; mx=0
    for v in o.data.vertices:
        p=mw@v.co
        if not (X0<p.x<X1 and Y0<p.y<Y1): continue
        dd=np.hypot(AX-p.x,AY-p.y); k=dd.argmin(); d=dd[k]
        if d>0.5: continue
        near=dd<d+0.06; t=np.median(AZ[near])-off
        w=1.0 if d<=0.15 else (0.5-d)/0.35
        lift=(t-p.z)*w
        if 0.001<lift<0.08: p.z+=lift; v.co=mi@p; n+=1; mx=max(mx,lift)
    o.data.update(); tot+=n; print('F202d',o.name[:34],'lifted',n,'max',round(mx,3),flush=True)
print('F202d total',tot,flush=True)
SH=[o.name for o in bpy.data.objects if o.type=='MESH' and any(o.name.startswith(k) for k in OFF)]
