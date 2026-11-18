# ov-prep: roof-level outlines from the 1 m DSM inside each day-6 OSM footprint -> polygons (scene x,y), area, perimeter (= parapet/coping run).
# Thresholds sit between the survey's roof levels. UNVERIFIED (1 m raster, simplified 0.75 m). Run from montclair-state/north.
import json, numpy as np, shapely
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
g=json.load(open('data/north_geom.json')); Z=np.load('data/grid_1m.npz'); D=Z['dsm']
LV={'313021892':('dickson',[(140.5,149.0,'low ~145.2'),(149.0,155.0,'high ~152.7 (3rd/4th floors)')]),
    '313024770':('calcia',[(143.0,147.8,'lower strip ~147.4'),(147.8,149.6,'main ~148.2')]),
    '375626230':('feliciano',[(140.0,152.0,'low wing/terrace <152'),(152.0,160.0,'mid ~156.4'),(160.0,170.0,'high ~165')])}
out={}
for oid,(slug,levels) in LV.items():
    b=[x for x in g['buildings'] if x['osm_id']==oid][0]; P=Polygon(b['footprint'])
    x0,y0,x1,y1=[int(v) for v in P.bounds]; recs=[]
    for lo,hi,lab in levels:
        cells=[box(x,y,x+1,y+1) for y in range(y0-1,y1+2) for x in range(x0-1,x1+2) if lo<=D[y+260,x+600]<hi and P.contains(shapely.Point(x+.5,y+.5))]
        if not cells: continue
        U=unary_union(cells).buffer(0.6).buffer(-0.6).intersection(P).simplify(0.75)
        parts=[p for p in getattr(U,'geoms',[U]) if p.geom_type=='Polygon' and p.area>=12]
        recs.append(dict(level=lab,z_range=[lo,hi],z_p50=round(float(np.median([D[int(c.bounds[1])+260,int(c.bounds[0])+600] for c in cells])),2),
            n_cells=len(cells),parts=[dict(area_m2=round(p.area,1),perimeter_m=round(p.exterior.length,1),centroid=[round(v,1) for v in p.centroid.coords[0]],
            outline=[[round(x,2),round(y,2)] for x,y in p.exterior.coords]) for p in sorted(parts,key=lambda p:-p.area)]))
    out[slug]=dict(osm_id=oid,footprint_area_m2=round(P.area,1),footprint_perimeter_m=round(P.exterior.length,1),levels=recs)
json.dump(out,open('data/ov_prep/day6_roof_level_outlines_ov.json','w'),indent=1)
for s,v in out.items():
    print(s,v['footprint_area_m2'],v['footprint_perimeter_m']); [print('  ',l['level'],l['z_p50'],[(p['area_m2'],p['perimeter_m'],p['centroid']) for p in l['parts']]) for l in v['levels']]
