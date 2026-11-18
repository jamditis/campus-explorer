# one Blender pass: ws142 inspect + ws143 Lot 9/forecourt/band (main142b, no save) + ws145 walk N-end nose (saves OUT copy)
import bpy, os
OUTF=os.environ.get('OUT',''); os.environ['OUT']=''
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws142/insp142.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws143/main142b.py').read())
os.environ['OUT']=OUTF
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws145/nose145.py').read())
