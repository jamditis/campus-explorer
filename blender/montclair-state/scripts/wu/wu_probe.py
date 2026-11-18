"""wu: read-only Tile B probe — x80-120, y245-320 (Richardson/Reid). No save."""
import bpy, numpy as np, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'
X0,X1,Y0,Y1=80,120,245,320
g=np.load(f'{R}/data/wo/chm_grid_sw_1m.npz'); kd=[f for f in g.files if f.endswith('dtm')][0]; L=g[kd]
print('extent', list(g['extent']) if 'extent' in g.files else g.files, 'dtm', kd, L.shape, flush=True)
GX0,GY0=40,140
def lv(x,y):
    i=int(round(x))-GX0; j=int(round(y))-GY0
    zs=[L[jj,ii] for jj in (j-1,j) for ii in (i-1,i) if 0<=jj<L.shape[0] and 0<=ii<L.shape[1] and np.isfinite(L[jj,ii])]
    return float(np.mean(zs)) if zs else None
dg=bpy.context.evaluated_depsgraph_get()
rep={'objs_scene':len(bpy.data.objects)}
def wverts(o,ev=True):
    if ev:
        e=o.evaluated_get(dg); m=e.to_mesh(); vs=[o.matrix_world@v.co for v in m.vertices]; e.to_mesh_clear(); return vs
    return [o.matrix_world@v.co for v in o.data.vertices]
def stats(vs):
    d=[c.z-lv(c.x,c.y) for c in vs if lv(c.x,c.y) is not None]
    if not d: return {'n':len(vs),'n_dtm':0}
    d=np.array(d); return {'n':len(vs),'n_dtm':len(d),'med':round(float(np.median(d)),3),'p5':round(float(np.percentile(d,5)),3),'p95':round(float(np.percentile(d,95)),3),'min':round(float(d.min()),3),'max':round(float(d.max()),3)}

# 1. objects overlapping the tile (skip huge far-field)
olist=[]
reidish=[]
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[b.x for b in bb]; ys=[b.y for b in bb]; zs=[b.z for b in bb]
    if max(xs)<X0-2 or min(xs)>X1+2 or max(ys)<Y0-2 or min(ys)>Y1+2: continue
    if max(xs)-min(xs)>400: continue
    rec={'name':o.name,'col':[c.name for c in o.users_collection],'bb':[round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2),round(min(zs),2),round(max(zs),2)],'hide':bool(o.hide_render),'nv':len(o.data.vertices) if o.type=='MESH' else 0}
    olist.append(rec)
    n=o.name.lower()
    if any(k in n for k in ('reid','313027434','irvin')) or any(k in ' '.join(rec['col']).lower() for k in ('reid','313027434','irvin')):
        reidish.append(rec)
rep['n_overlap']=len(olist)
rep['overlap']=[r['name'] for r in sorted(olist,key=lambda r:r['name'])]
rep['overlap_detail']=sorted(olist,key=lambda r:r['name'])
rep['reidish']=reidish

# 2. named ground / apron / doors / WT
names=['RZ2_SC_LiDAR_ground_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','Terrain_LiDAR_DTM_1m','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','WT_richardson_west_LiDAR_patch_UNVERIFIED','QQ_Richardson_paved_apron_UNVERIFIED','QQ_Richardson_entrance_doors','QT_Richardson_base_plinth_UNVERIFIED','QP_Richardson_ground_storey_glass_piers_UNVERIFIED','QP_Richardson_white_corner_towers_UNVERIFIED','QP_Richardson_upper_block_UNVERIFIED','QU_G_floor_UNVERIFIED']
# also walks that might enter tile B
for o in bpy.data.objects:
    if o.name.startswith(('QS_footway','QT_soil_edge','QW_footway','QW_soil_edge','QS_service','SG_QuadRoad','TR_footway')):
        names.append(o.name)
# building-like QP/QQ/QR/QT/QU/TI/TQ/TR
for o in bpy.data.objects:
    if o.name.startswith(('QP_','QQ_','QR_','QT_','QU_','TI_','TQ_','TR_','MO ')):
        if o.name not in names: names.append(o.name)

for n in names:
    o=bpy.data.objects.get(n)
    if not o: rep[n]='MISSING'; continue
    if o.type!='MESH':
        rep[n]={'type':o.type,'cols':[c.name for c in o.users_collection]}; continue
    vs=[c for c in wverts(o,False) if X0-1<=c.x<=X1+1 and Y0-1<=c.y<=Y1+1]
    rec={'n_in_box':len(vs),'stats':stats(vs),'bb_all':None,'mats':[m.name for m in o.data.materials if m] if o.type=='MESH' else [],'nv':len(o.data.vertices) if o.type=='MESH' else 0,'cols':[c.name for c in o.users_collection]}
    if vs:
        rec['z']=[round(min(c.z for c in vs),3),round(max(c.z for c in vs),3)]
        rec['xy']=[round(min(c.x for c in vs),2),round(max(c.x for c in vs),2),round(min(c.y for c in vs),2),round(max(c.y for c in vs),2)]
    rep[n]=rec

