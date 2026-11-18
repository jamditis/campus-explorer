import bpy,os
R='/workspace/nj-scenes/montclair-state'
exec(open(R+'/scripts/ws32/fix.py').read()); exec(open(R+'/scripts/ws32/fix2.py').read())
src=open(R+'/scripts/ws32/render.py').read()
os.environ['CAMS']=''
exec(src.split("if os.environ.get('FIX')",1)[0]+src.split("exec(open(R+'/scripts/ws32/hidepa.py').read())",1)[1])
exec(open(R+'/scripts/ws32/pick.py').read())
