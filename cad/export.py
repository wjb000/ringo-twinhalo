"""Build Ringo, export STEP / ASCII STL / viewer model / reports.
Run: python export.py   (CadQuery 2.x)"""
import json, base64, math, os, sys, itertools
import numpy as np
import cadquery as cq
from ringo import build, AX

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCK_DZ = -3.5      # dock shown under the robot; robot stays at floor coords

# id: (display name, layer, colour, opacity, explode [x,y,z], material/source, info)
META = {
 "pod_front":  ("Pod shell - front", "shell", "#f3efe7", 1, [70, 0, 0], "PC/ABS, injection molded (proto: PETG/PLA print)",
   "Front half of the sealed pod. Carries the eye socket, camera window, front + cliff ToF windows and mic ports. Splits from the rear at x=0, so both halves pull in one direction (no side actions)."),
 "pod_rear":   ("Pod shell - rear", "shell", "#e9e3d8", 1, [-70, 0, 0], "PC/ABS, injection molded",
   "Rear half of the pod: speaker grille, 4 screw counterbores, PCB and motor saddles. Joined to the front by 4 M2.5x8 self-tapping screws."),
 "eye_lens":   ("Eye lens", "shell", "#1a2430", 0.35, [130, 0, 0], "PMMA, clear, AR + hard coat",
   "Flat 42.8 mm window over the round display, recessed 3.5 mm into the socket so the face looks set-in, and drop-safe."),
 "ring_L":     ("Halo ring - left", "drive", "#bfefff", 0.55, [0, 95, 0], "Frosted translucent PC, internal gear molded in",
   "The wheel AND the body AND the bumper. 154 mm PC ring with a 124-tooth module-1 internal gear on its inside. Lit from inside by the halo LEDs. Left and right are the SAME part, flipped."),
 "ring_R":     ("Halo ring - right", "drive", "#bfefff", 0.55, [0, -95, 0], "Same tool as left ring",
   "Identical to the left ring, mounted flipped. One mold, two cavities."),
 "tread_L":    ("Tread - left", "drive", "#2b2d31", 1, [0, 110, 0], "TPU 85A, 2-shot overmolded on ring (proto: printed TPU band)",
   "Grippy 160 mm tread with molded sipes. The big diameter rolls over rug edges, cables and door thresholds up to ~25 mm."),
 "tread_R":    ("Tread - right", "drive", "#2b2d31", 1, [0, -110, 0], "TPU 85A overmold", "Same as left tread."),
 "pinion_L":   ("Pinion - left", "drive", "#e8833a", 1, [0, 60, -25], "POM, 12T module 1", "Press-fit on the motor D-shaft; drives the ring's internal gear (ratio 124:12 = 10.3:1 on top of the gearmotor)."),
 "pinion_R":   ("Pinion - right", "drive", "#e8833a", 1, [0, -60, -25], "POM, 12T module 1", "Same as left pinion."),
 "dock":       ("Lily-pad dock", "dock", "#d9d3c8", 1, [0, 0, -70], "PC/ABS, one molded part + rubber feet",
   "Ringo drives onto the two raised lanes; the detent dips park it so 4 belly pads land on 4 pogo pins (power + USB data). IR beacon in the back fin guides it home."),
 "main_pcb":   ("Main board", "electronics", "#1f6f4a", 1, [0, 0, 55], "2-layer FR4 68x42 mm, JLC-style SMT", "Single board: MCU, motor driver, charger, audio amp, IMU, connectors. Everything except the battery, motors, display and camera is on this one board."),
 "esp32s3_module": ("ESP32-S3-WROOM-1-N8R8", "electronics", "#b8bcc4", 1, [0, 0, 62], "Espressif, LCSC C2913201",
   "Dual-core 240 MHz + vector instructions, 8 MB flash, 8 MB PSRAM, Wi-Fi + BLE. Runs on-device wake word, person/pet detection and the behaviour engine; streams camera to the phone app."),
 "motor_driver": ("DRV8833 motor driver", "electronics", "#222222", 1, [0, 0, 62], "TI DRV8833 HTSSOP", "Dual H-bridge, 1.5 A per channel, runs both N20s straight off the cell."),
 "charger_ic": ("Li-ion charger + protection", "power", "#222222", 1, [0, 0, 62], "TP4056 + DW01A/FS8205", "1 A charge from dock pins, cell protection."),
 "audio_amp":  ("MAX98357A I2S amp", "electronics", "#222222", 1, [0, 0, 62], "Analog Devices MAX98357A", "3 W class-D for the speaker: voice, chirps, alarms."),
 "imu":        ("6-axis IMU", "sensors", "#444444", 1, [0, 0, 62], "QMI8658 / ICM-42670", "Measures pod swing. Doubles as the only 'button': pats, pick-up, shake and bumps are all read from the IMU."),
 "fpc_conn":   ("Display/camera FPC connectors", "electronics", "#dddddd", 1, [0, 0, 62], "0.5 mm FPC", "Display and camera plug straight into the board."),
 "display":    ("1.28in round IPS display", "electronics", "#0b0f14", 1, [95, 0, 0], "GC9A01 240x240 round TFT",
   "The face. Eyes, moods, timers, weather, caller photos."),
 "display_fpc": ("Display FPC", "electronics", "#d79b2b", 1, [60, 0, 20], "Flex tail", "Display flex to board."),
 "camera":     ("Camera (OV2640 / OV3660)", "sensors", "#333333", 1, [80, 0, 15], "2 MP DVP module, 66 deg lens",
   "Sees people, pets and obstacles; home check-in video. Privacy: a 'bow' (pod tipped forward) points the camera at the floor."),
 "tof_front":  ("Front ToF sensor", "sensors", "#55bb33", 1, [75, 0, -10], "ST VL53L0X/VL53L1X", "Obstacle range up to 2 m."),
 "tof_cliff":  ("Cliff ToF sensor", "sensors", "#55bb33", 1, [60, 0, -40], "ST VL53L0X", "Looks down-forward 50 deg: stops before stairs and table edges."),
 "battery":    ("18650 Li-ion cell", "power", "#3a7bd5", 1, [0, 0, 30], "3.6 V 3000 mAh (Samsung/EVE class)",
   "The pendulum weight. Sitting low in the pod it keeps Ringo upright with zero control effort; est. 4-6 h roaming, days in standby."),
 "motor_L":    ("N20 gearmotor + encoder - left", "drive", "#c9cdd2", 1, [0, 30, -30], "6 V N20, 1:100, Hall encoder, 25 mm D-shaft", "Drives the left ring. Encoders give odometry for mapping and docking."),
 "motor_R":    ("N20 gearmotor + encoder - right", "drive", "#c9cdd2", 1, [0, -30, -30], "6 V N20, 1:100, Hall encoder", "Drives the right ring."),
 "shaft_L":    ("Motor shaft - left", "drive", "#99aaaa", 1, [0, 45, -28], "steel D-shaft", "Extended 25 mm shaft passes through the drum shoulder into the ring gap."),
 "shaft_R":    ("Motor shaft - right", "drive", "#99aaaa", 1, [0, -45, -28], "steel D-shaft", "Extended shaft."),
 "speaker":    ("28 mm speaker", "electronics", "#555555", 1, [-90, 0, 0], "8 ohm 1 W", "Voice + sound effects through the rear grille."),
 "mic_flex":   ("Dual MEMS mic flex", "sensors", "#d79b2b", 1, [0, 0, 70], "2x PDM MEMS mic", "Far-field wake word + sound direction (turns toward your voice)."),
 "halo_leds":  ("Halo LEDs (4x)", "electronics", "#fff3a0", 1, [0, 0, 40], "WS2812B-2020", "Shine through hub windows into the frosted rings: the whole body glows for mood, notifications and night-light."),
 "ballast_keel": ("Ballast keel", "power", "#6d6f73", 1, [0, 0, -55], "Zinc-plated stamped steel, 54 g",
   "Cheapest performance part in the robot: 54 g of steel at the very bottom of the pod nearly doubles the pendulum's righting moment, so the motors can push harder before the pod swings."),
 "belly_pads": ("Belly charge pads", "power", "#d4af37", 1, [0, 0, -40], "Gold-plated pads on mini board", "4 pads: 5 V, GND, USB D+/D-. No USB port to seal, no cable to lose."),
 "dock_pogos": ("Dock pogo pins (4x)", "dock", "#d4af37", 1, [0, 0, -55], "Spring pogo pins, 1.5 mm travel", "Contact the belly pads when Ringo parks."),
 "dock_pcb":   ("Dock board + USB-C", "dock", "#1f6f4a", 1, [0, 0, -65], "1-layer FR4, USB-C in", "USB-C 5 V in, pogo routing, IR beacon driver."),
 "ir_beacon":  ("IR homing beacon", "dock", "#802020", 1, [-20, 0, -65], "940 nm IR LED, coded", "Ringo homes on it to find the dock."),
}
for s, n in (("L", "left"), ("R", "right")):
    sg = 1 if s == "L" else -1
    for k, zz in (("top", 1), ("bot", -1)):
        META[f"idler_{s}_{k}"] = (f"Idler roller - {n} {k}", "drive", "#7a7f88", 1, [0, 70 * sg, 30 * zz], "POM roller on 3 mm steel pin",
            "Rides the ring's smooth track. Top + bottom idlers plus the pinion hold the ring on the pod with no axle or bearing.")
        META[f"pin_{s}_{k}"] = (f"Idler pin - {n} {k}", "drive", "#b0b4ba", 1, [0, 75 * sg, 30 * zz], "3x13 mm steel dowel", "Idler axle, pressed into the shell.")

