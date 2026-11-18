import bpy, hashlib, os
objs=sorted(o.name for o in bpy.data.objects); mats=sorted(m.name for m in bpy.data.materials)
me=bpy.data.objects['Freeman Hall walls'].data
vh=hashlib.sha1(b''.join(f'{v.co.x:.5f},{v.co.y:.5f},{v.co.z:.5f};'.encode() for v in me.vertices)).hexdigest()[:16]
s=f"UBSIG O{len(objs)} M{len(mats)} {hashlib.sha1(chr(10).join(objs).encode()).hexdigest()[:12]} {hashlib.sha1(chr(10).join(mats).encode()).hexdigest()[:12]} FV{vh} prop{bpy.data.objects['Freeman Hall walls'].get('ub_fix')}"
print(s)
