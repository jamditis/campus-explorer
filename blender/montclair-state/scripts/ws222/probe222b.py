import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-253.3,-250.8,-55.3,-53.2
for nm in ['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width','WS70_gap_strip_grass_berms','WS69_CollegeAve_gap_strip_curbs_UNVERIFIED']:
    o=bpy.data.objects[nm]; M=o.matrix_world
    print('P222 ==',nm,len(o.data.vertices),len(o.data.polygons))
    for i,v in enumerate(o.data.vertices):
        w=M@v.co
        if X0<=w.x<=X1 and Y0<=w.y<=Y1: print('P222  v%d (%.3f,%.3f,%.3f)'%(i,w.x,w.y,w.z))
    if nm.startswith('WS72'):
        for p in o.data.polygons:
            c=M@p.center
            if X0<=c.x<=X1 and Y0<=c.y<=Y1: print('P222  f%d %s n(%.2f,%.2f,%.2f)'%(p.index,list(p.vertices),*p.normal))
