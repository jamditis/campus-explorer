import bpy,json
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=L.matrix_world; me=L.data
V=[tuple(M@v.co) for v in me.vertices]
F=[(p.index,list(p.vertices),p.normal.z) for p in me.polygons]
# also curb objects outline
out={'V':V,'F':F,'curb':{}}
for n in ('WS220_CollegeAve_curb_jog_return','WS27_CollegeAve_curb_left'):
    for o in bpy.data.objects:
        if o.name.startswith(n) and o.type=='MESH':
            Mo=o.matrix_world
            out['curb'][o.name]=[tuple(Mo@v.co) for v in o.data.vertices if -250<(Mo@v.co).x<-246.5 and -54.5<(Mo@v.co).y<-51.5]
json.dump(out,open('/tmp/ws224_land.json','w')); print('P224 dumped')
