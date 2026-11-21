# Teaser sound

The soundtrack for the teaser film: field recordings, recorded sound effects and one public-domain
orchestral recording, cut and mixed to the film's shot list. No synthesised tones, generated music or
machine speech. Who recorded what, and under which licence, is in [CREDITS.md](CREDITS.md); publish
its credit block with the film.

Audio is media, not source: the recordings and the mix stay out of the repository. This folder holds
only the cue sheet, the mix script and the papers.

| File | What it does |
|---|---|
| `cues.json` | The cue sheet: the sources by key, and every cue (where, which recording, gain, filters, fades) |
| `mix.py` | Builds the mix from a folder of the recordings, the cue sheet and the film's clock |
| `timeline.mjs` | Prints the film's clock (shots, graphics, markers) from `../storyboard.mjs` as JSON |
| `shots.default.json` | A stand-in clock from the brief's arc, used when no storyboard clock is given |
| `CREDITS.md` | Every recording used: author, source, licence, credit text |

## Rebuild

```sh
# 1. fetch the recordings named in CREDITS.md into one folder, named by key (e.g. robin_nps.mp3)
# 2. the film's clock, from the storyboard
node tools/teaser/sound/timeline.mjs > /tmp/teaser-timeline.json
# 3. the mix: WAV (48 kHz, 24-bit), AAC in .m4a, stems, report.json; --video also muxes the film
python3 tools/teaser/sound/mix.py SRC_DIR OUT_DIR --timeline /tmp/teaser-timeline.json \
    [--video OUT/teaser.mp4]
```

Needs ffmpeg (6.x) and numpy. The master is set to -16 LUFS integrated with true peak at most
-1.5 dBTP (measured with ffmpeg's `ebur128`; `report.json` has the numbers for the WAV and the AAC).

## Cue sheet

Cues are placed by name, not by time, so a re-timed cut needs no new numbers:

- `[shot, 2.0]` 2 s into a shot, `[shot, "end-1.5"]` before its end, `[shot, "40%"]`;
- `{"marker": "glass"}` a storyboard marker (the pass through the entrance glass, `travel_peak`,
  `dusk_turn`, `ui_return` and so on); `marker_fallback` places each marker within its shot when the
  storyboard does not name it;
- `{"graphic": "title_main", "edge": "land"}` a 3D title's landing (`in`, `land` or `out`);
- `{"any": [a, b]}` the first of these that exists in the cut.

`shots`, `markers` and `graphics` map the names used in the cue sheet to the storyboard's names.

Per cue: `key` (the recording), `src` (seconds into it) or `align` (put a moment of the recording on
an anchor: the train horn on the station, the orchestra's first full chord on the peak of the
travelling shot, the last chord on the end title), `dur` or `until`, `gain` (dB), `hp` / `lp` (Hz),
`rev` (play backwards: a whoosh into a hit), `pan`, `width`, `env` (gain points in dB, by seconds or
anchors), `fade_in` / `fade_out` (equal-power), `bus` (`amb`, `place`, `music`, `fx`, `ui`) and
`duck` (the beds and the music dip under this cue).

Each 3D title has the same signature: a reversed cloth whoosh that lifts into it, a thump on a large
hollow wooden surface as it lands, and a small metal click as a glint. Dimension lines draw with a
pen scratch and two switch clicks; pins get a wooden tick.
