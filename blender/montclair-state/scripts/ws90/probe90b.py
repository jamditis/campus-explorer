import bpy,json,math
OB=bpy.data.objects
out={}
for n,k in (('WS27_CollegeAve_curb_right_UNVERIFIED',6),('WS27_CollegeAve_curb_left_UNVERIFIED',6),('WS27_CollegeAve_carriageway_2020ortho',7)):
    o=OB[n]; mw=o.matrix_world
    V=[tuple(mw@v.co) for v in o.data.vertices]
    out[n]={'V':V,'F':[list(p.vertices) for p in o.data.polygons][:20],'mw':[list(r) for r in mw]}
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws90/ws27_dump.json','w'))
print('P90B done')
