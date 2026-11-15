import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const Q = new URLSearchParams(location.search);
const stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
stage.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;
const camera = new THREE.PerspectiveCamera(32, innerWidth / innerHeight, 1, 5000);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.target.set(0, 75, 0);
controls.minDistance = 120; controls.maxDistance = 1400;

scene.add(new THREE.HemisphereLight(0xdfefff, 0x20242a, 0.6));
const sun = new THREE.DirectionalLight(0xffffff, 1.6);
sun.position.set(220, 420, 260); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -260, right: 260, top: 260, bottom: -260, near: 50, far: 1200 });
scene.add(sun);
const ground = new THREE.Mesh(new THREE.CircleGeometry(900, 64), new THREE.ShadowMaterial({ opacity: 0.28 }));
ground.rotation.x = -Math.PI / 2; ground.position.y = -3.6; ground.receiveShadow = true; scene.add(ground);
const grid = new THREE.PolarGridHelper(420, 12, 8, 96, 0x2a3644, 0x1c2530);
grid.position.y = -3.5; scene.add(grid);

// robot frame: z-up mm  ->  three y-up
const root = new THREE.Group(); root.rotation.x = -Math.PI / 2; scene.add(root);
const AX = 80;
const LAYERS = { shell: ['Shell', '#f3efe7'], drive: ['Drive', '#bfefff'], electronics: ['Electronics', '#1f9f6a'],
  power: ['Power', '#3a7bd5'], sensors: ['Sensors', '#55bb33'], dock: ['Dock', '#d9d3c8'] };
const LABELED = { pod_front: 'Pod shell', ring_L: 'Halo ring = wheel + body', tread_R: 'TPU tread', display: 'Round display eyes',
  camera: 'Camera', battery: '18650 = pendulum mass', ballast_keel: 'Steel keel', motor_L: 'N20 motor', pinion_R: 'Pinion → ring gear',
  main_pcb: 'Main board', esp32s3_module: 'ESP32-S3', speaker: 'Speaker', tof_cliff: 'Cliff ToF', tof_front: 'Front ToF',
  halo_leds: 'Halo LEDs', dock: 'Lily-pad dock', idler_L_top: 'Idler roller', mic_flex: 'Mics', belly_pads: 'Charge pads', eye_lens: 'Eye lens' };

const EXTERNAL = new Set(['pod_front', 'ring_L', 'tread_R', 'eye_lens', 'camera', 'dock', 'tof_front']);
const parts = {}; let explodeT = +(Q.get('explode') || 0), xray = Q.get('xray') === '1', showLabels = Q.get('labels') !== '0', demo = false, selected = null;
const layerOn = Object.fromEntries(Object.keys(LAYERS).map(k => [k, true]));

function b64ToBuf(s) { const bin = atob(s); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u.buffer; }

function makeMaterial(p) {
  const c = new THREE.Color(p.color);
  const id = p.id;
  if (id.startsWith('ring')) return new THREE.MeshPhysicalMaterial({ color: c, roughness: 0.38, metalness: 0, transparent: true, opacity: 0.62,
    emissive: new THREE.Color('#38c8ff'), emissiveIntensity: 0.32, clearcoat: 0.6, side: THREE.DoubleSide, depthWrite: false });
  if (id === 'eye_lens') return new THREE.MeshPhysicalMaterial({ color: c, roughness: 0.05, metalness: 0, transparent: true, opacity: 0.28, clearcoat: 1, depthWrite: false });
  const metal = /motor|shaft|pin_|keel|esp32|pogo|pads/.test(id);
  return new THREE.MeshStandardMaterial({ color: c, roughness: metal ? 0.35 : (id.startsWith('tread') ? 0.85 : 0.48), metalness: metal ? 0.65 : 0.02, side: THREE.DoubleSide });
}

function eyeTexture() {
  const cv = document.createElement('canvas'); cv.width = cv.height = 256; const g = cv.getContext('2d');
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  tex.draw = (blink, look) => {
    g.fillStyle = '#05070b'; g.fillRect(0, 0, 256, 256);
    const h = 70 * (1 - blink) + 6;
    for (const sx of [-1, 1]) {
      const cx = 128 + sx * 46 + look * 10, cy = 122;
      const grd = g.createRadialGradient(cx, cy, 4, cx, cy, 42); grd.addColorStop(0, '#d8fbff'); grd.addColorStop(1, '#46d6ff');
      g.fillStyle = grd; g.beginPath(); g.ellipse(cx, cy, 26, h / 2, 0, 0, Math.PI * 2); g.fill();
    }
    g.strokeStyle = '#46d6ff'; g.lineWidth = 5; g.lineCap = 'round'; g.beginPath(); g.arc(128, 168, 16, 0.2 * Math.PI, 0.8 * Math.PI); g.stroke();
    tex.needsUpdate = true;
  };
  tex.draw(0, 0); return tex;
}

