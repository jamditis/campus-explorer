# Session io (2026-10-25): hn + aisle risers use the coursed riser stone, aisle treads match the seat tone, smooth-by-angle (30 deg) to remove flat facets.
# Session hn (2026-10-25): warm brown stone per the two 2007 Commons photos (msu_amphitheater, kasser_plaza_amphitheater_2007), coursed riser faces (3 courses/riser).
# Session hm (2026-10-25): hl + long granite bench blocks (UV brick joints along rows), outline-snapped edge (no saw-tooth).
# Session hl (2026-10-25): stone amphitheater next to Kasser (OSM way 232850516), v1 bowl in MAIN.
# Stepped stone rows follow the smoothed 2023 LiDAR ground contours (rise per row = (Z_TOP-Z_STAGE)/N_ROWS, ESTIMATE N_ROWS=19),
# flat stage at Z_STAGE, fieldstone skirt on the outline edge. Idempotent: deletes collection Kasser_amphitheater_hl first.
# Env: SAVE=1 to save; REVERT=1 removes the collection and restores terrain from the stored z (custom prop).
import bpy, bmesh, numpy as np, json, os, math
D='/workspace/nj-scenes/montclair-state/'
N_ROWS=int(os.environ.get('N_ROWS',19)); Z_STAGE=float(os.environ.get('Z_STAGE',132.45)); Z_TOP=float(os.environ.get('Z_TOP',141.3))
RISER=(Z_TOP-Z_STAGE)/N_ROWS; RES=float(os.environ.get('RES',0.15)); CN='Kasser_amphitheater_hl'
g=np.load(D+'north/data/day_heroes/cx/amphi/amphi_grid_0p5m_cx.npz'); G=g['ground'].astype(np.float64); x0=float(g['x0']); y0=float(g['y0']); R=float(g['res'])
P=np.array(json.load(open(D+'north/data/day_heroes/ct/amphi_locate_ct.json'))['osm']['232850516']['pts'])
def inside(x,y):
    c=np.zeros(np.shape(x),bool)
    for i in range(len(P)-1):
        x1,y1=P[i];x2,y2=P[i+1]; m=((y1>y)!=(y2>y)); xi=x1+(y-y1)*(x2-x1)/(y2-y1+1e-12); c^=m&(x<xi)
    return c
# gaussian smooth (sigma 1.2 m) so the quantised rows are clean arcs
s=1.2/R; r=int(3*s); k=np.exp(-0.5*(np.arange(-r,r+1)/s)**2); k/=k.sum()
Gp=np.pad(G,r,mode='edge'); Gs=np.apply_along_axis(lambda v:np.convolve(v,k,'valid'),1,Gp); Gs=np.apply_along_axis(lambda v:np.convolve(v,k,'valid'),0,Gs)
def samp(x,y):
    fx=(x-x0)/R-0.5; fy=(y-y0)/R-0.5; ix=np.clip(np.floor(fx).astype(int),0,G.shape[1]-2); iy=np.clip(np.floor(fy).astype(int),0,G.shape[0]-2)
    tx=np.clip(fx-ix,0,1); ty=np.clip(fy-iy,0,1)
    return (Gs[iy,ix]*(1-tx)*(1-ty)+Gs[iy,ix+1]*tx*(1-ty)+Gs[iy+1,ix]*(1-tx)*ty+Gs[iy+1,ix+1]*tx*ty)
terr=bpy.data.objects['Terrain_LiDAR_DTM_1m']
# --- cleanup / revert
if CN in bpy.data.collections:
    c=bpy.data.collections[CN]
    for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(c)
if 'hl_terrain_orig' in terr:
    d=json.loads(terr['hl_terrain_orig'])
    for i,z in d.items(): terr.data.vertices[int(i)].co.z=z
    del terr['hl_terrain_orig']
if os.environ.get('REVERT')=='1':
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile()
    print('HL REVERTED'); raise SystemExit
