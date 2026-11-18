import bpy,bmesh,numpy as np,os,json
from mathutils import Vector
src=open('/workspace/nj-scenes/montclair-state/scripts/ws102/apply102.py').read(); exec(src[:src.index('mats={')])
SSf=np.arange(-1,S1+1.01,0.5); FR=[frame(s) for s in SSf]; PP=np.array([f[0] for f in FR]); NN=np.array([f[1] for f in FR])
def so(q):
    dd=np.hypot(*(PP-q).T); a=int(np.argmin(dd)); return SSf[a],(q-PP[a])@NN[a]
road=[o for o in bpy.data.objects if o.name.startswith('WS102_CollegeAve_S_carriageway')][0]
from mathutils.bvhtree import BVHTree
bvh=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
rep={}
for nm,mode in (('UA_CollegeAve_spur_1557427669_UNVERIFIED','spur'),('Roads_OSM','in'),('Footpaths_OSM','in')):
    o=bpy.data.objects[nm]; mw=o.matrix_world; mwi=road.matrix_world.inverted()
    bm=bmesh.new(); bm.from_mesh(o.data); dl=[]; dz=[]
    for f in bm.faces:
        c=mw@f.calc_center_median(); s,off=so(np.array(c[:2]))
        if s<-0.3 or s>S1-0.2: continue
        if mode=='spur': hit= abs(off)<8 and s<S1-0.6
        else: hit= eE(s)-0.1<=off<=EW+0.2
        if hit:
            dl.append(f); h=bvh.ray_cast(mwi@Vector((c.x,c.y,c.z+6)),Vector((0,0,-1)),14)
            if h[0] is not None: dz.append(c.z-(road.matrix_world@h[0]).z)
    bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update()
    rep[nm]=dict(n=len(dl),dz_med=float(np.median(dz)) if dz else None,dz_max=float(max(dz)) if dz else None)
    print('F102',nm,rep[nm])
json.dump(rep,open(B+'fixed102.json','w'),indent=1)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('F102 SAVED')
