# pq wrapper: rebuild the Feliciano tier re-mass from data/pq (po outlines with short diagonal corner chamfers squared,
# re-nested; eaves/gutters re-derived), then po roof detail + gutters, then pq_snap (tier walls parallel to + 3 cm inside
# nearby old LiDAR wall planes, tier windows carried). REVERT=1 -> exact po state (rebuild from data/po). ALL UNVERIFIED.
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'
def run(path,rev,src=None,gsrc=None):
    code=open(path).read()
    if src: code=code.replace('data/pn/polys.json',src+'/polys.json').replace('data/pn/eaves.json',src+'/eaves.json')
    if gsrc: code=code.replace('data/po/gutters.json',gsrc+'/gutters.json')
    if rev: os.environ['REVERT']='1'
    else: os.environ.pop('REVERT',None)
    exec(compile(code,path,'exec'),{'__name__':'__main__'})
run('scripts/pq/pq_oldtop.py',True); run('scripts/pq/pq_snap.py',True)
run('scripts/po/po_gutters.py',True); run('scripts/po/po_roofdetail.py',True)
for s in ('pn_windows','pn_eaves','pn_remass'): run('scripts/pn/%s.py'%s,True)
src='data/po' if REV else 'data/pq'
run('scripts/pn/pn_remass.py',False,src); run('scripts/pn/pn_eaves.py',False,src); run('scripts/pn/pn_windows.py',False)
run('scripts/po/po_roofdetail.py',False); run('scripts/po/po_gutters.py',False,None,src)
if not REV: run('scripts/pq/pq_snap.py',False); run('scripts/pq/pq_oldtop.py',False)
print('PQ_MAIN done REV',REV,'src',src,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('PQSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
