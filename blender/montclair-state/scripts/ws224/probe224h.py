import bpy
from mathutils import Vector
G=bpy.data.objects['WS222_CollegeAve_return_gutter_asphalt_fill_UNVERIFIED']; M=G.matrix_world
print('P224 G nv',len(G.data.vertices),'nf',len(G.data.polygons))
for v in G.data.vertices: print('P224 gv',v.index,tuple(round(c,3) for c in M@v.co))
C=bpy.data.objects['WS27_CollegeAve_carriageway_2020ortho']; MC=C.matrix_world
for p in C.data.polygons:
    c=MC@p.center
    if p.material_index==1 and -249.5<c.x<-246 and -54<c.y<-52.5:
        print('P224 pan f%d'%p.index,[tuple(round(x,3) for x in MC@C.data.vertices[i].co) for i in p.vertices])
