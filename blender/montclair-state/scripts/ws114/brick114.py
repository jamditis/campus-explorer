# ws114: re-profile the WS112 E brick link as a designed walk (smooth long profile, 2% cross-slope), rebuild WS113 proxy.
import bpy, bmesh, numpy as np, os
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
o=O('WS112_CollegeAve_S_E_walk_N_brick'); me=o.data
assert o.matrix_world.is_identity or True
V=me.vertices; top=np.array([V[i].co[:] for i in range(120)]).reshape(24,5,3)
cen=top[:,2,:2]; s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(cen,axis=0),axis=1))]
dc=np.array([dtm(*c) for c in cen])
p=np.polyfit(s,dc,3); fit=np.polyval(p,s)+0.05
z0=top[0,2,2]
k=0.04; zc=k*np.logaddexp(z0/k,fit/k)   # soft max: level landing off the ws111 end, then the designed ramp
zc[0]=z0; zc+= (z0-zc[0])
# remove the softmax lift at row 0 smoothly
lift=zc[0]-z0
print('B114 s',s.round(2).tolist()); print('B114 dtm',dc.round(3).tolist()); print('B114 zc',zc.round(3).tolist())
new=top.copy()
for r in range(24):
    w=1.0 if r>=3 else (3-2*(r/3))*(r/3)**2   # cross-slope fades in over rows 0-3 (row 0 = shared flat ws111 end row)
    if r==0: continue
    c=top[r,2,:2]; d=top[r,4,:2]-top[r,0,:2]; d/=np.linalg.norm(d)
    for kk in range(5):
        t=float(np.dot(top[r,kk,:2]-c,d))
        new[r,kk,2]=zc[r]+0.02*t*w
for r in range(24):
    for kk in range(5): V[r*5+kk].co.z=new[r,kk,2]
# skirts: match xy
tops={(round(v[0],3),round(v[1],3)):v[2] for v in new.reshape(-1,3)}
n=0
for i in range(120,len(V)):
    key=(round(V[i].co.x,3),round(V[i].co.y,3))
    if key in tops: V[i].co.z=tops[key]-0.30; n+=1
print('B114 skirts',n,len(V)-120); me.update()
# cross/long slope report
for r in (1,5,10,15,20,23):
    print('B114 row',r,'cross %.2f%%'%(100*(new[r,4,2]-new[r,0,2])/np.linalg.norm(new[r,4,:2]-new[r,0,:2])))
g=np.diff(zc)/np.diff(s); print('B114 long grade % min/max',(100*g.min()).round(2),(100*g.max()).round(2),'2nd diff max',np.abs(np.diff(g)).max().round(4))
# rebuild proxy (gn113 PAV tops + fan113 paving tops inside the fill)
pv=bpy.data.objects['WS113_paving_tops_proxy']; n_old=len(pv.data.polygons)
bm=bmesh.new()
PAV=['WS112_CollegeAve_S_E_walk_N_brick','WS112_W_branch_walk','WS111_CollegeAve_S_E_walk_gap','WS111_CollegeAve_S_W_walk_gap','WS111_CollegeAve_E_corner_apron','WS111_CollegeAve_W_corner_apron']
def addtops(ob,filt=None):
    t=bmesh.new(); t.from_mesh(ob.data); t.transform(ob.matrix_world); t.normal_update()
    bad=[f for f in t.faces if abs(f.normal.z)<0.5 or (filt and not filt(f))]
    bmesh.ops.delete(t,geom=bad,context='FACES'); nk=len(t.faces)
    m=bpy.data.meshes.new('tmp'); t.to_mesh(m); t.free(); bm.from_mesh(m); bpy.data.meshes.remove(m); return nk
for pn in PAV: addtops(O(pn))
fill=O('WS113_terrain_fan_fill'); cells=set()
for f in fill.data.polygons:
    c=fill.matrix_world@f.center; cells.add((int(np.floor(c.x)),int(np.floor(c.y))))
X0,X1,Y0,Y1=-251,-118,-253,-156
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; gp=O('WS110_ground_patch'); B=[]
for ob in bpy.data.objects:
    if ob.type!='MESH' or ob.hide_render or ob in (t,fill,gp,pv) or ob.name in PAV or any(ob.name.startswith(q) for q in PAV): continue
    nm=ob.name
    if nm.startswith(('T_','Terrain','Context_skirt','OZ_','WS111_entrance','WS107_Chapin','WS108','Chapin')) or 'roof' in nm.lower() or 'wall' in nm.lower() or 'tree' in nm.lower() or 'shrub' in nm.lower(): continue
    if ob.modifiers: continue
    bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    if len(ob.data.polygons)>200000: continue
    def fl(f):
        c=f.calc_center_median()
        return f.normal.z>=0.7 and (int(np.floor(c.x)),int(np.floor(c.y))) in cells and abs(c.z-dtm(c.x,c.y))<=0.6
    nk=addtops(ob,fl)
    if nk: B.append((nm[:40],nk))
bm.to_mesh(pv.data); bm.free(); pv.data.update()
print('B114 proxy',n_old,'->',len(pv.data.polygons),B)
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('B114 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('B114 SAVED',SAVE)
