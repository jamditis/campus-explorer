# ws129 self-review fix 2: S/island/E-ext curb tops followed every lot bump (wavy curb in the close-up) -> smooth ring heights along the run
# (moving average, 11 rings ~ 5 m), then rebuild the lawn aprons (main129f) with the outer edge dived 12 cm (GN-evaluated lawn sits ~10 cm under the base mesh).
import bpy, os, numpy as np
for o in [o for o in bpy.data.objects if o.name.startswith(('WS129_Chapin_S_lot_S_curb','WS129e_Chapin_S_lot_S_curb','WS129_Chapin_S_lot_island_E_curb','WS129_Chapin_S_lot_N_curb'))]:
    me=o.data; n=len(me.vertices)//4; z=np.array([me.vertices[4*k].co.z for k in range(n)])
    k=11 if n>30 else 5; pad=np.pad(z,k//2,mode='edge'); zs=np.convolve(pad,np.ones(k)/k,mode='valid')
    # keep it a clean straight-graded run: blend toward a linear fit
    c=np.polyfit(np.arange(n),z,2); zl=np.polyval(c,np.arange(n)); zs=0.5*zs+0.5*zl
    for i in range(n):
        d=zs[i]-z[i]
        for j in range(4): me.vertices[4*i+j].co.z+=d
    me.update(); print('M129g smoothed',o.name[:40],n,'max dz %.3f'%np.abs(zs-z).max())
src=open('/workspace/nj-scenes/montclair-state/scripts/ws129/main129f.py').read().replace("(zo+0.004)*s","(zo-0.12)*s")
os.environ['SAVE']='1'
exec(compile(src,'main129f','exec'),{'__name__':'__main__'})