# --- grid
xs=np.arange(P[:,0].min()-0.3,P[:,0].max()+0.3,RES); ys=np.arange(P[:,1].min()-0.3,P[:,1].max()+0.3,RES)
X,Y=np.meshgrid(xs,ys); ZS=samp(X,Y); IN=inside(X,Y)&(ZS<Z_TOP+float(os.environ.get('TOPCUT',-0.15)))  # stop where the lawn rises past the top row
W=float(os.environ.get('RW',0.12))
def prof(zs):
    t=np.clip((zs-Z_STAGE-0.06)/RISER+1.0,0,N_ROWS+0.999); fl=np.floor(t); fr=t-fl
    st=np.clip((fr-(1-W))/W,0,1); st=st*st*(3-2*st); return np.clip(fl+st,0,N_ROWS)
SL=float(os.environ.get('STAGE_LVL',1)); lvl=np.maximum(prof(ZS),SL)
# hm: two stair aisles (ESTIMATE positions: thirds of the seating arc; 2007 photos show 2 aisles with rails), half-height steps
_st=IN&(lvl<SL+0.02); CX=float(X[_st].mean()); CY=float(Y[_st].mean())
TH=np.arctan2(Y-CY,X-CX); RR=np.hypot(X-CX,Y-CY); _sm=IN&(lvl>=2)
_t=np.unwrap(np.sort(TH[_sm])); ta,tb=np.percentile(TH[_sm],3),np.percentile(TH[_sm],97)
AISLE_TH=[ta+(tb-ta)/3,ta+2*(tb-ta)/3]; AW=float(os.environ.get('AISLE_W',1.3)); AISLE=np.zeros_like(IN)
for a in AISLE_TH: AISLE|=(np.abs(RR*np.sin(TH-a))<AW/2)&(np.cos(TH-a)>0)&(lvl>SL+0.02)
def prof2(zs):
    t=np.clip(((zs-Z_STAGE-0.06)/RISER+1.0)*2,0,2*N_ROWS+1.999); fl=np.floor(t); fr=t-fl
    st=np.clip((fr-(1-W))/W,0,1); st=st*st*(3-2*st); return np.clip((fl+st)/2,SL,N_ROWS)
lvl=np.where(AISLE,prof2(ZS),lvl); Z=Z_STAGE+lvl*RISER  # hm: the flat level-1 terrace IS the stage; drop the jagged 0.47 m level-0 strip
ny,nx=X.shape; idx=-np.ones((ny,nx),int)
bm=bmesh.new(); vs=[]
for j in range(ny):
    for i in range(nx):
        # a vertex is used if any adjacent cell is fully inside
        pass
cellin=IN[:-1,:-1]&IN[1:,:-1]&IN[:-1,1:]&IN[1:,1:]
use=np.zeros_like(IN); use[:-1,:-1]|=cellin; use[1:,:-1]|=cellin; use[:-1,1:]|=cellin; use[1:,1:]|=cellin
for j,i in zip(*np.nonzero(use)):
    idx[j,i]=len(vs); vs.append(bm.verts.new((X[j,i],Y[j,i],Z[j,i])))
bm.verts.ensure_lookup_table()
LV=lvl
uvl=bm.loops.layers.uv.new('UVMap')
# hm: snap outline verts onto the OSM polygon so the edge/skirt is a smooth curve, not a raster saw-tooth
full=np.zeros_like(IN); full[1:-1,1:-1]=cellin[:-1,:-1]&cellin[1:,:-1]&cellin[:-1,1:]&cellin[1:,1:]
A=P[:-1]; Bp=P[1:]; snapped=0
for j,i in zip(*np.nonzero(use&~full)):
    p=np.array([X[j,i],Y[j,i]]); d=Bp-A; t=np.clip(((p-A)*d).sum(1)/((d*d).sum(1)+1e-12),0,1); q=A+d*t[:,None]; dd=np.hypot(*(q-p).T); m=int(dd.argmin())
    if dd[m]<RES*1.6: v=vs[idx[j,i]]; v.co.x,v.co.y=q[m]; snapped+=1
