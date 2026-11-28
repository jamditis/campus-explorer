# ws274 (merge208 CHAIN, on main ws273c): College Ave N curb + concrete gutter pan along the police-lawn side.
# Evidence: NJ 2020 0.1 m ortho (scripts/ws269/url269.txt): a light concrete band along the N edge of College Ave at y ~ -19.3...-21
# for x ~ -385...-337 (sidewalk/curb line along the police lawn foot, parking bay in front of the police building).
# Curb: 15 cm reveal, 15 cm wide top, back face 0.40 m deep; gutter pan 0.45 m wide, +6 mm over the asphalt, dished 1.5 cm.
# The curb face sits 0.15 m inside the WS268 paving N outline. No paving or terrain vertices edited (raise-only, AGENTS.md rule 6).
# UNVERIFIED: reveal height, gutter width (no photo; ortho shows a light band only).
import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F274A'; OB=bpy.data.objects
NC='WS274_CollegeAve_N_curb_ortho2020_UNVERIFIED'; NG='WS274_CollegeAve_N_gutter_pan_UNVERIFIED'
if OB.get(NC): raise SystemExit('F274A already applied')
pav=OB['WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED']
bm=bmesh.new(); bm.from_mesh(pav.data); bm.transform(pav.matrix_world)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.normal.z<0.5],context='FACES')
TP=BVHTree.FromBMesh(bm)
# N outline: boundary edges of the top, sampled per x as the max y
E=[e for e in bm.edges if len(e.link_faces)==1]
X0,X1=-384.0,-332.0   # v3 (ws274c): runs on past the hatch to the red-roof building corner
xs=np.arange(X0,X1+0.01,0.5); ye=[]
for x in xs:
    best=None
    for e in E:
        a,b=e.verts[0].co,e.verts[1].co
        if (a.x-x)*(b.x-x)<=0 and abs(a.x-b.x)>1e-6:
            t=(x-a.x)/(b.x-a.x); y=a.y+t*(b.y-a.y)
            if y>-30 and (best is None or y>best): best=y
    ye.append(best)
bm.free()
ye=np.array([np.nan if v is None else v for v in ye])
ok=~np.isnan(ye); ye=np.interp(xs,xs[ok],ye[ok])
# smooth (removes the 1 m walk-end jog at x -357...-355 so the curb reads as one straight run), keep it inside the paving
k=np.exp(-0.5*(np.arange(-6,7)*0.5/1.2)**2); k/=k.sum()
ys=np.convolve(np.pad(ye,6,mode='edge'),k,mode='valid')
# v2 (ws274b): no clamp to the outline; at the police S walk end (x -358.6...-354.4) the curb drops to a 2 cm lip (curb cut)
CUT=(-358.6,-354.4)
print(TAG,'N edge y range',round(ys.min(),2),round(ys.max(),2),'max smooth shift',round(float(np.max(ye-ys)),2),flush=True)
def pz(x,y):
    r=TP.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return None if r[0] is None else r[0].z
P=[Vector((x,y)) for x,y in zip(xs,ys)]
T=[]
for i in range(len(P)):
    a=P[max(0,i-1)]; b=P[min(len(P)-1,i+1)]; d=(b-a).normalized(); T.append(Vector((d.y,-d.x)))  # inward (south) normal
def mat(*keys):
    for kk in keys:
        for m in bpy.data.materials:
            if kk in m.name: return m
