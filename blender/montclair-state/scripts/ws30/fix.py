import os, json
R='/workspace/nj-scenes/montclair-state'
os.environ['DBOX']='-175,70,-200,70'; exec(open(R+'/scripts/ws30/drape.py').read())
for box,raise_,tag in (('46,66,-94,-74','0','e56_SLOPE9'),('-100,-50,-75,-15','0','cole'),('-174,-100,-120,-90','0','kE')):
    os.environ['BOX']=box; os.environ['TAG']=tag; os.environ['SLOPE']='9' if 'SLOPE9' in tag else '0.45'; os.environ['RAISE']=raise_; os.environ.pop('DELROADS',None)
    exec(open(R+'/scripts/ws30/seat.py').read())