# hm: centre of the stage for row arc length
BL=float(os.environ.get('BLOCK',1.8))
for j,i in zip(*np.nonzero(cellin)):
    q=(idx[j,i],idx[j,i+1],idx[j+1,i+1],idx[j+1,i]); f=bm.faces.new([vs[t] for t in q])
    L=[LV[j,i],LV[j,i+1],LV[j+1,i+1],LV[j+1,i]]
    f.material_index = 0 if max(L)<SL+0.02 else (2 if (max(L)-min(L))>0.06 else 1)
    if AISLE[j,i] and AISLE[j,i+1] and AISLE[j+1,i] and AISLE[j+1,i+1] and max(L)>=SL+0.02: f.material_index=(4 if (max(L)-min(L))<=0.03 else 2)
    for lp,(jj,ii) in zip(f.loops,[(j,i),(j,i+1),(j+1,i+1),(j+1,i)]):
        r=math.hypot(X[jj,ii]-CX,Y[jj,ii]-CY); th=math.atan2(Y[jj,ii]-CY,X[jj,ii]-CX); lp[uvl].uv=(th*max(r,1.0)/BL, LV[jj,ii]+0.5)
# skirt: extrude boundary edges down 0.7 m (fieldstone base course / edge wall)
bnd=[e for e in bm.edges if e.is_boundary]
ret=bmesh.ops.extrude_edge_only(bm,edges=bnd)
for v in [x for x in ret['geom'] if isinstance(x,bmesh.types.BMVert)]: v.co.z-=0.7
for f in [x for x in ret['geom'] if isinstance(x,bmesh.types.BMFace)]: f.material_index=3
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new('Kasser_amphitheater_bowl_hl'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
me.set_sharp_from_angle(angle=math.radians(float(os.environ.get('SHARP_DEG',30))))
# --- materials
def mat(name,base,var,bumpscale,rough,jmin=0.55):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    o=nt.nodes.new('ShaderNodeOutputMaterial'); b=nt.nodes.new('ShaderNodeBsdfPrincipled'); nt.links.new(b.outputs[0],o.inputs[0])
    tc=nt.nodes.new('ShaderNodeTexCoord'); n1=nt.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value=1.6; n1.inputs['Detail'].default_value=8
    nt.links.new(tc.outputs['Object'],n1.inputs['Vector'])
    vo=nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value=var; nt.links.new(tc.outputs['Object'],vo.inputs['Vector'])
    vo.feature='DISTANCE_TO_EDGE'
    cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(*[c*0.78 for c in base],1); cr.color_ramp.elements[1].color=(*[min(1,c*1.12) for c in base],1)
    nt.links.new(n1.outputs['Fac'],cr.inputs[0])
    jt=nt.nodes.new('ShaderNodeMapRange'); jt.inputs['From Min'].default_value=0.0; jt.inputs['From Max'].default_value=0.04; jt.inputs['To Min'].default_value=jmin; jt.inputs['To Max'].default_value=1.0
    nt.links.new(vo.outputs['Distance'],jt.inputs['Value'])
    mx=nt.nodes.new('ShaderNodeMixRGB'); mx.blend_type='MULTIPLY'; mx.inputs[0].default_value=1.0; nt.links.new(cr.outputs[0],mx.inputs[1]); nt.links.new(jt.outputs[0],mx.inputs[2])
    nt.links.new(mx.outputs[0],b.inputs['Base Color']); b.inputs['Roughness'].default_value=rough
    bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=bumpscale; nt.links.new(vo.outputs['Distance'],bp.inputs['Height']); nt.links.new(bp.outputs[0],b.inputs['Normal'])
    return m
def seat(name,base,sc=1.0,c2=(0.86,0.85,0.83,1)):
    m=mat(name,base,0.45,0.0,0.74,1.0); nt=m.node_tree; b=[n for n in nt.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled'][0]
    uv=nt.nodes.new('ShaderNodeUVMap'); uv.uv_map='UVMap'; br=nt.nodes.new('ShaderNodeTexBrick'); nt.links.new(uv.outputs[0],br.inputs['Vector'])
    br.inputs['Scale'].default_value=sc; br.inputs['Brick Width'].default_value=1.0; br.inputs['Row Height'].default_value=1.0; br.inputs['Mortar Size'].default_value=0.012; br.inputs['Mortar Smooth'].default_value=0.3
    br.inputs['Color1'].default_value=(1,1,1,1); br.inputs['Color2'].default_value=c2; br.inputs['Mortar'].default_value=(0.22,0.21,0.2,1); br.offset=0.5; br.inputs['Bias'].default_value=0
    mx=[n for n in nt.nodes if n.bl_idname=='ShaderNodeMixRGB'][0]; m2=nt.nodes.new('ShaderNodeMixRGB'); m2.blend_type='MULTIPLY'; m2.inputs[0].default_value=1.0
    nt.links.new(mx.outputs[0],m2.inputs[1]); nt.links.new(br.outputs['Color'],m2.inputs[2]); nt.links.new(m2.outputs[0],b.inputs['Base Color'])
    bp=[n for n in nt.nodes if n.bl_idname=='ShaderNodeBump'][0]; bp.inputs['Strength'].default_value=0.35; bp.invert=True; nt.links.new(br.outputs['Fac'],bp.inputs['Height'])
    return m
mats=[mat('io_amphi_stage_concrete',(0.285,0.255,0.215),1.6,0.02,0.88,0.97), seat('hn_amphi_seat_stone_blocks',(0.245,0.2,0.16),1.0,(0.78,0.74,0.7,1)),
      seat('hn_amphi_riser_coursed_stone',(0.15,0.1,0.068),3.0,(0.6,0.52,0.46,1)), mat('hn_amphi_base_fieldstone',(0.22,0.15,0.1),2.6,0.6,0.92)]
def _stage_joints(m):
    # hn: saw-cut control joints on a ~2.4 m grid (object coords; ESTIMATE spacing), photo 1 shows a plain warm concrete walk at the bottom
    nt=m.node_tree; b=[n for n in nt.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled'][0]; mx=[n for n in nt.nodes if n.bl_idname=='ShaderNodeMixRGB'][0]
    tc=nt.nodes.new('ShaderNodeTexCoord'); br=nt.nodes.new('ShaderNodeTexBrick'); nt.links.new(tc.outputs['Object'],br.inputs['Vector'])
    br.inputs['Scale'].default_value=1/2.4; br.inputs['Brick Width'].default_value=1.0; br.inputs['Row Height'].default_value=1.0; br.offset=0.0
    br.inputs['Mortar Size'].default_value=0.006; br.inputs['Mortar Smooth'].default_value=0.2; br.inputs['Color1'].default_value=(1,1,1,1); br.inputs['Color2'].default_value=(0.94,0.93,0.91,1); br.inputs['Mortar'].default_value=(0.45,0.43,0.4,1)
    m2=nt.nodes.new('ShaderNodeMixRGB'); m2.blend_type='MULTIPLY'; m2.inputs[0].default_value=1.0; nt.links.new(mx.outputs[0],m2.inputs[1]); nt.links.new(br.outputs['Color'],m2.inputs[2]); nt.links.new(m2.outputs[0],b.inputs['Base Color'])
_stage_joints(mats[0])
mats.append(seat('io_amphi_aisle_stone',(0.275,0.228,0.184),1.0,(0.88,0.85,0.81,1)))
for m in mats: me.materials.append(m)
ob=bpy.data.objects.new('Kasser_amphitheater_bowl_hl',me)
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col); col.objects.link(ob)
# hm: steel handrail down the centre of each aisle (ESTIMATE), 0.9 m above the nosings, posts ~2.4 m
rm=bpy.data.materials.get('hm_rail_steel') or bpy.data.materials.new('hm_rail_steel'); rm.use_nodes=True; _b=rm.node_tree.nodes.get('Principled BSDF')
_b.inputs['Base Color'].default_value=(0.09,0.09,0.095,1); _b.inputs['Metallic'].default_value=0.85; _b.inputs['Roughness'].default_value=0.42
for ai,a in enumerate(AISLE_TH):
    rs=RR[AISLE&(np.abs(RR*np.sin(TH-a))<0.2)]
    if len(rs)<4: continue
    pts=[]
    for r in np.arange(rs.min()+0.4,rs.max()-0.3,0.25):
        x=CX+r*math.cos(a); y=CY+r*math.sin(a); i=int(round((x-xs[0])/RES)); j=int(round((y-ys[0])/RES))
        if 0<=j<ny and 0<=i<nx and use[j,i]: pts.append((x,y,float(Z[j,i])))
    if len(pts)<3: continue
    A_=np.array(pts); rr_=np.hypot(A_[:,0]-CX,A_[:,1]-CY); c1,c0=np.polyfit(rr_,A_[:,2],1); off=float((A_[:,2]-(c0+c1*rr_)).max())+0.9
    pts=[(q[0],q[1],c0+c1*r_+off) for q,r_ in zip(pts,rr_)]
    cu=bpy.data.curves.new(f'hm_amphi_rail_{ai}','CURVE'); cu.dimensions='3D'; cu.bevel_depth=0.024; cu.bevel_resolution=3
    sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for p_,q in zip(sp.points,pts): p_.co=(*q,1)
    ro=bpy.data.objects.new(f'Kasser_amphitheater_rail_hm_{ai}',cu); cu.materials.append(rm); col.objects.link(ro); ro['ESTIMATE']='aisle/rail position estimated (2007 photos show 2 aisles with rails)'
    pm=bpy.data.meshes.new(f'hm_rail_posts_{ai}'); bm2=bmesh.new()
    for q in pts[::10]+[pts[-1]]:
        g_=bmesh.ops.create_cone(bm2,cap_ends=True,segments=10,radius1=0.022,radius2=0.022,depth=0.9)
        bmesh.ops.translate(bm2,verts=g_['verts'],vec=(q[0],q[1],q[2]-0.45))
    bm2.to_mesh(pm); bm2.free(); pm.materials.append(rm); po=bpy.data.objects.new(f'Kasser_amphitheater_railposts_hm_{ai}',pm); col.objects.link(po)
    print('HM RAIL',ai,len(pts),'pts start',[round(v,2) for v in pts[0]],'end',[round(v,2) for v in pts[-1]])
ob['ESTIMATE_rows']=N_ROWS; ob['riser_m']=RISER; ob['source']='OSM 232850516 outline + 2023 LiDAR ground (cx 0.5 m grid, 1.2 m gaussian); rows/riser ESTIMATE'
# --- terrain: push DTM verts inside the outline below the bowl
co=np.empty(len(terr.data.vertices)*3); terr.data.vertices.foreach_get('co',co); co=co.reshape(-1,3); M=np.array(terr.matrix_world); w=co@M[:3,:3].T+M[:3,3]
k=np.nonzero(inside(w[:,0],w[:,1])&(samp(w[:,0],w[:,1])<Z_TOP-0.15))[0]; orig={}
zb=Z_STAGE+np.maximum(np.floor(prof(samp(w[k,0],w[k,1]))),SL)*RISER
for t,zz in zip(k,zb):
    if w[t,2]>zz-0.08:
        orig[str(int(t))]=float(terr.data.vertices[int(t)].co.z); terr.data.vertices[int(t)].co.z-= (w[t,2]-(zz-0.12))
terr['hl_terrain_orig']=json.dumps(orig); terr.data.update()
print('HL BUILT verts',len(me.vertices),'faces',len(me.polygons),'riser %.3f'%RISER,'terrain lowered',len(orig),'levels used',float(lvl[IN].max()))
for n in ['T_PinOak_L1_0330','T_PinOak_L1_0339','T_RedMaple_L1_0338','T_LondonPlane_L1_0349']:
    o=bpy.data.objects.get(n)
    if o: print('TREE',n,tuple(round(v,1) for v in o.matrix_world.translation),'inside',bool(inside(np.array([o.matrix_world.translation.x]),np.array([o.matrix_world.translation.y]))[0]))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('HL SAVED')
print('IO BUILD DONE')
