import bpy
for n in ('OG_Schmitt_E_entrance_storefront_frame','OG_Schmitt_E_entrance_landing','OG_Schmitt_E_entrance_glass','OG_Schmitt_E_entrance_vestibule_dark'):
    o=bpy.data.objects[n]; zs=[(o.matrix_world@v.co).z for v in o.data.vertices]; print('Z',n,round(min(zs),2),round(max(zs),2))
fp=bpy.data.objects['Footpaths_OSM']
zs=[(fp.matrix_world@v.co) for v in fp.data.vertices]; near=[v.z for v in zs if (v.x-10.6)**2+(v.y-141.1)**2<16]; print('FPnear',round(min(near),2) if near else None, round(max(near),2) if near else None)
