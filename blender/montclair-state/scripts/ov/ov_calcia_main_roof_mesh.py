# ov-prep: Calcia 'roof (LiDAR)' mesh as built by build_scene (data/geom.npz, bid 13) - steep facets, eave/fascia ring, roof levels. Read-only.
import json, numpy as np, shapely
G=np.load('data/geom.npz'); M=json.load(open('data/geom_meta.json'))
b=[x for x in M['buildings'] if x['osm_id']=='313024770'][0]; bid=b['bid']
S={f['id']:f for f in json.load(open('data/scene_data.json'))['features']}; P=shapely.Polygon(S['313024770']['pts'])
vb=G['roof_bid']; T=G['roof_t']; s=vb[T[:,0]]==bid; t=T[s]; V=G['roof_v']; Pt=V[t]; fl=G['roof_tflag'][s]
n=np.cross(Pt[:,1]-Pt[:,0],Pt[:,2]-Pt[:,0]); A=np.linalg.norm(n,axis=1)/2; nz=np.abs(n[:,2])/np.maximum(2*A,1e-9)
c=Pt.mean(1); d=shapely.distance(P.exterior,shapely.points(c[:,0],c[:,1]))*np.where(shapely.contains_xy(P,c[:,0],c[:,1]),1,-1)
r0=fl==0; steep=r0&(nz<0.93)
out=dict(bid=bid,meta=b,tris=int(s.sum()),tflag_counts=np.bincount(fl).tolist(),
 roof_area_m2=round(float(A[r0].sum())),steep_area_m2_nz_lt_0p93=round(float(A[steep].sum())),
 steep_area_by_signed_edge_dist_m={f'{a}..{a+1}':round(float(A[steep&(d>=a)&(d<a+1)].sum())) for a in range(-2,8)},
 steep_area_interior_gt3m=round(float(A[steep&(d>3)].sum())),
 eave_fascia_z_p10_50_90=np.percentile(Pt[~r0][:,:,2],[10,50,90]).round(2).tolist())
z=V[vb==bid][:,2]; h,e=np.histogram(z,np.arange(z.min()-.25,z.max()+.5,.25)); pk=[(round(float(.5*(e[i]+e[i+1])),2),int(h[i])) for i in np.argsort(h)[::-1][:6]]
out['roof_vertex_z_peaks_0p25m']=pk
json.dump(out,open('north/data/ov_prep/calcia_main_roof_mesh_ov.json','w'),indent=1); print(json.dumps(out,indent=1))
