import bpy,bmesh
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws27/road.py').read().split('# ---- materials')[0])
ro=bpy.data.objects['Roads_OSM']; me=ro.data
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
for f in bm.faces:
    cc=f.calc_center_median()
    if cc.x>-252 and -170<cc.y<-45:
        d=dist(cc.x,cc.y)
        if d<12: print('F',f.index,'c(%.1f,%.1f,%.2f)'%(cc.x,cc.y,cc.z),'d%.1f'%d,'a%.1f'%f.calc_area())
