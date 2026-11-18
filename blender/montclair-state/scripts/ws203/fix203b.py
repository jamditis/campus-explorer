# ws203 W13b: dark lens at the Lot 3 S concrete strip's S edge (~(-302.1,-236.4)). Hiding WS170b+WS191c shows NO ground under the strip and
# its fillets (open cut-out), so a grazing view sees through the hair gaps between strip/fillet and the WS163 lawn into the void = dark lens.
# Designer call: real ground is continuous soil under a strip -> add one hidden lawn UNDERLAY sheet under the strip/fillet footprint
# (dilated 0.3 m), 3.5 cm below the lowest top surface within 0.3 m, so any grazing slit shows lawn, not void. Nothing visible moves.
import bpy, numpy as np
G=np.load('/workspace/nj-scenes/montclair-state/scripts/ws202/p202w13.npz'); Z,O,xs,ys=G['Z'],G['O'],G['xs'],G['ys']; NM=list(G['names'])
K=[i for i,n in enumerate(NM) if n.startswith(('WS170b','WS191c','WS190b','WS192_','WS191b'))]
st=xs[1]-xs[0]; w=int(round(0.3/st))
M=np.isin(O,K)
from numpy.lib.stride_tricks import sliding_window_view as sw
Mp=np.pad(M,w); Md=sw(Mp,(2*w+1,2*w+1)).max(axis=(2,3))
Zp=np.pad(np.where(np.isfinite(Z),Z,1e9),w,constant_values=1e9); Zmin=sw(Zp,(2*w+1,2*w+1)).min(axis=(2,3))
SS3=0.1; gx=np.arange(-306.5,-298.0+1e-6,SS3); gy=np.arange(-237.6,-233.4+1e-6,SS3)
def cell(x,y):
    i=int(round((x-xs[0])/st)); j=int(round((y-ys[0])/st)); return min(max(i,0),len(xs)-1),min(max(j,0),len(ys)-1)
idx={}; verts=[]; faces=[]
for a,x in enumerate(gx):
    for b,y in enumerate(gy):
        i,j=cell(x,y)
        # vertex used if any of its 4 adjacent cells is in the dilated mask
        if Md[i,j] and Zmin[i,j]<1e8: idx[(a,b)]=len(verts); verts.append((x,y,Zmin[i,j]-0.035))
for a in range(len(gx)-1):
    for b in range(len(gy)-1):
        q=[(a,b),(a+1,b),(a+1,b+1),(a,b+1)]
        if all(k in idx for k in q): faces.append(tuple(idx[k] for k in q))
me=bpy.data.meshes.new('WS203_Lot3_S_strip_soil_underlay_hidden_UNVERIFIED'); me.from_pydata(verts,[],faces); me.update()
ob=bpy.data.objects.new(me.name,me)
src=[o for o in bpy.data.objects if o.name.startswith('WS191c_Lot3_S_strip_back_lawn')][0]
for c in src.users_collection: c.objects.link(ob)
me.materials.append(src.material_slots[0].material)
for p in me.polygons: p.use_smooth=True
print('F203b underlay verts',len(verts),'faces',len(faces),'z %.3f..%.3f'%(min(v[2] for v in verts),max(v[2] for v in verts)),flush=True)
