"""wi part 2: lawn shoulder on the S side of walk 1132693523 (walk S edge stood 8-11 cm proud
of the LiDAR patch over x 210.5-212.6 -> 'raised plate' from the W eye). Raise patch verts only
(never lower) to walk_S_z - 0.02 within 1.2 m of the S edge, smoothstep to 0 by 2.2 m."""
import bpy, os, json
import numpy as np
os.chdir('/workspace/nj-scenes/montclair-state')
SAVE=os.environ.get('SAVE')=='1'
P=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
W=bpy.data.objects['WD_walk_1132693523_UNVERIFIED']
mwW=W.matrix_world
pts={}
for v in W.data.vertices:
    c=mwW@v.co
    k=round(c.x,1)
    if k not in pts or c.y<pts[k][0]: pts[k]=(c.y,c.z)
xs=np.array(sorted(pts)); sy=np.array([pts[k][0] for k in xs]); sz=np.array([pts[k][1] for k in xs])
mw=P.matrix_world; inv=mw.inverted()
X0,X1=xs.min()+0.3,213.3
rep={'raised':0,'max_raise':0.0,'list':[]}
for v in P.data.vertices:
    c=mw@v.co
    if not (X0<=c.x<=X1): continue
    ys=float(np.interp(c.x,xs,sy)); zs=float(np.interp(c.x,xs,sz))
    d=ys-c.y
    if d<-0.15 or d>2.2: continue
    w=1.0 if d<=1.2 else 1-((d-1.2)/1.0)**2*(3-2*((d-1.2)/1.0))
    tgt=zs-0.02
    if tgt<=c.z: continue
    nz=c.z+w*(tgt-c.z)
    rep['list'].append([round(c.x,2),round(c.y,2),round(c.z,3),round(nz,3)])
    c.z=nz; v.co=inv@c
    rep['raised']+=1; rep['max_raise']=max(rep['max_raise'],nz-rep['list'][-1][2])
P.data.update()
P['wi_obj']=1
json.dump(rep,open('data/wi/shoulder_report2.json','w'),indent=0)
print('REP',rep['raised'],rep['max_raise'],rep['list'])
if SAVE: bpy.ops.wm.save_mainfile(compress=True); print('SAVED')