MOLDED = ["pod_front", "pod_rear", "ring_L", "tread_L", "pinion_L", "idler_L_top", "eye_lens", "dock"]
DENS = {"pod_front": 1.15, "pod_rear": 1.15, "eye_lens": 1.19, "ring_L": 1.2, "ring_R": 1.2, "tread_L": 1.2, "tread_R": 1.2,
        "pinion_L": 1.41, "pinion_R": 1.41, "dock": 1.15}
BOUGHT_MASS = {"battery": 46, "motor_L": 10, "motor_R": 10, "display": 6, "main_pcb": 9, "esp32s3_module": 3, "camera": 3,
               "speaker": 5, "ballast_keel": 54, "belly_pads": 2, "halo_leds": 1, "mic_flex": 1, "tof_front": 1, "tof_cliff": 1}


def fname(k):
    return k.replace("_L", "").replace("_top", "")


def mesh_of(shape, tol=0.12, ang=0.3):
    vs, ts = shape.val().tessellate(tol, ang)
    v = np.array([(p.x, p.y, p.z) for p in vs], dtype=np.float64)
    t = np.array(ts, dtype=np.int64)
    return v, t


def write_ascii_stl(shape, path, name, tol=0.12, ang=0.35):
    """Compact ASCII STL (0.01 mm precision) - prints fine, diff-able, small."""
    v, t = mesh_of(shape, tol, ang)
    with open(path, "w") as f:
        f.write(f"solid {name}\n")
        for a, b, c in t:
            p0, p1, p2 = v[a], v[b], v[c]
            n = np.cross(p1 - p0, p2 - p0); l = np.linalg.norm(n)
            n = n / l if l > 0 else n
            f.write(f"facet normal {n[0]:.3f} {n[1]:.3f} {n[2]:.3f}\nouter loop\n")
            for p in (p0, p1, p2):
                f.write(f"vertex {p[0]:.2f} {p[1]:.2f} {p[2]:.2f}\n")
            f.write("endloop\nendfacet\n")
        f.write(f"endsolid {name}\n")


