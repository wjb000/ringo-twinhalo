# Ringo: a pet robot that is its own wheels

**Live 3D viewer:** https://wjb000.github.io/ringo-twinhalo/ (it has layer toggles, labels, X-ray, an exploded view, standard views, click-for-info and a roll demo)

Ringo is a home pet robot whose body is two big frosted halo rings. The rings roll on the floor, and a sealed pod with the round-screen face hangs inside them like a pendulum. The battery and a steel keel sit low in the pod, so it always comes back upright and never needs to balance. Each ring has an internal gear molded into it, and one N20 gearmotor per ring drives it through a pinion. There's no axle, hub, bearing or balance loop.

| | |
|---|---|
| Size | 160 mm tall, ~96 mm wide (ring OD 160 mm) |
| Mass (CAD estimate) | ~545 g, of which the swinging pod is ~316 g; pod COM is 19 mm below the axle, so it self-rights |
| Brain | ESP32-S3 (8 MB PSRAM): wake word, person/pet detection and behaviours on-device; Wi-Fi app |
| Senses | 2 MP camera, front + cliff ToF, 2 mics, IMU (pats, pick-up, bumps) |
| Express | 1.28" round IPS eyes, whole-body halo glow (4 LEDs into the frosted rings), 28 mm speaker, pendulum body language |
| Power | 1x 18650 3000 mAh; drives onto the dock, where 4 belly pads meet 4 pogo pins (5 V + USB data) |
| Cost | prototype **$150.73** (retail parts, qty 1) · volume **$36.47**/unit at 10k (factory cost) · target retail **$129**. See [BOM.md](BOM.md) |

## Why it could take over
1. **A silhouette nobody has seen.** A glowing face floating inside two hoops reads instantly in a 2-second video, which is how consumer robots spread.
2. **It can't fall over.** The pendulum rights it, the rings are the bumper, and the 160 mm wheels roll over rug edges, cords and door sills.
3. **Physics gives it personality.** It nods when it starts, leans into turns and wobbles when it stops, with no actuators spent on emotion.
4. **It has the cheapest drivetrain a mobile robot can have.** That's 2 motors and 1 ring tool used twice, so $129 retail is realistic.
5. **It's useful every day.** It's a roaming home and pet camera, rolls over to give you timers and reminders, works as a night-light, and comes to find you when the doorbell or a smoke alarm sounds.

## Repo
```
site/            GitHub Pages viewer (three.js), deployed by .github/workflows/pages.yml
cad/ringo.py     parametric CadQuery model (all dimensions at the top)
cad/export.py    builds everything -> STEP, ASCII STL, viewer model, mass + interference reports
cad/bom.py       BOM source -> BOM.md + site/assets/bom.json
cad/step/        STEP per molded part (ring, tread, pinion and idler are drawn once and used 2-4x)
cad/stl/         ASCII STL for 3D-printed prototypes
cad/reports/     mass.json (pendulum check), interference.json
```
Rebuild with `pip install cadquery numpy`, then `python cad/export.py` and `python cad/bom.py`. The full colored assembly STEP is generated locally as `cad/step/ringo_assembly.step` (~11 MB). It isn't committed.

## Production notes
**Part count:** 6 molding tools for the robot (pod front, pod rear, ring + tread 2-shot, idler, pinion, lens) and 1 for the dock. That makes 11 molded pieces, plus 1 main PCB, 4 screws and 4 pins.

**DFM**
- The pod is split at x = 0. Both halves pull straight along x with no side actions. Walls are 2.0 mm, and the screw bosses are molded in. Hub-cap décor grooves need 1° draft.
- The ring is a cored U-channel with 2.5 mm walls, open on the inboard face so the core pulls straight. It has 24 ribs and a module-1, 124-tooth internal gear molded in. The tread is TPU 85A, 2-shot overmolded into a locking groove. Left and right are the same part, flipped.
- POM idlers and pinions come from one family tool. The lens is PMMA with a hard coat.
- The pinion runs on a spring-loaded motor saddle (not yet modeled). That makes ring assembly possible, sets mesh preload and lets the gear slip instead of breaking on a drop.

**Assembly (about 8 min target)**
1. Rear shell: snap in the main board, battery and keel, seat the motors on their saddles, and press on the pinions.
2. Front shell: fit the display and lens, then plug the display and camera flex cables into the board.
3. Close with 4 M2.5x8 self-tapping screws.
4. Push each motor in, slide a ring over its hub, release, then press in 2 idler pins per side.
5. Park it on the dock. The end-of-line test runs over the pogo USB.

**Prototype:** print the shells in PETG, the rings in translucent PETG (0.4 mm nozzle, 0.12 mm layers for the gear) and the treads as TPU bands. Use the parts from BOM.md and the XIAO ESP32-S3 Sense in place of the custom board.

## Honest status
This is a design model only. Nothing has been printed, built or driven. The bought parts are modeled as datasheet-size envelopes, not vendor CAD. The gear teeth are simplified trapezoids, not involutes, so they show about 6 mm³ of mesh overlap in the interference report. Wiring, the spring motor saddle and the snap features aren't modeled. Runtime, sill climbing and mass are estimates. Volume prices mix quoted listings with engineering estimates; each line in BOM.md says which.
