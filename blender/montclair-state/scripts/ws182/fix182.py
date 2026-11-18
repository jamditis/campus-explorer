# ws182 — UNIFY #88 follow-up + PLAN day 20 Lot 36 S edge (runs AFTER ws181/fix181.py).
# (a) NE drive join: the WS167 service lane's own W edge is straight; the "notches" were a 0-0.8 m sliver of the lane showing between the
#     Lot 36 E edge (intensity-mask outline) and the WS162 bank-toe lawn, which itself is straight. Real pavement is one surface to the toe:
#     move the lot's E boundary verts (y -224.5..-211.4) east to the bank-toe lawn edge +0.12 m (tucked under the lawn), floored 1 cm above the lane.
# (b) S edge structures (prep/ws181_lot36/REFS.md §4 re-read in ws182 with 2023 class-1 returns per 0.5 m band):
#     x -323.5..-320.8, y -243.9..-239.1: tops 2.4-2.75 m, intensity 3-4k (not vegetation) -> 3-sided enclosure, open N to the lot, low (1.5 m)
#     returns inside = dumpster (type/material UNVERIFIED). x -319.5..-313.5, y -246.3..-238.5: smooth 1.1-2.1 m tops, intensity 8-9k (= vegetation,
#     like lawn) -> clipped shrub mass, NOT a fence (REFS "fence line" superseded). Light strip x -320.3..-317.3 (2020 ortho) from the Normal Ave N
#     walk into the lot -> concrete pad/walk; the 2023 shrub canopy overhangs its E part at ~1.7 m (UNVERIFIED overlap).
import bpy, bmesh, math, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def ob(pre): return next((o for o in bpy.data.objects if o.name.startswith(pre)),None)
LOT=ob('WS181_Lot36_asphalt'); LANE=ob('WS167_Sprague_E_service_lane'); BANK=ob('WS162_Lot3_W_shoulder_lawn')
def bvh(o):
    bm=bmesh.new(); bm.from_object(o,dg); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
sc=bpy.context.scene
def topname(x,y):
    hit,loc,n,i,o,m=sc.ray_cast(dg,Vector((x,y,140)),Vector((0,0,-1))); return (o.name if hit else '',loc.z if hit else None)
if LOT and LANE and BANK:
    TL=bvh(LANE); TB=bvh(BANK)
    def zdown(t,x,y):
        h=t.ray_cast(Vector((x,y,140)),Vector((0,0,-1))); return h[0].z if h[0] else None
    sc=bpy.context.scene
    def topname(x,y):
        hit,loc,n,i,o,m=sc.ray_cast(dg,Vector((x,y,140)),Vector((0,0,-1))); return (o.name if hit else '',loc.z if hit else None)
    me=LOT.data; bm=bmesh.new(); bm.from_mesh(me); M=LOT.matrix_world; Mi=M.inverted()
    moved=0; dmax=0; cand=[]
    for v in bm.verts:
        w=M@v.co
        corner=abs(w.x+313.6)<0.08 and abs(w.y+211.5)<0.08
        if not v.is_boundary or w.x<-316.6 or not (corner or -224.5<w.y<-211.9): continue   # E chain + NE corner only (N edge verts stay)
        xe=None
        for k in range(1,28):
            x=w.x+0.05*k; nm,z=topname(x,w.y)
            if nm.startswith('WS162_Lot3_W_shoulder'): xe=x; break
        if xe is None: continue
        cand.append((v,w,xe))
    # the bank-toe lawn edge is a straight run: fit x = a*y + b to the found toe points and put the lot edge on that line + 0.25 m
    # (under the lawn), so the visible seam is the lawn's own straight toe, not the 5 cm scan steps
    import numpy as _np
    A=_np.array([(c[1].y,c[2]) for c in cand]); a,b=_np.polyfit(A[:,0],A[:,1],1); res=A[:,1]-(a*A[:,0]+b)
    print('FIX182 toe line x = %.4f*y + %.3f  resid max %.2f rms %.2f n %d'%(a,b,abs(res).max(),(res**2).mean()**0.5,len(A)),flush=True)
    for v,w,xe in cand:
        nx=a*w.y+b+0.25; zl=zdown(TL,nx,w.y); zb=zdown(TB,nx,w.y)
        nz=w.z
        if zl is not None: nz=max(nz,zl+0.01)
        if zb is not None: nz=min(nz,zb-0.03)
        dmax=max(dmax,nx-w.x); v.co=Mi@Vector((nx,w.y,nz)); moved+=1
    # interior verts within 1.2 m of the moved edge: floor 1 cm above the lane where the lane is under them
    fl=0
    for v in bm.verts:
        w=M@v.co
        if v.is_boundary or not (-224.5<w.y<-211.0) or w.x<-318.5: continue
        zl=zdown(TL,w.x,w.y)
        if zl is not None and w.z<zl+0.01: v.co=Mi@Vector((w.x,w.y,zl+0.01)); fl+=1
    bm.to_mesh(me); bm.free(); me.update()
    print('FIX182 NE-edge verts moved',moved,'max shift %.2f'%dmax,'interior floored',fl,flush=True)

