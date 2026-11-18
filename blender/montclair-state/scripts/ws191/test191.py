# probe-mode test (modifiers off, never saved): build fix191 node tree + fix191b fill, then re-run the coverage map
import bpy
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws191/fix191.py').read())
exec(open(S+'ws191/fix191b.py').read())
exec(open(S+'ws191/probe191d.py').read())
