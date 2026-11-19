# ws233 fix d (on ws233b): Stone Hall upper storey window row. upper0 (walls 139.9..143.17) shared the old datum ti_z0 = 135.888, so its
# only row ran 140.04..141.51 and its bottom 0.5 m sat BEHIND the lower volume's fascia ledge (TQ_Stone_fascia_lower 140.11..140.55) -
# half-height windows in the ws233 SE eye view; a window cannot run behind a ledge. upper0 ti_z0 -> 139.7: row 140.65..142.12 (clear of
# the ledge top 140.55, under the z1-0.9 = 142.27 top gate). Second-floor sill height above its slab UNVERIFIED (1966 slides: upper
# windows sit high under the roof fascia).
import bpy, json
MS='/workspace/nj-scenes/montclair-state/'
o=bpy.data.objects['TI_Stone_Hall_313028565_upper0_UNVERIFIED']; a=o.data.attributes['ti_z0']
old=sorted(set(round(x.value,3) for x in a.data))
for x in a.data: x.value=139.7
rep={'upper0_ti_z0':[old,139.7]}
print('F233D',json.dumps(rep),flush=True); json.dump(rep,open(MS+'scripts/ws233/fix233d_report.json','w'))
