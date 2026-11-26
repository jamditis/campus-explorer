cd /workspace/nj-scenes/montclair-state
while pgrep -f shoot.mjs >/dev/null; do sleep 3; done
F=montclair_state_ws251b.blend TAGM=ws251b_BEFORE D=test ONLY=2 GATE=6000 bash scripts/ws252/jobwip252.sh
F=montclair_state_ws252b.blend TAGM=ws252b D=test ONLY=24 GATE=6000 bash scripts/ws252/jobwip252.sh
echo TESTSDONE
