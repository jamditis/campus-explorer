"""we: Stone footway / Stone Street junction wedge (x~143-145, y~293.6-296.6): WV lawn sat ~8-15 cm under the two
walk slabs around it. Raise-only ease of WV (and any top-most ground sheet) to nearest slab top -2.5 cm within 1.0 m,
fading to 0 at 2.4 m; verts under a slab lifted to slab -5 cm. Box-limited; slab pokes checked and backed off;
soil strip 546643369 verts in the box re-seated if buried >1 cm; grass points re-snapped."""
import bpy,numpy as np,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects
import os
BX=tuple(float(v) for v in os.environ.get('BOX','141.5,146.5,292.0,298.0').split(',')); D_FULL=1.0; D_OUT=float(os.environ.get('DOUT','2.4')); LIFT=float(os.environ.get('LIFT','0.025')); CAP=0.20
TAG=os.environ.get('TAG','wedge'); ONLYG=os.environ.get('ONLYG',''); STRIPS=os.environ.get('STRIPS','546643369').split(',')
def dg(): return bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg()); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
def top(B,x,y):
    z=[h[0].z for b in B for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
SLn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QW_footway_','QS_service_','TR_footway','SG_'))]
GRDn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone','WN_south','WO_gully','Terrain_LiDAR','QW_DTM','WU_rich','WT_rich','WF_east','RZ2_','WA0_','SA_ground_lower_patch'))]
def inbox(c,m=0): return BX[0]-m<=c.x<=BX[1]+m and BX[2]-m<=c.y<=BX[3]+m
# slab objects overlapping the box only
def bbx(o):
    c=np.array([o.matrix_world@Vector(b) for b in o.bound_box]); return c[:,0].min(),c[:,0].max(),c[:,1].min(),c[:,1].max()
SLn=[n for n in SLn if (lambda b:(b[0]<BX[1]+3 and b[1]>BX[0]-3 and b[2]<BX[3]+3 and b[3]>BX[2]-3))(bbx(O[n]))]
GRDn=[n for n in GRDn if (lambda b:(b[0]<BX[1] and b[1]>BX[0] and b[2]<BX[3] and b[3]>BX[2]))(bbx(O[n]))]
GRDn=[n for n in GRDn if n.startswith(ONLYG)] if ONLYG else GRDn
print('SL',SLn,'GRD',GRDn,BX,LIFT,flush=True)
SL=[bvh(O[n]) for n in SLn]
def near_slab(x,y):
    for r in np.arange(0.1,D_OUT+0.01,0.1):
        zs=[top(SL,x+r*np.cos(a),y+r*np.sin(a)) for a in np.linspace(0,2*np.pi,16,endpoint=False)]
        zs=[z for z in zs if z is not None]
        if zs: return r,max(zs)
    return None
def gap_stats(tag):
    G=[bvh(O[n]) for n in GRDn]; e=[]
    for x in np.arange(BX[0],BX[1],0.2):
        for y in np.arange(BX[2],BX[3],0.2):
            if top(SL,x,y) is not None: continue
            ns=near_slab(x,y) if True else None
            if ns is None or ns[0]>0.45: continue
            g=top(G,x,y)
            if g is not None: e.append(ns[1]-g)
    e=np.array(e); r=dict(n=len(e),p50=round(float(np.median(e)),3),p90=round(float(np.percentile(e,90)),3),max=round(float(e.max()),3)); print('EXP',tag,r,flush=True); return r
def pokes(tag):
    G=[bvh(O[n]) for n in GRDn]; L=[]
    for x in np.arange(BX[0]-1,BX[1]+1,0.2):
        for y in np.arange(BX[2]-1,BX[3]+1,0.2):
            s=top(SL,x,y)
            if s is None: continue
            g=top(G,x,y)
            if g is not None and g>s-0.005: L.append((x,y,g-s))
    print('POKES',tag,len(L),flush=True); return L
rep={'exp0':gap_stats('before')}; rep['pk0']=len(pokes('before'))
G0=[bvh(O[n]) for n in GRDn]; PRE={}
for n in GRDn:
    o=O[n]; me=o.data; mw=o.matrix_world; mi=mw.inverted(); PRE[n]=np.array([v.co[:] for v in me.vertices]); cnt=0; mx=0
    for v in me.vertices:
        c=mw@v.co
        if not inbox(c): continue
        g=top(G0,c.x,c.y)
        if g is not None and c.z<g-0.05: continue
        s=top(SL,c.x,c.y)
        if s is not None: tgt=s-0.05
        else:
            ns=near_slab(c.x,c.y)
            if ns is None: continue
            d,sz=ns; w=0.0 if d<=D_FULL else (d-D_FULL)/(D_OUT-D_FULL); w=w*w*(3-2*w)
            tgt=(sz-LIFT)*(1-w)+c.z*w
        # fade at box edge so nothing tears
        dd=min(c.x-BX[0],BX[1]-c.x,c.y-BX[2],BX[3]-c.y); fb=min(1.0,dd/1.0)
        dz=min(max(0.0,(tgt-c.z)*fb),CAP)
        if dz>0.002: c.z+=dz; v.co=mi@c; cnt+=1; mx=max(mx,dz)
    me.update(); rep['raise_'+n[:12]]=[cnt,round(mx,3)]; print('RAISE',n,cnt,round(mx,3),flush=True)
bpy.context.view_layer.update()
L=pokes('after')
for it in range(4):
    if len(L)<=rep['pk0']: break
    for n in GRDn:
        o=O[n]; B=bvh(o); ids={}
        for x,y,d in L:
            h=B.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
            if h[2] is None: continue
            for vi in o.data.polygons[h[2]].vertices:
                if abs(o.data.vertices[vi].co.z-PRE[n][vi][2])>1e-5: ids[vi]=max(ids.get(vi,0),d+0.012)
        for vi,d in ids.items(): o.data.vertices[vi].co.z=max(PRE[n][vi][2],o.data.vertices[vi].co.z-d)
        o.data.update()
    bpy.context.view_layer.update(); L=pokes('backoff%d'%it)
rep['pk1']=len(L); rep['exp1']=gap_stats('after')
G=[bvh(O[n]) for n in GRDn]; kg=0
for g in [o for o in O if o.type=='MESH' and 'grass_points' in o.name]:
    b=bbx(g)
    if not (b[0]<BX[1] and b[1]>BX[0] and b[2]<BX[3] and b[3]>BX[2]): continue
    m=g.matrix_world; mi2=m.inverted()
    for v in g.data.vertices:
        c=m@v.co
        if not inbox(c,0.5): continue
        z=top(G,c.x,c.y)
        if z is None: continue
        if top(SL,c.x,c.y) is not None:
            if c.z>z-0.15: c.z=z-0.2; v.co=mi2@c; kg+=1
        elif abs(c.z-z)>0.01: c.z=z; v.co=mi2@c; kg+=1
    g.data.update()
rep['grass']=kg; print('GRASS',kg,flush=True)
for sid in STRIPS:
  t=O['QT_soil_edge_%s_UNVERIFIED'%sid]; mw=t.matrix_world; inv=mw.inverted(); S=bvh(O['QS_footway_%s_UNVERIFIED'%sid]); k=0
  for v in t.data.vertices:
    w=mw@v.co
    if not inbox(w,0.5) or S.find_nearest(w)[3]<0.05: continue
    z=top(G,w.x,w.y)
    if z is not None and abs(w.z-(z+0.005))>0.003: v.co=inv@Vector((w.x,w.y,z+0.005)); k+=1
  t.data.update(); rep['reseat_'+sid]=k; print('RESEAT',sid,k,flush=True)
json.dump(rep,open(f'{R}/data/wf/{TAG}_report.json','w'),indent=1)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)