# 3. QW verts with x>80 (the "does Tile B meet QW?" question)
QW=bpy.data.objects['QW_DTM_north_edge_ramp_UNVERIFIED']
qv=wverts(QW,False)
q_hi=[c for c in qv if c.x>80]
q_tile=[c for c in qv if 80<=c.x<=120 and 245<=c.y<=320]
rep['QW_xgt80']={'n':len(q_hi),'n_tile':len(q_tile),'xs':sorted(set(round(c.x,1) for c in q_hi))[:40],'ys':sorted(set(round(c.y,1) for c in q_hi))[:40],'z':None if not q_hi else [round(min(c.z for c in q_hi),3),round(max(c.z for c in q_hi),3)]}
if q_tile:
    rep['QW_xgt80']['tile_xy']=[round(min(c.x for c in q_tile),2),round(max(c.x for c in q_tile),2),round(min(c.y for c in q_tile),2),round(max(c.y for c in q_tile),2)]

# 4. WT east edge at x=80
WT=bpy.data.objects['WT_richardson_west_LiDAR_patch_UNVERIFIED']
wv=wverts(WT,False)
ee=[c for c in wv if abs(c.x-80)<0.05]
rep['WT_east_x80']={'n':len(ee),'ys':sorted(set(round(c.y,2) for c in ee)),'dz_vs_dtm':stats(ee),'z_by_y':[[round(c.y,2),round(c.z,3),round(c.z-(lv(c.x,c.y) or 0),3)] for c in sorted(ee,key=lambda c:c.y)]}
# WT feather zone x72-80
fe=[c for c in wv if 71.5<=c.x<=80.5]
rep['WT_feather_x72_80']=stats(fe)

# 5. WF south edge y=320, x80-120
WF=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
fv=[c for c in wverts(WF,False) if 78<=c.x<=122 and c.y<322]
se=[c for c in fv if abs(c.y-320)<0.05]
rep['WF_south_y320_x80_120']={'n_near':len(fv),'n_edge':len(se),'xs':sorted(set(round(c.x,2) for c in se)),'stats_edge':stats(se),'stats_near':stats(fv)}

# 6. Terrain_LiDAR north of y238 in tile
TL=bpy.data.objects['Terrain_LiDAR_DTM_1m']
tv=[c for c in wverts(TL,False) if 78<=c.x<=122 and c.y>238]
rep['TL_north_tileB']={'n':len(tv),'ys':sorted(set(round(c.y,2) for c in tv))[:20],'stats':stats(tv)}

# 7. door sill
doors=bpy.data.objects.get('QQ_Richardson_entrance_doors') or bpy.data.objects.get('QQ_Richardson_entrance_doors_UNVERIFIED')
if doors:
    dv=wverts(doors,False)
    inb=[c for c in dv if 70<=c.x<=90 and 235<=c.y<=300]
    zmin=min(c.z for c in dv)
    bot=[c for c in dv if c.z<zmin+0.08]
    rep['doors']={'name':doors.name,'zminmax':[round(min(c.z for c in dv),3),round(max(c.z for c in dv),3)],'bot_n':len(bot),'bot_xy':None if not bot else [round(min(c.x for c in bot),2),round(max(c.x for c in bot),2),round(min(c.y for c in bot),2),round(max(c.y for c in bot),2)],'bot_z':round(zmin,3),'in_box_n':len(inb)}
else:
    # find by prefix
    cand=[o.name for o in bpy.data.objects if 'entrance_door' in o.name.lower() or 'Richardson_entrance' in o.name]
    rep['doors']={'MISSING':True,'cands':cand}

# 8. skirt GN list + WT group compare values
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
ngs=[]
for m in sk.modifiers:
    if m.type=='NODES' and m.node_group:
        ng=m.node_group
        cmp=[(n.name,n.operation if hasattr(n,'operation') else '',round(n.inputs[1].default_value,3) if n.inputs and len(n.inputs)>1 and hasattr(n.inputs[1],'default_value') and isinstance(n.inputs[1].default_value,(int,float)) else None) for n in ng.nodes if n.bl_idname=='FunctionNodeCompare']
        nms=[(n.bl_idname,n.name) for n in ng.nodes if n.bl_idname in ('GeometryNodeObjectInfo','GeometryNodeSubdivideMesh','GeometryNodeInputNamedAttribute')]
        ngs.append({'mod':m.name,'ng':ng.name,'cmp':cmp,'nodes':nms})
rep['skirt_ng']=ngs

# 9. WT material name + attrs
wtm=[m.name for m in WT.data.materials if m]
rep['WT_mats']=wtm
rep['WT_attrs']=[(a.name,a.domain,a.data_type) for a in WT.data.attributes if not a.name.startswith('.')]
rep['WT_nv']=len(WT.data.vertices); rep['WT_nf']=len(WT.data.polygons)

# 10. building object names containing ground/plinth/floor near tile (for mask)
bldg=[r for r in olist if any(k in r['name'] for k in ('plinth','ground_storey','G_floor','tower','upper_block','Reid','reid','313027434','wall','Hall'))]
rep['bldg_like']=bldg

json.dump(rep,open(f'{R}/data/wu/probe.json','w'),indent=1)
print('OVERLAP',len(olist),'REIDISH',reidish, flush=True)
print('QW_xgt80',rep['QW_xgt80'], flush=True)
print('WT_east n',rep['WT_east_x80']['n'],'ys',rep['WT_east_x80']['ys'][:8],'...',rep['WT_east_x80']['ys'][-4:] if rep['WT_east_x80']['ys'] else None, flush=True)
print('WF_south',rep['WF_south_y320_x80_120'], flush=True)
print('TL',rep['TL_north_tileB'], flush=True)
print('DOORS',rep['doors'], flush=True)
print('DONE', flush=True)