const loadingEl = document.getElementById('loading');
fetch('assets/ringo_model.json').then(r => r.json()).then(data => {
  for (const p of data.parts) {
    const q = new Int16Array(b64ToBuf(p.pos)); const pos = new Float32Array(q.length);
    for (let i = 0; i < q.length; i++) pos[i] = q[i] * data.scale;
    const idx = p.i32 ? new Uint32Array(b64ToBuf(p.idx)) : new Uint16Array(b64ToBuf(p.idx));
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setIndex(new THREE.BufferAttribute(idx, 1));
    geo.computeVertexNormals();
    const mat = makeMaterial(p);
    const mesh = new THREE.Mesh(geo, mat); mesh.castShadow = !/ring|lens/.test(p.id); mesh.receiveShadow = true;
    const grp = new THREE.Group(); grp.add(mesh); root.add(grp);
    mesh.userData.part = p.id;
    parts[p.id] = { meta: p, grp, mesh, mat, baseOpacity: mat.opacity, baseTransparent: mat.transparent };
  }
  // animated face on the display
  const tex = eyeTexture(); parts.display.tex = tex;
  const face = new THREE.Mesh(new THREE.CircleGeometry(16.2, 64), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }));
  face.position.set(59.85, 0, AX); face.rotation.set(0, Math.PI / 2, 0); face.rotation.z = -Math.PI / 2;
  parts.display.grp.add(face);
  // halo glow lights inside rings
  for (const s of [1, -1]) { const L = new THREE.PointLight(0x5fd8ff, 900, 160, 2); L.position.set(0, 37 * s, AX + 40); parts['halo_leds'].grp.add(L); }
  buildUI(); applyMaterials(); setView(Q.get('view') || '34', true);
  if (Q.get('panel') === '0') document.getElementById('panel').classList.add('closed');
  fetch('assets/bom.json').then(r => r.json()).then(b => {
    document.getElementById('bproto').textContent = '$' + b.proto_total.toFixed(0);
    document.getElementById('bvol').textContent = '$' + b.volume_total.toFixed(2);
    document.getElementById('btool').textContent = '$' + Math.round(b.tooling_total / 1000) + 'k';
  }).catch(() => {});
  requestAnimationFrame(() => requestAnimationFrame(() => document.body.classList.add('loaded')));
}).catch(e => { loadingEl.querySelector('span').textContent = 'Failed to load model: ' + e; console.error(e); });

// ---------- UI ----------
const labelsEl = document.getElementById('labels'); const labelDivs = {};
function buildUI() {
  const lay = document.getElementById('layers');
  for (const [k, [name, col]] of Object.entries(LAYERS)) {
    const b = document.createElement('button'); b.className = 'on'; b.innerHTML = `<span class="sw" style="background:${col}"></span>${name}`;
    b.onclick = () => { layerOn[k] = !layerOn[k]; b.classList.toggle('on', layerOn[k]); applyVisibility(); }; lay.appendChild(b);
  }
  for (const [id, txt] of Object.entries(LABELED)) {
    if (!parts[id]) continue;
    const d = document.createElement('div'); d.className = 'lbl'; d.textContent = txt; d.onclick = () => select(id); labelsEl.appendChild(d); labelDivs[id] = d;
  }
  document.querySelectorAll('#views button').forEach(b => b.onclick = () => setView(b.dataset.v));
  const xb = document.getElementById('xray'); xb.classList.toggle('on', xray); xb.onclick = () => { xray = !xray; xb.classList.toggle('on', xray); applyMaterials(); };
  const lb = document.getElementById('lbl'); lb.classList.toggle('on', showLabels); lb.onclick = () => { showLabels = !showLabels; lb.classList.toggle('on', showLabels); };
  const db = document.getElementById('demo'); db.onclick = () => { demo = !demo; db.classList.toggle('on', demo); };
  const ex = document.getElementById('explode'); ex.value = explodeT; ex.oninput = () => { explodeT = +ex.value; };
  document.getElementById('infoclose').onclick = () => select(null);
  document.getElementById('ptoggle').onclick = () => { const p = document.getElementById('panel'); p.classList.toggle('closed'); document.getElementById('ptoggle').textContent = p.classList.contains('closed') ? '⟨' : '⟩'; };
  applyVisibility();
}
function applyVisibility() { for (const p of Object.values(parts)) p.grp.visible = layerOn[p.meta.layer]; }
function isSkin(id) { return /pod_|eye_lens|ring|tread|dock$/.test(id); }
function applyMaterials() {
  for (const [id, p] of Object.entries(parts)) {
    const m = p.mat;
    if (xray && isSkin(id)) { m.transparent = true; m.opacity = 0.09; m.depthWrite = false; p.mesh.castShadow = false; }
    else { m.transparent = p.baseTransparent; m.opacity = p.baseOpacity; m.depthWrite = !p.baseTransparent; p.mesh.castShadow = !/ring|lens/.test(id); }
    if (m.emissive && !id.startsWith('ring')) m.emissive.set(id === selected ? 0x2a6f88 : 0x000000);
    m.needsUpdate = true;
  }
}
function select(id) {
  selected = id; const box = document.getElementById('info');
  if (!id) { box.classList.add('hidden'); applyMaterials(); return; }
  const m = parts[id].meta;
  document.getElementById('iname').textContent = m.name;
  document.getElementById('imat').textContent = m.material;
  document.getElementById('itext').textContent = m.info;
  document.getElementById('isize').textContent = `Envelope ${m.size.join(' × ')} mm · layer: ${LAYERS[m.layer][0]}`;
  box.classList.remove('hidden'); applyMaterials();
}
const ray = new THREE.Raycaster(); const ptr = new THREE.Vector2(); let downAt = null;
renderer.domElement.addEventListener('pointerdown', e => downAt = [e.clientX, e.clientY]);
renderer.domElement.addEventListener('pointerup', e => {
  if (!downAt || Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 5) return;
  ptr.set(e.clientX / innerWidth * 2 - 1, -e.clientY / innerHeight * 2 + 1); ray.setFromCamera(ptr, camera);
  const cands = Object.entries(parts).filter(([id, p]) => p.grp.visible && !(xray && isSkin(id))).map(([, p]) => p.mesh);
  const hit = ray.intersectObjects(cands, false)[0]; select(hit ? hit.object.userData.part : null);
});

