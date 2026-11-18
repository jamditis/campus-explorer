import bpy
o=bpy.data.objects['Center for Computing and Information Science walls']; me=o.data
for i in (34,35,36,37,38,39):
    p=me.polygons[i]; print('F',i,[tuple(round(c,2) for c in me.vertices[v].co) for v in p.vertices],tuple(round(c,2) for c in p.normal))
