import bpy
o=bpy.data.objects['Feliciano School of Business walls']; mw=o.matrix_world
exec(open('scripts/pq/pq_probe.py').read().split("probe('PK")[0])
probe('PO_CAM_closeup_feliciano_gutter_downpipe',[(900,430),(960,420),(1000,400),(900,400),(960,395)])
for fi in (141,):
    p=o.data.polygons[fi]; print('F',fi,[tuple(round(c,2) for c in mw@o.data.vertices[i].co) for i in p.vertices])
