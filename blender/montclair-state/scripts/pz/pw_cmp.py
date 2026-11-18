import bpy, hashlib
exec(open('scripts/pn/pn_sig.py').read())
rv=bpy.data.objects['PV2_Dickson_window_reveals_glass_UNVERIFIED']
print('PV2MATS',[m.name for m in rv.data.materials],'PROPS',sorted(rv.keys()))
print('MATNAMES',hashlib.sha1(','.join(sorted(m.name for m in bpy.data.materials)).encode()).hexdigest()[:12])
