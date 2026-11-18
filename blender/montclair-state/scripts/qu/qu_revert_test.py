import os,bpy
os.environ['REVERT']='1'
try: exec(open('scripts/qu/qu_main.py').read())
except SystemExit: pass
exec(open('scripts/qu/qu_sig.py').read())
og=bpy.data.materials['QP_Richardson_glass_bronze_dark_UNVERIFIED']; print('fake',og.use_fake_user, [m.name for m in bpy.data.materials if m.name.startswith(('QU_','KIT_'))][:20])
