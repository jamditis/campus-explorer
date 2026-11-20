import test from 'node:test';
import assert from 'node:assert/strict';
import { fixCat, isSeeThroughSolid } from '../viewer/cat.js';

test('a category from the export is kept when nothing is known against it', () => {
  assert.equal(fixCat('WS27_curb_concrete_UNVERIFIED', 'concrete'), 'concrete');
  assert.equal(fixCat('SW_turf_painted_p013_0', 'turf'), 'turf');
  assert.equal(fixCat('SW_asphalt_painted_p009_1', 'asphalt'), 'asphalt');
});

test('known misfilings are corrected', () => {
  assert.equal(fixCat('WS172_lawn_fade_nostripe_WS175', 'glass'), 'grass');
  assert.equal(fixCat('WS187_Sprague_field_paint_white_UNVERIFIED', 'grass'), '');
  assert.equal(fixCat('KX_drive_concrete', 'asphalt'), 'concrete');
  assert.equal(fixCat('Bark_Maple', ''), 'bark');
  assert.equal(fixCat('Roof_barrel_tile_course', ''), 'rooftile');
});

test('synthetic turf the exporter filed as lawn is turf', () => {
  // Pittser Field (north model) and a strip of Sprague turf in the main model: the exporter's
  // grass rule matches "turf", and only SW_ names get the turf category
  assert.equal(fixCat('fs_turf', 'grass'), 'turf');
  assert.equal(fixCat('WS186_Sprague_artificial_turf_ortho2020_UNVERIFIEDtone', 'grass'), 'turf');
  // lawns stay lawn, field paint stays paint, fieldstone stays stone
  assert.equal(fixCat('CCOM_lawn_grass', 'grass'), 'grass');
  assert.equal(fixCat('BD_farfield_ortho_haze', 'grass'), 'grass');
  assert.equal(fixCat('turfgrass_lawn', 'grass'), 'grass');
  assert.equal(fixCat('fs_turf_line_paint', 'grass'), '');
  assert.equal(fixCat('hn_amphi_base_fieldstone', 'grass'), 'stone');
});

test('fence fabric and netting exported as glass are see-through metal', () => {
  assert.equal(fixCat('MH_chainlink_galv', 'glass'), 'metal');
  assert.equal(fixCat('fs_goal_net', 'glass'), 'metal');
  assert.equal(isSeeThroughSolid('MH_chainlink_galv', 'glass'), true);
  assert.equal(isSeeThroughSolid('SW_metal_chainlink_black', 'metal'), true);
});

test('window and lamp glass, and see-through materials without a category, stay glass', () => {
  assert.equal(isSeeThroughSolid('CELS_win_glass_thin', 'glass'), false);
  assert.equal(isSeeThroughSolid('Glass_Lamp_Frosted', 'glass'), false);
  assert.equal(isSeeThroughSolid('some_unnamed_clear_thing', ''), false);
});

test('water of the scripted build is water, and nothing else that mentions water is', () => {
  assert.equal(fixCat('SW_water_base', 'water'), 'water');
  assert.equal(fixCat('SW_water_base', ''), 'water'); // an export without the water category
  assert.equal(fixCat('NA_water_bottle_clear_UNVERIFIED', 'glass'), 'glass');
  assert.equal(fixCat('CCM office water bottles (na)', ''), '');
});
