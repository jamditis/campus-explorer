import bpy,hashlib
for on in ('PN_Feliciano_eaves_UNVERIFIED','PO_Feliciano_gutters_downpipes_UNVERIFIED','PR_Calcia_slot_surrounds_UNVERIFIED','Feliciano School of Business walls','Calcia Hall walls'):
    me=bpy.data.objects[on].data; h=hashlib.sha1()
    for v in me.vertices: h.update(('%.5f %.5f %.5f'%tuple(v.co)).encode())
    for p in me.polygons: h.update(str(tuple(p.vertices)).encode())
    print('COHASH',on[:20],h.hexdigest()[:12],len(me.vertices),len(me.polygons))
