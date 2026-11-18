# Session eb (Oct 21 2026): wall-top-to-roof gap audit + fix (MAIN). Idempotent. AUDIT only by default;
# FIX=1 raises gap vertices; SAVE=1 saves; REVERT=1 restores (mesh attribute 'eb_orig_z').
# Joe 3:43 PM: "huge gap in the wall of the building next to our old office/the lab" = LiDAR-derived
# wall tops stopping below their own eave soffit/roof (same bug dT fixed on CCOM's north wing).
# Method (generalised dT): for every TOP vertex (no edge rises above it) of each '<Bldg> walls' mesh,
# ray straight up from 0.12 m inside the wall (horizontal vertex normal), skipping non-roof hits, up to 8 m.
# First hit on the SAME building's roof / eave soffit / tile course = underside. Gap = underside - z.
# Vertices with their own wall face anywhere above them (window sills / opening bottoms) are skipped.
# FIX raises gap > 0.05 m to underside - 0.01 (wall only extended under its own roof: rule 4a safe).
import bpy, os, json
from mathutils import Vector
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'; FIX=os.environ.get('FIX')=='1'
OUTJ=os.environ.get('OUTJ','/workspace/nj-scenes/montclair-state/data/eb/walltop_gap_audit_eb.json')
sc=bpy.context.scene
BLD=['School of Communication and Media','Life Hall','Morehead Hall','Finley Hall','Memorial Auditorium','Schmitt Hall','Speech Building']
FIX_BLD=os.environ.get('FIX_BLD','School of Communication and Media,Life Hall').split(',')
# Morehead/Schmitt/Memorial flagged by the audit are window openings that run up to the eave (Morehead's
# upper-row windows were closed by a first FIX in eb, verified by render) -> audit-only, never auto-fixed.
ROOFK=('roof','eave','soffit','fascia','tile','rafter')
def revert():
    n=0
    for b in BLD:
        W=bpy.data.objects.get(b+' walls')
        if not W: continue
        me=W.data; att=me.attributes.get('eb_orig_z')
        if att is None: continue
        Mi=W.matrix_world.inverted(); M=W.matrix_world
        for v,a in zip(me.vertices,att.data):
            if a.value>-1e8:
                w=M@v.co; w.z=a.value; v.co=Mi@w; n+=1
        me.attributes.remove(att); me.update()
        if 'eb_walltop_fix' in W: del W['eb_walltop_fix']
    print('REVERT restored',n,'verts')
if os.environ.get('NOREV')!='1': revert()   # NOREV=1: audit the saved state as-is (post-fix check)
bpy.context.view_layer.update()
if REVERT:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
dg=bpy.context.evaluated_depsgraph_get()
from mathutils.bvhtree import BVHTree
def roof_bvh(b,own):
    vs=[];fs=[];names=[]
    for ob in bpy.data.objects:
        nm=ob.name
        if ob.type!='MESH' or nm==own or not nm.startswith(b) or not any(k in nm.lower() for k in ROOFK): continue
        if ob.hide_render: continue
        e=ob.evaluated_get(dg); m=e.to_mesh(); M=ob.matrix_world; off=len(vs)
        vs+=[M@v.co for v in m.vertices]; fs+=[[off+i for i in p.vertices] for p in m.polygons]
        names.append(nm); e.to_mesh_clear()
    return (BVHTree.FromPolygons(vs,fs) if fs else None),names
def up_hit(o,bvh):
    p,_,_,d=bvh.ray_cast(o,Vector((0,0,1)),8.0)
    return (p.z if p is not None else None)
rep={}
for b in BLD:
    W=bpy.data.objects.get(b+' walls')
    if not W or W.type!='MESH': continue
    me=W.data; M=W.matrix_world; Mi=M.inverted(); R=M.to_3x3()
    wc=[M@v.co for v in me.vertices]
    up=[-1e9]*len(wc)
    for e in me.edges:
        a,c=e.vertices; up[a]=max(up[a],wc[c].z); up[c]=max(up[c],wc[a].z)
    vn=[Vector() for _ in wc]
    for p in me.polygons:
        n=R@p.normal
        for i in p.vertices: vn[i]+=n
    bvh,rn=roof_bvh(b,W.name)
    wbvh=BVHTree.FromPolygons(wc,[list(p.vertices) for p in me.polygons])
    if bvh is None: continue
    rows=[]
    for i,w in enumerate(wc):
        if up[i]>w.z+1e-3: continue
        n=vn[i].copy(); n.z=0
        if n.length<1e-6: continue
        n.normalize(); o=w-n*0.12+Vector((0,0,0.03))
        z=up_hit(o,bvh); nm='+'.join(x[len(b):len(b)+12] for x in rn)
        if z is None: continue
        # wall resumes above (window sill / opening bottom, not a top)? probe the wall plane horizontally
        zz=w.z+0.15; covered=False
        while zz<z-0.05 and not covered:
            q=Vector((w.x,w.y,zz))+n*0.5
            h=wbvh.ray_cast(q,-n,1.0)[0]
            if h is not None: covered=True
            zz+=0.25
        if covered: continue
        rows.append((i,round(w.x,2),round(w.y,2),round(w.z,3),round(z,3),round(z-w.z,3)))
    gaps=[r for r in rows if r[5]>0.05]
    big=[r for r in gaps if r[5]>0.5]
    rep[b]={'top_verts_under_own_roof':len(rows),'gaps_gt_0.05':len(gaps),'gaps_gt_0.5':len(big),
            'max_gap':max([r[5] for r in gaps],default=0),'gap_rows':gaps}
    rep[b]['note']='rows: vert index, x, y, wall top z, own roof/eave underside z, gap m'
    rep[b]['roof_parts']=rn
    print('AUDIT %-35s top-under-roof %4d gaps>0.05 %4d gaps>0.5 %4d max %.2f'%(b,len(rows),len(gaps),len(big),rep[b]['max_gap']))
    for r in sorted(big,key=lambda r:-r[5])[:12]: print('   BIG',r)
    if FIX and gaps and b in FIX_BLD:
        att=me.attributes.new('eb_orig_z','FLOAT','POINT')
        for a in att.data: a.value=-1e9
        for r in gaps:
            i=r[0]; w=wc[i].copy(); att.data[i].value=w.z; w.z=r[4]-0.01; me.vertices[i].co=Mi@w
        me.update(); W['eb_walltop_fix']=len(gaps)
        print('FIX raised',len(gaps),'verts on',W.name)
json.dump({'mode':'FIX' if FIX else 'AUDIT','buildings':rep},open(OUTJ,'w'),indent=1)
print('WROTE',OUTJ)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
