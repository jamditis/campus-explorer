import bpy,os
os.environ['DRY']='1'
exec(open('scripts/pr/pr_tiersnap.py').read())
