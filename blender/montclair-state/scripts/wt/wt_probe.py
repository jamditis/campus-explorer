import bpy, numpy as np, json
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state'
g=np.load(f'{R}/data/wo/chm_grid_sw_1m.npz'); kd=[f for f in g.files if f.endswith('dtm')][0]; L=g[kd]; print('extent',g['extent'])
GX0,GY0=40,140
def lv(x,y):
    i=int(round(x))-GX0; j=int(round(y))-GY0
    zs=[L[jj,ii] for jj in (j-1,j) for ii in (i-1,i) if 0<=jj<L.shape[0] and 0<=ii<L.shape[1] and np.isfinite(L[jj,ii])]
    return float(np.mean(zs)) if zs else None
dg=bpy.context.evaluated_depsgraph_get()
rep={}
X0,X1,Y0,Y1=56,82,243,322
def wverts(o,ev=True):
    if ev:
        e=o.evaluated_get(dg); m=e.to_mesh(); vs=[o.matrix_world@v.co for v in m.vertices]; e.to_mesh_clear(); return vs
    return [o.matrix_world@v.co for v in o.data.vertices]
def stats(o,box=(X0,X1,Y0,Y1),ev=True):
    vs=[c for c in wverts(o,ev) if box[0]<=c.x<=box[1] and box[2]<=c.y<=box[3]]
    d=[c.z-lv(c.x,c.y) for c in vs if lv(c.x,c.y) is not None]
    if not d: return {'n':len(vs)}
    d=np.array(d); return {'n':len(vs),'med':round(float(np.median(d)),3),'p5':round(float(np.percentile(d,5)),3),'p95':round(float(np.percentile(d,95)),3),'min':round(float(d.min()),3),'max':round(float(d.max()),3)}
objs=[]
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[b.x for b in bb]; ys=[b.y for b in bb]; zs=[b.z for b in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if max(xs)-min(xs)>500: continue
    objs.append({'name':o.name,'col':[c.name for c in o.users_collection],'type':o.type,'bb':[round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(zs),2),round(max(zs),2)],'hide':o.hide_render,'mods':[m.type for m in o.modifiers],'mats':[m.name for m in o.data.materials if m] if o.type=='MESH' else []})
rep['objs']=objs
for n in ['RZ2_SC_LiDAR_ground_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','Terrain_LiDAR_DTM_1m','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','QQ_Richardson_paved_apron_UNVERIFIED','QS_footway_313027436','QS_footway_313027437','QS_footway_313027428','PB2_walk_lawn_fillet_UNVERIFIED','Context_skirt_3DEP_ortho_4km']:
    o=bpy.data.objects.get(n)
    if not o: rep[n]='MISSING'; continue
    d={'stats_tile':stats(o,(58,80,245,320)),'mats':[m.name for m in o.data.materials if m],'attrs':[(a.name,a.domain,a.data_type) for a in o.data.attributes if not a.name.startswith('.')],'mods':[(m.name,m.type,getattr(m,'node_group',None) and m.node_group.name) for m in o.modifiers],'nv':len(o.data.vertices),'hide':o.hide_render,'cols':[c.name for c in o.users_collection],'uv':[u.name for u in o.data.uv_layers]}
    rep[n]=d
RZ=bpy.data.objects['RZ2_SC_LiDAR_ground_patch_UNVERIFIED']
vs=wverts(RZ,False); xs=sorted(set(round(c.x,2) for c in vs)); rep['RZ2_xs_tail']=xs[-6:]; rep['RZ2_ys']=[round(min(c.y for c in vs),2),round(max(c.y for c in vs),2)]
mx=max(c.x for c in vs); ee=[c for c in vs if abs(c.x-mx)<0.05]
rep['RZ2_east_edge']=[[round(c.x,2),round(c.y,2),round(c.z,3),round(c.z-(lv(c.x,c.y) or 0),3)] for c in sorted(ee,key=lambda c:c.y)]
TL=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tv=[c for c in wverts(TL,False) if 55<=c.x<=83 and c.y>238]
rep['TL_north']=[[round(c.x,2),round(c.y,2),round(c.z,2),round(c.z-(lv(c.x,c.y) or 0),3)] for c in sorted(tv,key=lambda c:(c.x,c.y))][:200]
WF=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']; fv=[c for c in wverts(WF,False) if 55<=c.x<=83 and c.y<323]
rep['WF_south']=[[round(c.x,2),round(c.y,2),round(c.z,2),round(c.z-(lv(c.x,c.y) or 0),3)] for c in sorted(fv,key=lambda c:(c.x,c.y))][:200]
QW=bpy.data.objects['QW_DTM_north_edge_ramp_UNVERIFIED']; qv=wverts(QW,False)
rep['QW_ys']=sorted(set(round(c.y,1) for c in qv))[:50]; rep['QW_xs_near']=sorted(set(round(c.x,1) for c in qv if 50<c.x<90))
rep['QW_npoly']=len(QW.data.polygons)
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
for m in sk.modifiers:
    if m.type=='NODES':
        ng=m.node_group; rep.setdefault('skirt_ng',[]).append([m.name,ng.name,[(n.bl_idname,n.name) for n in ng.nodes if n.bl_idname in ('GeometryNodeObjectInfo','GeometryNodeSubdivideMesh','GeometryNodeInputNamedAttribute','FunctionNodeCompare')]])
for mn in rep['RZ2_SC_LiDAR_ground_patch_UNVERIFIED']['mats']:
    m=bpy.data.materials[mn]; rep.setdefault('rz2_mat_nodes',{})[mn]=[(n.bl_idname,n.name,getattr(n,'attribute_name',None) or (n.image.name if getattr(n,'image',None) else None)) for n in m.node_tree.nodes]
json.dump(rep,open(f'{R}/data/wt/probe.json','w'),indent=1)
print('DONE')
