# qd: painted-window HAIRLINE slivers qb_corner missed (qb flagged overlaps > 3 cm only). E.g. Calcia face 66 at the west
# step = the thin dark vertical line in the qc close-up. Slot-0 wall faces whose U range overlaps a painted window column
# by only 3 mm..3 cm (no full column) and whose V range overlaps a painted row -> slot 1 (qb no-window copy).
# Original indices in prop qd_sliver_faces (merged per run); REVERT=1 restores slot 0. Mask maths = qb_corner CFG. UNVERIFIED.
import bpy, os, math, json
REV=os.environ.get('REVERT')=='1'
CFG={'Dickson':('Dickson Hall walls',2.4,0.5,1.9,0.0,4.6,1.0,3.6),'Calcia':('Calcia Hall walls',2.4,0.75,1.65,0.1,4.4,0.6,3.8)}
for key in os.environ.get('QD_SLIVER_OBJS','Calcia,Dickson').split(','):
    OBN,UP,ULO,UHI,VOF,VP,VLO,VHI=CFG[key]; o=bpy.data.objects[OBN]; me=o.data; uv=me.uv_layers['facade']
    if REV:
        for fi in json.loads(o.get('qd_sliver_faces','[]')): me.polygons[fi].material_index=0
        if 'qd_sliver_faces' in o: del o['qd_sliver_faces']
        print('QD_SLIVER reverted',key); continue
    WT=float(o.get('win_top',99))
    def rowhit(v0,v1):
        a=max(v0,0.8); b=min(v1,WT)
        if b-a<0.03: return False
        for k in range(math.floor((a-VOF)/VP)-1, math.floor((b-VOF)/VP)+2):
            lo=VOF+VP*k+VLO; hi=VOF+VP*k+VHI
            if min(b,hi)-max(a,lo)>0.03: return True
        return False
    ch=[]
    for p in me.polygons:
        if p.material_index!=0 or abs(p.normal.z)>0.3 or p.area<0.005: continue
        U=[uv.data[li].uv.x for li in p.loop_indices]; V=[uv.data[li].uv.y for li in p.loop_indices]
        u0,u1=min(U),max(U); rng=range(math.floor(u0/UP)-1, math.floor(u1/UP)+2)
        full=[k for k in rng if UP*k+ULO>=u0-1e-3 and UP*k+UHI<=u1+1e-3]
        if full: continue
        ow=[min(u1,UP*k+UHI)-max(u0,UP*k+ULO) for k in rng]
        if any(0.003<w<=0.03 for w in ow) and rowhit(min(V),max(V)): ch.append(p.index)
    print('QD_SLIVER',key,'candidates',len(ch),ch[:40])
    if os.environ.get('QD_SLIVER_APPLY','1')=='1':
        assert len(me.materials)==2
        for fi in ch: me.polygons[fi].material_index=1
        old=json.loads(o.get('qd_sliver_faces','[]')); o['qd_sliver_faces']=json.dumps(sorted(set(old)|set(ch))); print('QD_SLIVER applied',key,len(ch),'total',len(set(old)|set(ch)))
