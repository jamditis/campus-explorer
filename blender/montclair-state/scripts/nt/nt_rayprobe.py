# nt: which surfaces does the cutaway aerial see over the CCOM block (applies the full nq render-chain hides, ray-casts instead of rendering)
import bpy, builtins, io, mathutils, os, collections
_open=builtins.open
def _p(path,*a,**k):
    if str(path).endswith('scripts/nh/nh_render.py'):
        t=_open(path).read().replace("bpy.ops.render.render(write_still=True)","bpy.app.driver_namespace['NTPROBE']()")
        return io.StringIO(t)
    return _open(path,*a,**k)
builtins.open=_p
def probe():
    sc=bpy.context.scene; cam=sc.camera
    hid=[o for o in bpy.data.objects if o.hide_render and not o.hide_viewport]
    for o in hid: o.hide_viewport=True
    dg=bpy.context.evaluated_depsgraph_get()
    fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]
    o0=cam.matrix_world.translation; cnt=collections.Counter(); zs={}
    N=int(os.environ.get('NG','80')); M=int(N*9/16)
    for i in range(N):
        for j in range(M):
            u=(i+.5)/N; v=(j+.5)/M
            p=fr[3]+(fr[0]-fr[3])*u; p=p+(fr[1]-fr[0])*0  # placeholder
            top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); q=top.lerp(bot,v)
            ok,loc,nor,idx,ob,mx=sc.ray_cast(dg,o0,(q-o0).normalized())
            if ok:
                k=(ob.name, 'ccom' if (-23<loc.x<16 and -16<loc.y<28) else 'out'); cnt[k]+=1; zs.setdefault(k,[]).append(loc.z)
    for (n,r),c in cnt.most_common(30):
        z=zs[(n,r)]; print('HIT|',c,r,'|',n,'| z',round(min(z),2),round(max(z),2))
    for o in hid: o.hide_viewport=False
bpy.app.driver_namespace['NTPROBE']=probe
os.environ.setdefault('OUT','/tmp/x_CAM.jpg')
exec(_open('scripts/nt/nt_build.py').read()); exec(_open('scripts/nt/nt_render.py').read())
