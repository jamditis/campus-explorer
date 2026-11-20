import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fixTone, finishMetal } from '../viewer/tone.js';

const color = (r, g, b) => ({
  r, g, b,
  multiplyScalar(s) { this.r *= s; this.g *= s; this.b *= s; return this; },
});
const lum = c => c.r * 0.2126 + c.g * 0.7152 + c.b * 0.0722;

test('fixTone darkens Granite_Curb when the granite image was dropped', () => {
  const c = color(0.8, 0.8, 0.8);
  fixTone('Granite_Curb', c, false);
  const l = lum(c);
  assert.ok(Math.abs(l - 0.8 * 0.44) < 1e-9, `luminance ${l}`);
  assert.ok(l >= 0.25 && l <= 0.36, `mid-grey granite range, got ${l}`);
});

test('fixTone is a no-op when a base-color map is present', () => {
  const c = color(0.8, 0.8, 0.8);
  fixTone('Granite_Curb', c, true);
  assert.equal(lum(c), 0.8);
});

test('fixTone is a no-op for already mid-grey granite and for other stone', () => {
  const grey = color(0.39, 0.385, 0.375);
  const before = lum(grey);
  fixTone('WS35_grey_granite', grey, false);
  assert.equal(lum(grey), before);

  const sill = color(0.86, 0.84, 0.78);
  const sl = lum(sill);
  fixTone('MH_win_sill_cast_stone', sill, false);
  assert.equal(lum(sill), sl);

  const mid = color(0.35, 0.35, 0.35);
  fixTone('Granite_Curb', mid, false);
  assert.equal(lum(mid), 0.35);
});

test('fixTone restores authored amphitheater colours when the export collapsed to white or a pale factor', () => {
  const seat = color(1, 1, 1);
  fixTone('hn_amphi_seat_stone_blocks', seat, false);
  assert.equal(seat.r, 0.215);
  assert.equal(seat.g, 0.176);
  assert.equal(seat.b, 0.141);

  const stage = color(0.797, 0.787, 0.77);
  fixTone('io_amphi_stage_concrete', stage, false);
  assert.equal(stage.r, 0.25);

  const field = color(0.45, 0.45, 0.45);
  fixTone('hn_amphi_base_fieldstone', field, false);
  assert.equal(field.r, 0.22);

  // leave alone when the shipped colour already matches
  const ok = color(0.215, 0.176, 0.141);
  fixTone('hn_amphi_seat_stone_blocks', ok, false);
  assert.equal(ok.r, 0.215);
});

test('fixTone does not invent amphitheater colours when a map is present', () => {
  const c = color(1, 1, 1);
  fixTone('hn_amphi_seat_stone_blocks', c, true);
  assert.equal(lum(c), 1);
});

test('fixTone gives turf that lost its colour in the export the scripted turf tone', () => {
  // fs_turf (Pittser Field) ships as the export's neutral 0.45 grey
  const c = color(0.45, 0.45, 0.45);
  fixTone('fs_turf', c, false);
  assert.deepEqual([c.r, c.g, c.b], [0.03, 0.12, 0.04]);
  // an authored turf green is kept
  const own = color(0.029, 0.051, 0.025);
  fixTone('WS186_Sprague_artificial_turf_ortho2020_UNVERIFIEDtone', own, false);
  assert.deepEqual([own.r, own.g, own.b], [0.029, 0.051, 0.025]);
  // a grey lawn, or turf with its own image, is left alone
  const lawn = color(0.45, 0.45, 0.45);
  fixTone('COLE_lawn_post2020_bs', lawn, false);
  assert.equal(lawn.r, 0.45);
  const mapped = color(1, 1, 1);
  fixTone('SW_turf_painted_stadium_p037_0', mapped, true);
  assert.equal(mapped.r, 1);
  // white line paint on turf stays white
  const paint = color(1, 1, 1);
  fixTone('fs_turf_line_paint', paint, false);
  assert.equal(paint.g, 1);
});

import { fixCat } from '../viewer/cat.js';

test('fixCat refiles fieldstone and concrete bed curbs, and labels amphitheater nosings as stone', () => {
  assert.equal(fixCat('hn_amphi_base_fieldstone', 'grass'), 'stone');
  assert.equal(fixCat('WS159_bed_edge_concrete_curb', 'mulch'), 'concrete');
  assert.equal(fixCat('ip_amphi_aisle_nosing_worn', ''), 'stone');
  // do not steal real lawn or mulch
  assert.equal(fixCat('CCOM_lawn_grass', 'grass'), 'grass');
  assert.equal(fixCat('WS159_mulch_dark_shredded', 'mulch'), 'mulch');
});


test('fixCat files stainless and aluminium as metal, and a grass plinth as concrete', () => {
  assert.equal(fixCat('OD_stair_rail_satin_stainless_UNVERIFIED', 'concrete'), 'metal');
  assert.equal(fixCat('OD_stair_nosing_aluminium_UNVERIFIED', 'concrete'), 'metal');
  assert.equal(fixCat('fo_cogen_plinth', 'grass'), 'concrete');
  assert.equal(fixCat('CCOM_lawn_grass', 'grass'), 'grass');
});

test('finishMetal restores satin metalness and roughness after a concrete overwrite', () => {
  const rail = { metalness: 0, roughness: 0.85 };
  finishMetal('OD_stair_rail_satin_stainless_UNVERIFIED', rail);
  assert.equal(rail.metalness, 1);
  assert.equal(rail.roughness, 0.22);

  const nose = { metalness: 0, roughness: 0.85 };
  finishMetal('OD_stair_nosing_aluminium_UNVERIFIED', nose);
  assert.equal(nose.metalness, 0.8);
  assert.equal(nose.roughness, 0.38);

  const other = { metalness: 0, roughness: 0.85 };
  finishMetal('Wall_stucco_mission', other);
  assert.equal(other.metalness, 0);
  assert.equal(other.roughness, 0.85);

  const screen = { metalness: 0.2, roughness: 0.3 };
  finishMetal('NZ_screen_case_white_aluminium_UNVERIFIED', screen);
  assert.equal(screen.metalness, 0.2);
  assert.equal(screen.roughness, 0.3);

  const bin = { metalness: 1, roughness: 0.32 };
  finishMetal('OC_bin_brushed_stainless_UNVERIFIED', bin);
  assert.equal(bin.metalness, 1);
  assert.equal(bin.roughness, 0.32);
});
