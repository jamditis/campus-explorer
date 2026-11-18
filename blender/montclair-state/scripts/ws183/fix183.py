# ws183 — UNIFY #88 follow-up (runs AFTER ws181/fix181.py + ws182/fix182.py): Lot 36 SE corner / bank toe y -234..-220.
# Evidence (scripts/ws183/probe183a.out, 0.1 m per-object BVH stack): the WS167 Sprague E service lane runs on UNDER the Lot 36 asphalt and the
# WS162 bank-toe lawn S of fix182's window, only 0-4 mm below them -> (1) the lane pokes THROUGH the lot at (-319.9..-319.6,-230.0..-230.3)
# (= fix181 'BAD' points, the grey flap in the ws182 top-down) and at the SE edge (-316.6..-316.1,-230..-230.8) (the 'sliver'); (2) the bank lawn
# z-fights the lane along the toe x -316.1..-315.5, y -226..-231 (the ragged 'lawn jag' line in the top-down). Real ground (REFS §1/§6, 2023 LiDAR
# + 2020 ortho): one flat paved lot surface running to the straight bank toe; the lane is not a separate visible strip there.
# Fix: lane verts that are COVERED by the lot or the bank lawn (top within 0.30 m above) in x -322..-312, y -234.5..-220 drop 4 cm
# (taper 0 at y -220 -> full at y -224.5); nothing visible moves.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def ob(pre): return next((o for o in bpy.data.objects if o.name.startswith(pre)),None)
LOT=ob('WS181_Lot36_asphalt'); LANE=ob('WS167_Sprague_E_service_lane'); BANK=ob('WS162_Lot3_W_shoulder_lawn')
def bvh(o):
    bm=bmesh.new(); bm.from_object(o,dg); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
if LOT and LANE and BANK:
    print('FIX183 lane mods',[m.type for m in LANE.modifiers],'verts',len(LANE.data.vertices),flush=True)
    TC=[bvh(LOT),bvh(BANK)]
    me=LANE.data; M=LANE.matrix_world; Mi=M.inverted(); n=0; nl=0; nb=0
    for v in me.vertices:
        w=M@v.co
        if not (-322<w.x<-312 and -234.5<w.y<-220): continue
        cov=False
        for k,t in enumerate(TC):
            h=t.ray_cast(Vector((w.x,w.y,w.z+0.30)),Vector((0,0,-1)),0.60)
            if h[0] is not None: cov=True; nl+=(k==0); nb+=(k==1); break   # lot/bank present over (or a hair under = the poke) this vert
        if not cov: continue
        f=min(1.0,max(0.0,(-220.0-w.y)/4.5)); 
        if f<=0: continue
        v.co=Mi@Vector((w.x,w.y,w.z-0.04*f)); n+=1
    me.update()
    # check: lane above-or-within-5 mm of lot/bank tops in the window
    TL=bvh(LANE); bad=0; tot=0
    import numpy as _np
    for y in _np.arange(-234.4,-220.0,0.1):
        for x in _np.arange(-321.9,-312.0,0.1):
            hl=TL.ray_cast(Vector((x,y,140)),Vector((0,0,-1)))
            if hl[0] is None: continue
            zs=[t.ray_cast(Vector((x,y,140)),Vector((0,0,-1)))[0] for t in TC]; zs=[z.z for z in zs if z is not None]
            if not zs: continue
            tot+=1; bad+=(hl[0].z>max(zs)-0.005)
    # (3) SE corner: WS169c lawn bridge sits 1-4 mm under the lot edge at (-317,-232.4..-233) and the WS163 patch z-fights the bridge
    #     (0-3 mm) along y -232.2..-233.8 -> covered verts of the lower sheet drop: bridge under lot 3 cm, WS163 patch under bridge 2 cm.
    BR=ob('WS169c_Lot3_S_end_lawn_bridge'); GP=ob('WS163_ground_patch_W_of_WS110')
    def drop(o,cover,dz,box):
        if not (o and cover): return 0
        tc=bvh(cover); me2=o.data; M2=o.matrix_world; M2i=M2.inverted(); c=0
        for v in me2.vertices:
            w=M2@v.co
            if not (box[0]<w.x<box[1] and box[2]<w.y<box[3]): continue
            h=tc.ray_cast(Vector((w.x,w.y,w.z+0.10)),Vector((0,0,-1)),0.20)
            if h[0] is not None: v.co=M2i@Vector((w.x,w.y,w.z-dz)); c+=1
        me2.update(); return c
    print('FIX183 mats bridge',[m.name for m in BR.data.materials][:2] if BR else None,'patch',[m.name for m in GP.data.materials][:2] if GP else None,flush=True)
    print('FIX183 bridge verts under lot dropped',drop(BR,LOT,0.03,(-322,-312,-234.5,-229)),'patch verts under bridge dropped',drop(GP,BR,0.02,(-322,-310,-235,-231)),flush=True)
    print('FIX183 lane verts dropped',n,'(under lot %d / bank %d)'%(nl,nb),'check lane-within-5mm-of-top %d/%d'%(bad,tot),flush=True)
else:
    print('FIX183 SKIPPED missing',[LOT is None,LANE is None,BANK is None],flush=True)
