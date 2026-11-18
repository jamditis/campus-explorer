# Short station search for NW lower W closeup (avoid black/tree frames).
import bpy, json, math
from mathutils import Vector
ROOT='/workspace/nj-scenes/montclair-state'
d=json.load(open(ROOT+'/data/wc/apply.json'))
O=Vector((d['origin'][0], d['origin'][1], 0))
U=Vector((d['U'][0], d['U'][1], 0))
N=Vector((d['N'][0], d['N'][1], 0))
tm=d['frame_tm']
dg=bpy.context.evaluated_depsgraph_get()
# target point mid-facade
target = O + U*tm + N*0.2; target.z = 128.0
stations=[]
for dt in (-4, -2, 0, 2, 4):
  for n in (12, 16, 20, 24, 28):
    for z in (126.0, 130.0, 134.0, 138.0):
      p = O + U*(tm+dt) + N*n; p.z=z
      # ray toward target
      direction = (target - p)
      dist = direction.length
      if dist < 1: continue
      direction.normalize()
      hit, loc, nrm, idx, obj, mat = bpy.context.scene.ray_cast(dg, p, direction, distance=dist-0.3)
      # also check free air: short probe forward clear of near hits in first 2m
      hit2,_,_,_,_,_ = bpy.context.scene.ray_cast(dg, p, direction, distance=2.0)
      # upward clear (not buried)
      hit_up,_,_,_,_,_ = bpy.context.scene.ray_cast(dg, p, Vector((0,0,1)), distance=1.0)
      hit_dn, loc_dn,_,_,obj_dn,_ = bpy.context.scene.ray_cast(dg, p+Vector((0,0,2)), Vector((0,0,-1)), distance=50)
      ground_z = loc_dn.z if hit_dn else None
      stations.append(dict(
        dt=dt,n=n,z=z,
        hit_facade=bool(hit), hit_obj=(obj.name[:40] if hit and obj else None),
        near_blocked=bool(hit2), buried=bool(hit_up),
        ground_z=round(ground_z,2) if ground_z is not None else None,
        above_g=round(z-(ground_z or z),2) if ground_z is not None else None,
        px=round(p.x,2), py=round(p.y,2),
      ))
# prefer: not near_blocked, not buried, hit_facade, above_g > 1.5, hits Bohn/WC
good=[s for s in stations if not s['near_blocked'] and not s['buried'] and s['hit_facade'] and (s['above_g'] or 0)>1.0]
# score: prefer WC/TK/TL hit, mid n
def score(s):
  sc=0
  name=s['hit_obj'] or ''
  if 'WC_' in name or 'Bohn' in name or 'VW_' in name: sc+=5
  if 16<=s['n']<=24: sc+=2
  if 128<=s['z']<=136: sc+=2
  if abs(s['dt'])<=2: sc+=1
  return sc
good.sort(key=lambda s: (-score(s), s['n']))
out=dict(n_stations=len(stations), n_good=len(good), top=good[:12], target=[round(target.x,2),round(target.y,2),round(target.z,2)])
json.dump(out, open(ROOT+'/data/wc/cam_search.json','w'), indent=2)
print('stations', len(stations), 'good', len(good))
for s in good[:8]:
  print('OK', s)
if not good:
  # show near misses
  almost=[s for s in stations if not s['buried'] and s['hit_facade']]
  print('almost', len(almost))
  for s in almost[:8]: print('AL', s)