else: print('FIX182 (a) SKIPPED missing',[n for n,o in (('lot',LOT),('lane',LANE),('bank',BANK)) if o is None],flush=True)
# (a2) a bank-toe regrade (subdivide + lower within 0.9 m of the line) was tried in ws182 and REMOVED: no visible change in the top/close-up renders.
# ---------- (b) S-edge structures ----------
col=LOT.users_collection[0] if LOT else bpy.context.scene.collection
def mat(name,rgb,rough=0.85):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*rgb,1); p.inputs['Roughness'].default_value=rough; return m
import numpy as np
_L2=np.load('/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/las163.npy'); _L2=_L2[_L2[:,3]==2]
def gz(x,y):
    # top modelled surface, but only if it agrees with 2023 LiDAR ground within 0.3 m (in main a tree canopy / pole / wire could be the top hit)
    k=(abs(_L2[:,0]-x)<0.75)&(abs(_L2[:,1]-y)<0.75); zl=float(np.median(_L2[k,2])) if k.any() else None
    nm,z=topname(x,y)
    if z is not None and (zl is None or abs(z-zl)<0.3): return z
    return zl
def box(name,x0,x1,y0,y1,z0,z1,m):
    bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0)
    for v in bm.verts: v.co=Vector((x0+(v.co.x+0.5)*(x1-x0),y0+(v.co.y+0.5)*(y1-y0),z0+(v.co.z+0.5)*(z1-z0)))
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o=bpy.data.objects.new(name,me); col.objects.link(o); me.materials.append(m); return o
for n in [o.name for o in bpy.data.objects if o.name.startswith('WS182_')]: bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
# concrete pad/walk strip (2020 ortho light strip), Normal Ave N walk -> lot S edge; top 2 cm over local ground, base buried 25 cm
CON=next((m for m in bpy.data.materials if m.name.startswith('WS162_walk_concrete')),None) or mat('WS182_concrete',(0.55,0.54,0.50))
ys=[-248.6+0.5*i for i in range(21)]
bmS=bmesh.new(); rows=[]
for y in ys:
    r=[]
    for x in (-320.3,-318.8,-317.3):
        z=gz(x,y); r.append(bmS.verts.new((x,y,(z if z else 115.6)+0.02)))
    rows.append(r)
for a,b in zip(rows[:-1],rows[1:]):
    for j in range(2): bmS.faces.new((a[j],a[j+1],b[j+1],b[j]))