// ---------- views ----------
const VIEWS = { '34': [300, 190, 330], front: [470, 80, 0], side: [0, 80, -470], top: [1, 520, 0], back: [-470, 90, 0] };
let tween = null;
function setView(v, instant) {
  document.querySelectorAll('#views button').forEach(b => b.classList.toggle('on', b.dataset.v === v));
  const to = new THREE.Vector3(...(VIEWS[v] || VIEWS['34'])); const tgt = new THREE.Vector3(0, 70, 0);
  if (innerWidth < 900) to.multiplyScalar(1.5);
  if (instant) { camera.position.copy(to); controls.target.copy(tgt); controls.update(); return; }
  tween = { from: camera.position.clone(), to, ft: controls.target.clone(), tt: tgt, t: 0 };
}

// ---------- animate ----------
const clock = new THREE.Clock(); let rollAng = 0, tAcc = 0, nextBlink = 2;
const v3 = new THREE.Vector3();
function placeAboutAxle(grp, theta, off) {   // rotate about robot-y axis through (0,0,AX)
  grp.rotation.set(0, theta, 0);
  grp.position.set(off[0] - AX * Math.sin(theta), off[1], off[2] + AX - AX * Math.cos(theta));
}
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05); tAcc += dt;
  if (tween) { tween.t = Math.min(1, tween.t + dt * 1.6); const k = 1 - Math.pow(1 - tween.t, 3);
    camera.position.lerpVectors(tween.from, tween.to, k); controls.target.lerpVectors(tween.ft, tween.tt, k); if (tween.t >= 1) tween = null; }
  let tilt = 0;
  if (demo) { const sp = Math.sin(tAcc * 0.9); rollAng += sp * dt * 2.2; tilt = -0.22 * Math.cos(tAcc * 0.9) + 0.03 * Math.sin(tAcc * 7) * Math.exp(-((tAcc * 0.9) % Math.PI)); }
  const ease = explodeT * explodeT * (3 - 2 * explodeT);
  for (const [id, p] of Object.entries(parts)) {
    const e = p.meta.explode; const off = [e[0] * ease, e[1] * ease, e[2] * ease];
    if (p.meta.layer === 'dock') { p.grp.position.set(...off); continue; }
    if (/^(ring|tread)/.test(id)) placeAboutAxle(p.grp, rollAng, off);
    else placeAboutAxle(p.grp, tilt, off);
  }
  if (parts.display && parts.display.tex) {
    if (tAcc > nextBlink) { const b = (tAcc - nextBlink) / 0.18; parts.display.tex.draw(b < 1 ? Math.sin(b * Math.PI) : 0, demo ? Math.sin(tAcc * 0.9) : 0); if (b >= 1) nextBlink = tAcc + 2 + Math.random() * 3; }
    else if (demo) parts.display.tex.draw(0, Math.sin(tAcc * 0.9));
  }
  controls.update(); renderer.render(scene, camera);
  // labels
  for (const [id, d] of Object.entries(labelDivs)) {
    const p = parts[id]; const inside = !EXTERNAL.has(id);
    const vis = showLabels && p.grp.visible && !(xray && isSkin(id) && id !== 'ring_L') && (!inside || xray || explodeT > 0.15) && !(id === 'camera' && (xray || explodeT > 0.15) && false);
    if (!vis) { d.style.display = 'none'; continue; }
    const c = p.meta.center; const s = p.meta.size;
    v3.set(c[0], c[1], c[2] + (/^(ring|tread)/.test(id) ? s[2] / 2 - 4 : 0)); p.grp.localToWorld(v3);
    v3.project(camera);
    if (v3.z > 1) { d.style.display = 'none'; continue; }
    d.style.display = 'block'; d.style.left = ((v3.x + 1) / 2 * innerWidth) + 'px'; d.style.top = ((1 - v3.y) / 2 * innerHeight) + 'px';
  }
}
animate();
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });
