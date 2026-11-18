import bpy, math
for n in ('WS131_E_building_W_foot_mulch_bed_tree0001_UNVERIFIED','WS131_lot_E_drive_S_of_E_building_LiDAR2023_UNVERIFIEDend_x-170'):
    o=bpy.data.objects.get(n); me=o.data
    bad=[v.index for v in me.vertices if any(math.isnan(c) for c in v.co)]
    print('NAN',n,len(me.vertices),len(bad))
print('MATS',[m.name for m in bpy.data.materials if any(k in m.name.lower() for k in ('stucco','tile','chapin','roof','membrane','glass','window','trim'))][:60])
for o in bpy.data.objects:
    if o.name.startswith(('Roof_vent','Exhaust','WS1','Bldg')) and o.type=='MESH':
        pass
import collections
c=collections.Counter(o.name.split('.')[0][:18] for o in bpy.data.objects if -182<o.location.x<-120 and -265<o.location.y<-224)
print('NEAR',c.most_common(30))
