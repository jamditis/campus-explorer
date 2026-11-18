import bpy
for n in ('NG atrium red wall maroon doors 0 frame','NG atrium red wall maroon doors 0 frosted glass','NG atrium S wall red panel'):
    o=bpy.data.objects[n]; me=o.data
    print('PF',n,len(me.vertices),len(me.polygons),sorted(set(round((o.matrix_world@v.co).x,2) for v in me.vertices)),sorted(set(round((o.matrix_world@v.co).z,2) for v in me.vertices)))
