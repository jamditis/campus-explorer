"""Soft check: Stone Hall upper ribbon band height vs object dims (UNVERIFIED; no DSM edit)."""
import bpy, json
out={}
for n in ('TI_Stone_Hall_313028565_lower_UNVERIFIED','TI_Stone_Hall_313028565_upper0_UNVERIFIED'):
    o=bpy.data.objects.get(n)
    if not o: continue
    bb=[o.matrix_world @ v.co for v in o.data.vertices]
    zs=[v.z for v in bb]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    out[n]=dict(zmin=round(min(zs),3), zmax=round(max(zs),3), zspan=round(max(zs)-min(zs),3),
                dim=tuple(round(x,2) for x in o.dimensions))
# upper0 is the top storey mass — ribbon should sit near its mid/lower band
# lower height ~9.8 m spans punched windows; upper ~3.3 m is ribbon storey — plausible 2-storey reading
note='Slide 285: upper continuous ribbon under thin eave; lower punched 2x2. Model has separate lower (~9.8m) + upper0 (~3.3m) masses. Ribbon band geometry itself not isolated as own mesh — likely shader window cuts on TR_Stone. Height split looks plausible for 2-storey + parapet; exact ribbon sill/head vs LiDAR UNVERIFIED — no fix this session.'
json.dump({'objs':out,'note':note}, open('/workspace/nj-scenes/montclair-state/data/vy/ribbon_probe.json','w'), indent=1)
print(json.dumps(out, indent=1))
print(note)
