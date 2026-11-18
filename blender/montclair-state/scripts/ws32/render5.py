import bpy,os
R='/workspace/nj-scenes/montclair-state'
exec(open(R+'/scripts/ws32/skirt.py').read())
s=open(R+'/scripts/ws32/render.py').read().replace("if os.environ.get('FIX')=='1':","if False:")
exec(s)