col=pav.users_collection[0]
# ---- curb: back line at edge-0.0, face line at edge-0.15 (inward)
bm=bmesh.new(); rows=[]; miss=0
for p,n in zip(P,T):
    pf=p+n*0.15; pg=p+n*0.60
    zf=pz(pf.x,pf.y); zb=pz(p.x+n.x*0.02,p.y+n.y*0.02)
    if zf is None: miss+=1; zf=rows[-1][-1] if rows else 119.0
    if zb is None: zb=zf
    rv=0.15
    if CUT[0]-0.8<p.x<CUT[1]+0.8:
        t=min(1.0,max(0.0,min(p.x-(CUT[0]-0.8),(CUT[1]+0.8)-p.x)/0.8)); rv=0.15-0.13*t
    # v4 (ws274d): reveal tapers to 2 cm over the last 1.2 m at both ends so the curb dies into the grade instead of a free end
    te=min(p.x-X0,X1-p.x)
    if te<1.2: rv=min(rv,0.02+0.13*max(0.0,te)/1.2)
    top=max(zf,zb)+rv
    vb0=bm.verts.new((p.x,p.y,top-0.40)); vb1=bm.verts.new((p.x,p.y,top))
    vf1=bm.verts.new((pf.x,pf.y,top)); vf0=bm.verts.new((pf.x,pf.y,zf-0.03))
    rows.append((vb0,vb1,vf1,vf0,zf))
for r0,r1 in zip(rows[:-1],rows[1:]):
    bm.faces.new((r0[0],r1[0],r1[1],r0[1]))   # back
    bm.faces.new((r0[1],r1[1],r1[2],r0[2]))   # top
    bm.faces.new((r0[2],r1[2],r1[3],r0[3]))   # face (road side)
for r in (rows[0],rows[-1]):
    bm.faces.new((r[0],r[1],r[2],r[3]))       # end caps
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
bm.normal_update()
tops=[f for f in bm.faces if abs(f.normal.z)>0.5]
if sum(f.normal.z for f in tops)<0:
    for f in bm.faces: f.normal_flip()
# small bevel-like chamfer on the top front edge is skipped (1 cm at this scale reads only in close-up)
me=bpy.data.meshes.new(NC); bm.to_mesh(me); bm.free()
mc=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED') or mat('WS27_curb','ge_walk_concrete')
if mc: me.materials.append(mc)
oc=OB.new(NC,me); col.objects.link(oc)
oc['ws274']='College Ave N curb along the police lawn; ortho 2020 light band; reveal 15 cm UNVERIFIED'
print(TAG,'curb rows',len(rows),'miss',miss,'mat',mc and mc.name,flush=True)
# ---- gutter pan: from the curb face 0.45 m into the road, +6 mm at the outer edge, dished -9 mm (net) mid
bm=bmesh.new(); G=[]; gm=0
for p,n in zip(P,T):
    row=[]
    for s,dz in ((0.15,0.006),(0.36,0.004),(0.60,0.006)):
        q=p+n*s; z=pz(q.x,q.y)
        if z is None: gm+=1; z=row[-1].co.z-dz if row else 119.0
        row.append(bm.verts.new((q.x,q.y,z+dz)))
    G.append(row)
for r0,r1 in zip(G[:-1],G[1:]):
    for j in range(2): bm.faces.new((r0[j],r0[j+1],r1[j+1],r1[j]))
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new(NG); bm.to_mesh(me); bm.free()
mg=bpy.data.materials.get('WS274_gutter_pan_concrete_WS27tone')
if mg is None and mc:
    mg=mc.copy(); mg.name='WS274_gutter_pan_concrete_WS27tone'
    try:
        bsdf=[nd for nd in mg.node_tree.nodes if nd.type=='BSDF_PRINCIPLED'][0]
        if not bsdf.inputs['Base Color'].is_linked:
            c=bsdf.inputs['Base Color'].default_value; bsdf.inputs['Base Color'].default_value=(c[0]*0.82,c[1]*0.82,c[2]*0.80,1)
        bsdf.inputs['Roughness'].default_value=0.85
    except Exception as ex: print(TAG,'gutter tint skipped',ex)
if mg: me.materials.append(mg)
og=OB.new(NG,me); col.objects.link(og)
og['ws274']='concrete gutter pan 0.45 m in front of the N curb; width UNVERIFIED'
print(TAG,'gutter faces',len(me.polygons),'miss',gm,'mat',mg and mg.name,flush=True)
for o in (oc,og):
    o.hide_render=False; o.hide_viewport=False