bmesh.ops.recalc_face_normals(bmS,faces=bmS.faces)
meS=bpy.data.meshes.new('WS182_Lot36_S_concrete_strip_ortho2020_UNVERIFIED'); bmS.to_mesh(meS); bmS.free()
oS=bpy.data.objects.new(meS.name,meS); col.objects.link(oS); meS.materials.append(CON)
oS.modifiers.new('solid','SOLIDIFY').thickness=0.25
# enclosure: 3 walls (W, E, S) 0.2 m, 2.6 m tall, open N toward the lot; dumpster inside
G0=min(z for z in (gz(-323.5,-243.9),gz(-320.8,-243.9),gz(-323.5,-239.1),gz(-320.8,-239.1)) if z)
WALL=mat('WS182_enclosure_wall_CMU_UNVERIFIED',(0.16,0.15,0.13),0.92)
box('WS182_Lot36_enclosure_W_wall_LiDAR2023_UNVERIFIED',-323.5,-323.3,-243.9,-239.1,G0-0.2,G0+2.6,WALL)
box('WS182_Lot36_enclosure_E_wall_LiDAR2023_UNVERIFIED',-321.0,-320.8,-243.9,-239.1,G0-0.2,G0+2.6,WALL)
box('WS182_Lot36_enclosure_S_wall_LiDAR2023_UNVERIFIED',-323.5,-320.8,-243.9,-243.7,G0-0.2,G0+2.6,WALL)
box('WS182_Lot36_enclosure_pad_UNVERIFIED',-323.6,-320.7,-244.0,-238.9,G0-0.2,G0+0.03,CON)
DUMP=mat('WS182_dumpster_green_UNVERIFIED',(0.015,0.05,0.025),0.55)
box('WS182_Lot36_dumpster_UNVERIFIED',-322.95,-321.35,-243.5,-241.5,G0+0.12,G0+1.5,DUMP)
box('WS182_Lot36_dumpster_lid_UNVERIFIED',-323.0,-321.3,-243.55,-241.45,G0+1.5,G0+1.56,mat('WS182_dumpster_lid',(0.03,0.03,0.03),0.5))
# shrub mass: LiDAR heights per 0.5 m (smooth clipped top), built as a heightfield shell draped to ground
import numpy as np
LAS=np.load('/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/las163.npy')
k=(LAS[:,0]>-320)&(LAS[:,0]<-313)&(LAS[:,1]>-247)&(LAS[:,1]<-238)&(LAS[:,3]==1); Q=LAS[k]
SH=mat('WS182_shrub_mass_UNVERIFIEDspecies',(0.02,0.04,0.012),0.95)
if 'leafnoise' not in [n.name for n in SH.node_tree.nodes]:
    nt=SH.node_tree; nz_=nt.nodes.new('ShaderNodeTexNoise'); nz_.name='leafnoise'; nz_.inputs['Scale'].default_value=18; nz_.inputs['Detail'].default_value=8
    cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.008,0.02,0.006,1); cr.color_ramp.elements[1].color=(0.05,0.09,0.025,1)
    nt.links.new(nz_.outputs['Fac'],cr.inputs[0]); nt.links.new(cr.outputs[0],nt.nodes['Principled BSDF'].inputs['Base Color'])
    bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.8; nt.links.new(nz_.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs[0],nt.nodes['Principled BSDF'].inputs['Normal'])
bmH=bmesh.new(); grid={}
xs=np.arange(-319.5,-313.25,0.5); yv=np.arange(-246.5,-238.25,0.5)
for i,x in enumerate(xs):
    for j,y in enumerate(yv):
        q=Q[(abs(Q[:,0]-x)<0.5)&(abs(Q[:,1]-y)<0.5)]; g=gz(x,y) or 115.8
        h=(np.percentile(q[:,2],90)-g) if len(q)>2 else 0.0
        edge=(i in (0,len(xs)-1)) or (j in (0,len(yv)-1))
        h=0.0 if edge else max(0.0,min(2.2,h)); 
        if 0<h<0.5: h=0.5
        grid[i,j]=bmH.verts.new((x,y,g+(h if h>0 else -0.1)))
for i in range(len(xs)-1):
    for j in range(len(yv)-1): bmH.faces.new((grid[i,j],grid[i+1,j],grid[i+1,j+1],grid[i,j+1]))
bmesh.ops.recalc_face_normals(bmH,faces=bmH.faces)
meH=bpy.data.meshes.new('WS182_Lot36_S_shrub_mass_LiDAR2023_UNVERIFIED'); bmH.to_mesh(meH); bmH.free()
for p in meH.polygons: p.use_smooth=True
oH=bpy.data.objects.new(meH.name,meH); col.objects.link(oH); meH.materials.append(SH)
sub=oH.modifiers.new('sub','SUBSURF'); sub.levels=2; sub.render_levels=2
d=oH.modifiers.new('disp','DISPLACE'); tx=bpy.data.textures.new('WS182_shrub_noise','CLOUDS'); tx.noise_scale=0.22; tx.noise_depth=3; d.texture=tx; d.strength=0.30; d.mid_level=0.5
print('FIX182 S-edge built: concrete strip, enclosure G0 %.2f, shrub pts %d'%(G0,len(Q)),flush=True)
