import bpy,hashlib
for N,U in (('Dickson Hall walls','facade'),('PU_Dickson_window_frames_UNVERIFIED',None)):
    me=bpy.data.objects[N].data; h=hashlib.sha1()
    for v in me.vertices: h.update(('%.5f %.5f %.5f'%tuple(v.co)).encode())
    for p in me.polygons: h.update((str(tuple(p.vertices))+str(p.material_index)).encode())
    if U:
        for l in me.uv_layers[U].data: h.update(('%.4f %.4f'%tuple(l.uv)).encode())
    print('COHASH',N,h.hexdigest()[:12],len(me.vertices),len(me.polygons))
