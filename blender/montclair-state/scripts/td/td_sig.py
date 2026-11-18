import bpy
o=bpy.data.objects
print('TDSIG',len(o),len(bpy.data.materials),[o[n].data.materials[0].name for n in ('SG_QuadRoad_full_313028548_549_UNVERIFIED','SG_WebsterRoad_313028543_UNVERIFIED','SG_Lot38_oil_stains_UNVERIFIED','SG_Lot38_curbs_UNVERIFIED')],'td_curbdir' in o['SG_Lot38_curbs_UNVERIFIED'].data.attributes)
