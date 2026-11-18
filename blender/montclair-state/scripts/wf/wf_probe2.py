import bpy, json, numpy as np, os
from mathutils import Vector
os.chdir('/workspace/nj-scenes/montclair-state')
D=np.load('data/wf/east_dorm_dtm_1m.npz'); filled=D['dtm_filled']; X0,X1,Y0,Y1,_=D['extent']
def dtm(x,y):
    i=int(np.floor(x-X0)); j=int(np.floor(y-Y0))
    if 0<=i<filled.shape[1]-1 and 0<=j<filled.shape[0]-1:
        fx=x-X0-i; fy=y-Y0-j
        return float((1-fx)*(1-fy)*filled[j,i]+fx*(1-fy)*filled[j,i+1]+(1-fx)*fy*filled[j+1,i]+fx*fy*filled[j+1,i+1])
    return None
# find N door related objects
names=[n for n in bpy.data.objects.keys() if 'Bohn' in n and ('door' in n.lower() or 'Door' in n or 'N_' in n or 'landing' in n.lower())]
print('BOHN_DOORISH',sorted(names)[:40])
out={}
for nm in sorted(names):
    o=bpy.data.objects[nm]
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    out[nm]=dict(cx=round(sum(p.x for p in bb)/8,2),cy=round(sum(p.y for p in bb)/8,2),
                 zmin=round(min(p.z for p in bb),3),zmax=round(max(p.z for p in bb),3),
                 xmin=round(min(p.x for p in bb),2),xmax=round(max(p.x for p in bb),2),
                 ymin=round(min(p.y for p in bb),2),ymax=round(max(p.y for p in bb),2))
# stair verts detail
st=bpy.data.objects['WD_Bohn_N_steps_313029912_UNVERIFIED']
V=[st.matrix_world@v.co for v in st.data.vertices]
print('STEPS n',len(V),'z',round(min(p.z for p in V),3),round(max(p.z for p in V),3))
# sample along stair centerline by y
for y in np.linspace(min(p.y for p in V), max(p.y for p in V), 8):
    near=[p for p in V if abs(p.y-y)<0.4]
    if not near: continue
    x=sum(p.x for p in near)/len(near); z=sum(p.z for p in near)/len(near)
    print('stair y',round(y,2),'x',round(x,2),'z',round(z,3),'dtm',round(dtm(x,y) or -1,3),'dz_top',round(z-0.0-(dtm(x,y) or 0),3))
L=bpy.data.objects['TK_Bohn_landing_N_steps_UNVERIFIED']
LV=[L.matrix_world@v.co for v in L.data.vertices]
print('LANDING',[(round(p.x,2),round(p.y,2),round(p.z,3)) for p in LV])
print('landing dtm at corners:')
for p in LV:
    print(' ',round(p.x,2),round(p.y,2),round(p.z,3),'dtm',dtm(p.x,p.y),'dz', (dtm(p.x,p.y) or 0)-p.z)
# W walk vs dtm
w=bpy.data.objects['WD_walk_1132693523_UNVERIFIED']
WV=[w.matrix_world@v.co for v in w.data.vertices]
dzs=[(dtm(p.x,p.y) or 0)-p.z for p in WV]
print('W_walk dz_to_dtm min/med/max',round(min(dzs),3),round(float(np.median(dzs)),3),round(max(dzs),3))
w2=bpy.data.objects['WD_walk_600258640_UNVERIFIED']
WV2=[w2.matrix_world@v.co for v in w2.data.vertices]
dzs2=[(dtm(p.x,p.y) or 0)-p.z for p in WV2]
print('walk600 dz_to_dtm min/med/max',round(min(dzs2),3),round(float(np.median(dzs2)),3),round(max(dzs2),3))
# N door glass/frame
for nm in sorted(bpy.data.objects.keys()):
    if 'Bohn' in nm and 'door' in nm.lower() and ('N' in nm or 'n_' in nm):
        o=bpy.data.objects[nm]
        if o.type!='MESH': continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('DOOR',nm,'z',round(min(p.z for p in bb),3),round(max(p.z for p in bb),3),'xy',round(sum(p.x for p in bb)/8,2),round(sum(p.y for p in bb)/8,2))
json.dump(out,open('data/wf/bohn_doorish.json','w'),indent=1)
print('n doorish',len(out))
