"""Probe Freeman Hall walls vs OSM 312845860 footprint."""
import bpy, json, os
from mathutils import Vector
OUT='/workspace/nj-scenes/montclair-state/data/uv/freeman_main_probe.json'
osm=json.load(open('/workspace/nj-scenes/montclair-state/data/uv/freeman_osm_probe.json'))
o=bpy.data.objects.get('Freeman Hall walls')
ro=bpy.data.objects.get('Freeman Hall roof (LiDAR)')
para=bpy.data.objects.get('UC_Freeman_parapet_coping_UNVERIFIED')
def bb(obj):
    if not obj: return None
    cs=[obj.matrix_world@Vector(c) for c in obj.bound_box]
    return dict(xmin=round(min(v.x for v in cs),3), xmax=round(max(v.x for v in cs),3),
                ymin=round(min(v.y for v in cs),3), ymax=round(max(v.y for v in cs),3),
                zmin=round(min(v.z for v in cs),3), zmax=round(max(v.z for v in cs),3),
                nverts=len(obj.data.vertices) if obj.type=='MESH' else 0,
                nfaces=len(obj.data.polygons) if obj.type=='MESH' else 0)
walls_bb=bb(o); roof_bb=bb(ro); para_bb=bb(para)
ob=osm['bbox']
dx0=walls_bb['xmin']-ob['xmin']; dx1=walls_bb['xmax']-ob['xmax']
dy0=walls_bb['ymin']-ob['ymin']; dy1=walls_bb['ymax']-ob['ymax']
# grade near north face mid
nf=None
for e in osm['edges']:
    if e['i']==6: nf=e; break
info=dict(
    session='uv', osm_id='312845860',
    walls=walls_bb, roof=roof_bb, parapet=para_bb,
    osm_bbox=ob,
    delta_walls_vs_osm_m=dict(dx_min=round(dx0,3),dx_max=round(dx1,3),dy_min=round(dy0,3),dy_max=round(dy1,3)),
    match='OK' if abs(dx0)<1.5 and abs(dx1)<1.5 and abs(dy0)<1.5 and abs(dy1)<1.5 else 'CHECK',
    ub_fix=bool(o.get('ub_fix')) if o else None,
    wall_top_z_sample=None,
    north_face_edge6=nf,
    objects_named_freeman=sorted([x.name for x in bpy.data.objects if 'freeman' in x.name.lower()]),
)
if o:
    zs=sorted(v.co.z for v in o.data.vertices)
    info['wall_top_z_sample']=dict(zmax=round(zs[-1],3), z_p95=round(zs[int(0.95*len(zs))],3), n_above_146=sum(1 for z in zs if z>=146.0))
json.dump(info, open(OUT,'w'), indent=2)
print('PROBE', json.dumps(info, indent=2)[:1200])
print('WROTE', OUT)
