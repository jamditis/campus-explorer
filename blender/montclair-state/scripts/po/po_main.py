# po wrapper: (1) rebuild the pn Feliciano re-mass from the smoothed+nested data/po polys/eaves (staircase eaves -> straight runs),
# (2) membrane/RTU/drain detail (po_roofdetail.py). REVERT=1: undo (2), then rebuild pn exactly from data/pn (pre-session state).
# ALL UNVERIFIED. Save with POSAVE=1 or SAVEAS=path.
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; SAVEAS=os.environ.pop('SAVEAS',None); argv=sys.argv; sys.argv=[a for a in argv if a!='--save']
def run(path,rev,src=None):
    code=open(path).read()
    if src: code=code.replace('data/pn/polys.json',src+'/polys.json').replace('data/pn/eaves.json',src+'/eaves.json')
    if rev: os.environ['REVERT']='1'
    else: os.environ.pop('REVERT',None)
    exec(compile(code,path,'exec'),{'__name__':'__main__'})
run('scripts/po/po_gutters.py',True); run('scripts/po/po_roofdetail.py',True)
for s in ('pn_windows','pn_eaves','pn_remass'): run('scripts/pn/%s.py'%s,True)
src='data/pn' if REV else 'data/po'
run('scripts/pn/pn_remass.py',False,src); run('scripts/pn/pn_eaves.py',False,src); run('scripts/pn/pn_windows.py',False)
if not REV: run('scripts/po/po_roofdetail.py',False); run('scripts/po/po_gutters.py',False)
print('PO_MAIN done REV',REV,'src',src,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if SAVEAS: bpy.ops.wm.save_as_mainfile(filepath=SAVEAS,copy=True); print('SAVED_AS',SAVEAS)
if os.environ.get('POSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
