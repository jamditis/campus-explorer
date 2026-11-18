# ws187 (Nov 16 ~12:45 PM ET) — UNIFY #90 leftover: diagonal fold / dark seam lines at the Lot 3 W shoulder ↔ bank toe (W eye view, ws186f 1152).
# probe187 (ray casts through the dark lines): four stacked lawn sheets meet there — WS162 shoulder lawn (1 m, flat-shaded), WS186 bank sheet
# (0.25 m), WS169c lawn bridge and WS163 patch (1 m) — each on a slightly different surface, so overlaps show as thin shadowed steps and the
# 1 m facets catch the low sun as a fold. v1 (re-seat all four on the DTM with 1 cm stacking) removed the fold but left straight 1 m seam lines
# (renders/wip/20261116-1238_*_ws187a_subset.jpg) -> v2: ONE 0.25 m lawn sheet over x -320..-307.5, y -236.5..-227.5 on the same 2023 0.5 m DTM
# (3x3 mean) fix184/fix186 used; boundary ring flush (-5 mm) to the neighbour surface closest to the DTM, feathered to the DTM over 1 m; never
# above paving -3 cm (lifted to a paving edge within 0.45 m); the four old sheets' verts inside (0.4 m in) pushed 6 cm under it.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def _bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); bm=bmesh.new(); bm.from_object(o,dg); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
_D=np.load('/workspace/nj-scenes/montclair-state/prep/ws181_lot36/dtm181_0p5m.npy')
def _dtm(x,y):
    c=int(round((x+355)/0.5)); r=int(round((-200-y)/0.5)); w=_D[max(r-1,0):r+2,max(c-1,0):c+2]
    return float(np.nanmean(w)) if np.isfinite(w).any() else None
_NB=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS186_Lot3_S_bank_lawn','WS162_Lot3_W_shoulder_lawn','WS169c','WS163_ground_patch_W_of_WS110','WS167_ground_W'))]
_PVo=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS162_Lot3_W_walk_band','WS163_Lot3_aisle_S_drive','WS162_Lot3_S_end_apron','WS170b_Lot3_S_end_curb','WS162_Lot3_asphalt','WS181_Lot36_asphalt','WS162_Lot3_W_curb'))]
_SRC=next((o for o in _NB if o.name.startswith('WS186_Lot3_S_bank_lawn')),None)
if _SRC is None: print('FIX187 SKIPPED WS186 sheet missing (chain fix186 first)',flush=True)
else:
    TN=[_bvh(o) for o in _NB]; TP=[_bvh(o) for o in _PVo]
    def near(x,y,zref):
        best=None
        for t in TN:
            z=140.0
            while True:
                h=t.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),60.0)
                if h[0] is None: break
                if best is None or abs(h[0].z-zref)<abs(best-zref): best=h[0].z
                z=h[0].z-0.002
        return best
    def ptop(x,y,zref):
        best=None
        for t in TP:
            h=t.ray_cast(Vector((x,y,140.0)),Vector((0,0,-1)),60.0)
            if h[0] is not None and h[0].z<zref+0.6 and (best is None or h[0].z>best): best=h[0].z
        return best
    XA,XB,YA,YB,SS=-320.0,-307.5,-236.5,-227.5,0.25
    xs=np.arange(XA,XB+1e-6,SS); ys=np.arange(YA,YB+1e-6,SS); nx=len(xs); vs=[]; fs=[]; npv=0; nl=0; nd=0
    for y in ys:
        for x in xs:
            edge=(x<XA+1e-6 or x>XB-1e-6 or y<YA+1e-6 or y>YB-1e-6)
            zd=_dtm(x,y); tn=near(x,y,zd if zd is not None else 116.5)
            if zd is None: nd+=1; zd=tn if tn is not None else 116.5
            z=zd
            if tn is not None:
                d=min(x-XA,XB-x,y-YA,YB-y); wgt=min(1.0,d/1.0)
                z=(tn-0.005) if edge else (tn+wgt*(zd-tn))
            tp=ptop(x,y,z)
            if tp is not None and z>tp-0.03: z=tp-0.03; npv+=1
            elif tp is None:
                for t in TP:   # v3: lift toward the paving edge with a linear falloff over 0.8 m (v2's hard 0.45 m lift made a 42-deg crease row, probe187 closeup)
                    h=t.find_nearest(Vector((x,y,z)),0.8)
                    if h[0] is not None and h[0].z-0.015>z and h[0].z<z+0.4:
                        dd=(Vector((x,y))-h[0].xy).length; z=z+max(0.0,1.0-dd/0.8)*(h[0].z-0.015-z); nl+=1; break
            vs.append((float(x),float(y),float(z)))
    for j in range(len(ys)-1):
        for i in range(nx-1): a=j*nx+i; fs.append((a,a+1,a+nx+1,a+nx))
    nm=bpy.data.meshes.new('WS187_Lot3_W_toe_lawn_DTM2023_UNIFY90'); nm.from_pydata(vs,[],fs); nm.update()
    for p in nm.polygons: p.use_smooth=True
    for m in _SRC.data.materials: nm.materials.append(m)
    ob=bpy.data.objects.new('WS187_Lot3_W_shoulder_toe_lawn_DTM2023_UNIFY90',nm)
    for c in _SRC.users_collection: c.objects.link(ob)
    tf=BVHTree.FromPolygons([Vector(v) for v in vs],fs); cnt={}
    for o in _NB:
        M=o.matrix_world; Mi=M.inverted(); c=0
        for v in o.data.vertices:
            w=M@v.co
            if not (XA+0.4<w.x<XB-0.4 and YA+0.4<w.y<YB-0.4): continue
            h=tf.ray_cast(Vector((w.x,w.y,w.z+2.0)),Vector((0,0,-1)),4.0)
            if h[0] is not None and w.z>h[0].z-0.06: v.co=Mi@Vector((w.x,w.y,h[0].z-0.06)); c+=1
        if c: o.data.update(); cnt[o.name[:26]]=c
    print('FIX187 toe sheet verts %d faces %d nodtm %d under-paving %d lifted-to-edge %d neighbours pushed %s'%(len(vs),len(fs),nd,npv,nl,cnt),flush=True)
