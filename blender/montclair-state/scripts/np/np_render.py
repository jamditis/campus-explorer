import bpy, os
# np: no_render chain + studio rigging grid / hung grid items + NP atrium sprinklers hidden for cutaway cams only
src=open('scripts/no/no_render.py').read()
extra2='''
for o in bpy.data.objects:
    if o.name.startswith(('CCOM newsroom studio lighting grid','CCOM newsroom grid','CCOM newsroom robotic PTZ','NP sprinkler atrium','NP sprinkler 2F','NP sprinkler double-height')):
        cut.append(o)
'''
src=src.replace("exec(src,{'EXTRA2':extra,","exec(src,{'EXTRA2':extra+EXTRA3,",1)
exec(src,{'EXTRA3':extra2,'__name__':'npr'})