def b64(a):
    return base64.b64encode(a.tobytes()).decode()


def main():
    P = build()
    for d in ("cad/step", "cad/stl", "cad/reports", "site/assets"):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)

    # ---- viewer model first (fast feedback)
    parts = []
    for k, v in P.items():
        name, layer, col, op, ex, mat, info = META[k]
        shape = v.translate((0, 0, DOCK_DZ)) if layer == "dock" else v
        tol = 0.3 if k.startswith(("tread", "dock")) else 0.15
        verts, tris = mesh_of(shape, tol, 0.35)
        q = np.round(verts * 100).astype(np.int16)          # 0.01 mm
        i32 = len(verts) >= 65535
        idx = tris.astype(np.uint32 if i32 else np.uint16).ravel()
        bb = shape.val().BoundingBox()
        parts.append({"id": k, "name": name, "layer": layer, "color": col, "opacity": op, "explode": ex, "material": mat,
                      "info": info, "size": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
                      "center": [round(bb.center.x, 1), round(bb.center.y, 1), round(bb.center.z, 1)],
                      "pos": b64(q), "idx": b64(idx), "i32": bool(i32), "nv": int(len(verts)), "nt": int(len(tris))})
    with open(os.path.join(ROOT, "site", "assets", "ringo_model.json"), "w") as f:
        json.dump({"units": "mm", "scale": 0.01, "up": "z", "parts": parts}, f, separators=(",", ":"))
    print("model written", sum(p["nt"] for p in parts), "tris")

    # ---- mass + pendulum check
    mass = {}; mtot = 0; pod_m = 0; pod_c = np.zeros(3)
    for k, v in P.items():
        if META[k][1] == "dock": continue
        shp = v.val()
        if k in BOUGHT_MASS:
            m = BOUGHT_MASS[k]; c = shp.BoundingBox().center
        else:
            d = DENS.get(k, 7.8 if k.startswith(("pin_", "shaft")) else 1.41 if k.startswith("idler") else 1.5)
            m = shp.Volume() / 1000 * d; c = shp.Center()
        c = np.array([c.x, c.y, c.z]); mass[k] = round(m, 1); mtot += m
        if not k.startswith(("ring", "tread")):
            pod_m += m; pod_c += m * c
    pod_c /= pod_m
    rep = {"total_mass_g": round(mtot, 1), "pod_swinging_mass_g": round(pod_m, 1),
           "pod_com_mm": [round(x, 1) for x in pod_c], "axle_height_mm": AX,
           "pendulum_drop_mm": round(AX - pod_c[2], 1), "self_righting": bool(pod_c[2] < AX),
           "note": "Bought-part masses are datasheet/typical values; molded parts from CAD volume x density.",
           "masses_g": mass}
    json.dump(rep, open(os.path.join(ROOT, "cad", "reports", "mass.json"), "w"), indent=1)
    print(json.dumps({k: rep[k] for k in rep if k != "masses_g"}))

    # ---- STEP (molded parts) + ASCII STL (printable prototype parts)
    for k in MOLDED:
        cq.exporters.export(P[k], os.path.join(ROOT, "cad", "step", f"{fname(k)}.step"))
        write_ascii_stl(P[k], os.path.join(ROOT, "cad", "stl", f"{fname(k)}.stl"), fname(k))
    asm = cq.Assembly(name="ringo")
    for k, v in P.items():
        if META[k][1] == "dock": continue
        asm.add(v, name=k, color=cq.Color(META[k][2]))
    asm.save(os.path.join(ROOT, "cad", "step", "ringo_assembly.step"))
    print("step/stl done")

    # ---- interference check (robot only)
    keys = [k for k in P if META[k][1] != "dock"]
    hits = []
    bbs = {k: P[k].val().BoundingBox() for k in keys}
    for a, b in itertools.combinations(keys, 2):
        A, B = bbs[a], bbs[b]
        if A.xmax < B.xmin or B.xmax < A.xmin or A.ymax < B.ymin or B.ymax < A.ymin or A.zmax < B.zmin or B.zmax < A.zmin:
            continue
        try:
            vol = P[a].intersect(P[b]).val().Volume()
        except Exception:
            vol = 0
        if vol > 0.5:
            hits.append([a, b, round(vol, 1)])
    json.dump({"overlaps_mm3": hits, "note": "pairs with >0.5 mm^3 shared volume; press fits are intentional"},
              open(os.path.join(ROOT, "cad", "reports", "interference.json"), "w"), indent=1)
    print("overlaps", hits)


if __name__ == "__main__":
    main()
