"""Ringo - parametric CadQuery model.

Concept: the body IS the wheels. Two big frosted 'halo' rings roll on the floor;
a sealed pod hangs inside them like a pendulum (battery low = always upright).
Each ring has an internal gear molded in; one N20 gearmotor per ring drives it
with a pinion. No axle, no hub, no balancing control loop.

Frame: x forward, y left, z up, mm. Axle (ring centre) at z = AX.
"""
import math
import cadquery as cq

# ---------------- parameters ----------------
AX = 80.0            # ring centre height = tread outer radius
R_TREAD = 80.0       # tread outer radius
R_RIM = 77.0         # PC ring outer radius (tread sits on this)
R_ROOT = 63.25       # internal gear root / idler track radius
R_TIP = 61.0         # internal gear tip radius
N_RING = 124         # internal gear teeth, module 1
R_LIP = 57.0         # retaining lip inner radius
Y_IN, Y_GEAR, Y_LIPIN, Y_OUT = 26.0, 38.0, 45.5, 48.0   # ring axial stations (|y|)
R_DRUM, Y_DRUM = 66.0, 25.0   # central face drum radius / half width
R_HUB, Y_HUB = 54.0, 46.0     # side hub radius / half width
WALL = 2.0
N_PIN = 12                    # pinion teeth, module 1 -> pitch r 6
R_PIN_C = 62.0 - 6.0          # pinion centre radius from axle
PIN_ANG = {+1: 255.0, -1: 285.0}  # pinion angle (deg, in xz plane) per side
IDLER_R = 7.0
IDLER_C = R_ROOT - IDLER_R
EYE_Z = AX
CAM_Z = 112.0


def polar(r, ang_deg, z0=AX):
    a = math.radians(ang_deg)
    return (r * math.cos(a), z0 + r * math.sin(a))


def rounded_profile(pts, radii, wp=None):
    """Closed polyline (x,y) on XY workplane with corner fillets (true arcs)."""
    n = len(pts)
    segs = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        r = radii[i]
        if r <= 0:
            segs.append(("pt", p1)); continue
        v1 = (p0[0] - p1[0], p0[1] - p1[1]); v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1 = math.hypot(*v1); l2 = math.hypot(*v2)
        u1 = (v1[0] / l1, v1[1] / l1); u2 = (v2[0] / l2, v2[1] / l2)
        cosang = max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1]))
        ang = math.acos(cosang)
        t = r / math.tan(ang / 2)
        t = min(t, 0.45 * l1, 0.45 * l2)
        a = (p1[0] + u1[0] * t, p1[1] + u1[1] * t)
        b = (p1[0] + u2[0] * t, p1[1] + u2[1] * t)
        bis = (u1[0] + u2[0], u1[1] + u2[1]); lb = math.hypot(*bis)
        bis = (bis[0] / lb, bis[1] / lb)
        rr = t * math.tan(ang / 2)
        d = rr / math.sin(ang / 2)
        c = (p1[0] + bis[0] * d, p1[1] + bis[1] * d)
        m = (c[0] - bis[0] * rr, c[1] - bis[1] * rr)
        segs.append(("arc", a, m, b))
    w = wp or cq.Workplane("XY")
    first = segs[0]
    start = first[1] if first[0] == "pt" else first[1]
    w = w.moveTo(*start)
    cur = start
    for s in segs[1:] + [segs[0]]:
        if s[0] == "pt":
            if s[1] != cur: w = w.lineTo(*s[1]); cur = s[1]
        else:
            if s[1] != cur: w = w.lineTo(*s[1])
            w = w.threePointArc(s[2], s[3]); cur = s[3]
    return w.close()


def revolve_y(pts, radii):
    """Revolve an (r, y) profile 360 deg about the global Y axis, then lift to AX."""
    s = rounded_profile(pts, radii).revolve(360, (0, 0, 0), (0, 1, 0))
    return s.translate((0, 0, AX))


def cyl_x(r, x0, x1, y, z):
    return cq.Workplane("YZ", origin=(x0, 0, 0)).center(y, z).circle(r).extrude(x1 - x0)


def cyl_y(r, y0, y1, x, z):
    s = cq.Workplane("XY").circle(r).extrude(y1 - y0)       # along +z
    s = s.rotate((0, 0, 0), (1, 0, 0), -90)                   # +z -> +y
    return s.translate((x, y0, z))


def cyl_z(r, z0, z1, x, y):
    return cq.Workplane("XY", origin=(0, 0, z0)).center(x, y).circle(r).extrude(z1 - z0)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def gear_disc(n, r_root, r_tip, internal):
    """2D zigzag gear outline as a disc solid (extruded 1 along +z)."""
    p = 2 * math.pi / n
    pts = []
    for k in range(n):
        th = k * p
        if internal:   # teeth point inward: tip at small radius
            seq = [(-0.30, r_root), (-0.16, r_tip), (0.16, r_tip), (0.30, r_root)]
        else:
            seq = [(-0.30, r_root), (-0.15, r_tip), (0.15, r_tip), (0.30, r_root)]
        for f, r in seq:
            a = th + f * p
            pts.append((r * math.cos(a), r * math.sin(a)))
    return cq.Workplane("XY").polyline(pts).close().extrude(1.0)


def along_y(solid_z1, y0, y1, x, z):
    s = solid_z1.val().scale(1.0) if False else solid_z1
    s = cq.Workplane("XY").add(s.val().transformGeometry(cq.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, y1 - y0, 0]])))
    s = s.rotate((0, 0, 0), (1, 0, 0), -90)
    return s.translate((x, y0, z))


# ---------------- pod (front + rear shells) ----------------
def pod_solids():
    outer_pts = [(0, -Y_HUB), (R_HUB, -Y_HUB), (R_HUB, -Y_DRUM), (R_DRUM, -Y_DRUM),
                 (R_DRUM, Y_DRUM), (R_HUB, Y_DRUM), (R_HUB, Y_HUB), (0, Y_HUB)]
    outer_r = [0, 5, 2, 5, 5, 2, 5, 0]
    w = WALL
    inner_pts = [(0, -Y_HUB + w), (R_HUB - w, -Y_HUB + w), (R_HUB - w, -Y_DRUM + w), (R_DRUM - w, -Y_DRUM + w),
                 (R_DRUM - w, Y_DRUM - w), (R_HUB - w, Y_DRUM - w), (R_HUB - w, Y_HUB - w), (0, Y_HUB - w)]
    inner_r = [0, 3, 4, 3, 3, 4, 3, 0]
    outer = revolve_y(outer_pts, outer_r)
    inner = revolve_y(inner_pts, inner_r)
    shell = outer.cut(inner)

    # eye socket boss + hole, lens seat
    boss = cyl_x(25.0, 50, 70, 0, EYE_Z).cut(cyl_x(21.6, 49, 71, 0, EYE_Z)).intersect(outer)
    shell = shell.union(boss).cut(cyl_x(21.6, 50, 72, 0, EYE_Z))
    # camera window, front ToF window, cliff ToF window
    shell = shell.cut(cyl_x(3.4, 45, 72, 0, CAM_Z))
    shell = shell.cut(cyl_x(1.3, 50, 72, 2.6, 50)).cut(cyl_x(1.3, 50, 72, -2.6, 50))
    cx, cz = polar(R_DRUM - 1, -50)
    cliff = cq.Workplane("XY").circle(2.0).extrude(12).rotate((0, 0, 0), (0, 1, 0), 90 + 50).translate((cx, 0, cz))
    shell = shell.cut(cliff)
    # mic ports on top
    for y in (-12, 12):
        shell = shell.cut(cyl_z(0.8, 130, 150, 0.5, y))
    # speaker grille (rear)
    for i in range(-2, 3):
        for j in range(-2, 3):
            if i * i + j * j <= 5:
                shell = shell.cut(cyl_x(1.0, -72, -55, i * 4.2, 80 + j * 4.2))
    # belly charge-pad holes
    for x in (-5, 5):
        for y in (-6, 6):
            shell = shell.cut(cyl_z(2.2, 10, 18, x, y))
    # screw bosses (x axis), split at x=0
    for y in (-15, 15):
        for z in (38, 124):
            b = cyl_x(3.6, -70, 70, y, z).intersect(inner)
            shell = shell.union(b)
            shell = shell.cut(cyl_x(1.1, -70, 70, y, z))           # pilot
            shell = shell.cut(cyl_x(1.45, -70, 0, y, z))           # clearance in rear
            shell = shell.cut(cyl_x(2.6, -80, -(math.sqrt(R_DRUM**2 - (z - AX)**2) - 3.0), y, z))   # counterbore
    # motor shaft holes through shoulders, hub pockets for idlers + pinions, halo LED windows
    for s in (+1, -1):
        px, pz = polar(R_PIN_C, PIN_ANG[s])
        ylo, yhi = (Y_DRUM - 3, Y_DRUM + 3)
        shell = shell.cut(cyl_y(2.2, ylo, yhi, px, pz).mirror("XZ") if s < 0 else cyl_y(2.2, ylo, yhi, px, pz))
        for (x, z, r, y0, y1) in [(0, AX - IDLER_C, 8.2, Y_IN, Y_GEAR + 0.5), (0, AX + IDLER_C, 8.2, Y_IN, Y_GEAR + 0.5),
                                  (px, pz, 8.6, Y_DRUM + 4.5, Y_HUB + 1)]:
            c = cyl_y(r, y0, y1, x, z)
            shell = shell.cut(c.mirror("XZ") if s < 0 else c)
        for ang in (45, 135):
            lx, lz = polar(R_HUB - 1, ang)
            c = cq.Workplane("XY").circle(3.0).extrude(8).rotate((0, 0, 0), (0, 1, 0), -ang + 90).translate((lx, 34 * s, lz))
            c = cq.Workplane("XY").box(7, 7, 8).rotate((0, 0, 0), (0, 1, 0), 90 - ang).translate((lx, 34 * s, lz))
            shell = shell.cut(c)
    for s in (+1, -1):
        g = cyl_y(36.0, Y_HUB - 0.8, Y_HUB + 1, 0, AX).cut(cyl_y(33.0, Y_HUB - 1, Y_HUB + 2, 0, AX))
        shell = shell.cut(g if s > 0 else g.mirror("XZ"))
    front = shell.intersect(box(0, 100, -100, 100, -10, 200))
    rear = shell.intersect(box(-100, 0, -100, 100, -10, 200))
    return front, rear, outer


# ---------------- halo ring ----------------
def ring_solid(side=+1):
    """Cored U-channel ring (uniform ~2.5 mm walls), open on the inboard face so the
    core pulls straight out; 24 radial ribs; module-1 internal gear on the track."""
    pts = [(R_ROOT, Y_IN), (R_RIM, Y_IN), (R_RIM, Y_OUT), (R_LIP, Y_OUT), (R_LIP, Y_LIPIN), (R_ROOT, Y_LIPIN)]
    rad = [1.0, 1.5, 2.0, 1.0, 0.5, 0]
    body = revolve_y(pts, rad)
    cavity = revolve_y([(R_ROOT + 2.75, Y_IN - 2), (R_RIM - 2.5, Y_IN - 2), (R_RIM - 2.5, Y_LIPIN), (R_ROOT + 2.75, Y_LIPIN)], [0, 0, 1.0, 1.0])
    body = body.cut(cavity)
    for k in range(24):
        a = 360.0 * k / 24 + 7.5
        rib = box(R_ROOT + 2.0, R_RIM - 2.0, Y_IN + 2.0, Y_LIPIN + 0.5, -1.0, 1.0).rotate((0, 0, 0), (0, 1, 0), a).translate((0, 0, AX))
        body = body.union(rib)
    yc = (Y_IN + Y_OUT) / 2
    groove = revolve_y([(R_RIM - 1.0, yc - 6.5), (R_RIM + 1, yc - 6.5), (R_RIM + 1, yc + 6.5), (R_RIM - 1.0, yc + 6.5)], [0, 0, 0, 0])
    body = body.cut(groove)
    teeth = cyl_y(R_ROOT + 0.4, Y_GEAR, Y_LIPIN, 0, AX).cut(along_y(gear_disc(N_RING, R_ROOT + 0.15, R_TIP, True), Y_GEAR - 0.1, Y_LIPIN + 0.1, 0, AX))
    body = body.union(teeth)
    return body if side > 0 else body.mirror("XZ")


def tread_solid(side=+1):
    """14 mm TPU tread centred on the rim so the frosted PC shows on both sides."""
    yc = (Y_IN + Y_OUT) / 2
    pts = [(R_RIM - 1.0, yc - 6.5), (R_RIM, yc - 6.5), (R_RIM, yc - 7.0), (R_TREAD, yc - 7.0),
           (R_TREAD, yc + 7.0), (R_RIM, yc + 7.0), (R_RIM, yc + 6.5), (R_RIM - 1.0, yc + 6.5)]
    t = revolve_y(pts, [0, 0, 0, 1.5, 1.5, 0, 0, 0])
    n = 48
    for k in range(n):
        a = 360.0 * k / n
        sipe = box(-0.6, 0.6, yc - 5, yc + 5, R_TREAD - 0.8, R_TREAD + 1).rotate((0, 0, 0), (0, 1, 0), a).translate((0, 0, AX))
        t = t.cut(sipe)
    return t if side > 0 else t.mirror("XZ")


def pinion_solid(side=+1):
    g = along_y(gear_disc(N_PIN, 4.75, 7.0, False), Y_GEAR + 0.5, Y_LIPIN - 0.5, 0, 0)
    g = g.union(cyl_y(4.0, Y_DRUM + 6, Y_GEAR + 0.5, 0, 0)).cut(cyl_y(1.5, 20, 50, 0, 0))
    px, pz = polar(R_PIN_C, PIN_ANG[side])
    g = g.translate((px, 0, pz))
    return g if side > 0 else g.mirror("XZ")


def idler_solid(side, top):
    z = AX + IDLER_C if top else AX - IDLER_C
    y0, y1 = Y_IN + 1.0, Y_GEAR - 0.5
    r = cyl_y(IDLER_R, y0 + 1, y1 - 1, 0, z).union(cyl_y(IDLER_R + 1.2, y0, y0 + 1, 0, z)).union(cyl_y(IDLER_R + 1.2, y1 - 1, y1, 0, z))
    r = r.cut(cyl_y(1.6, y0 - 1, y1 + 1, 0, z))
    # the flanges straddle the ring track: trim flange overlap with ring by making them tiny
    r = cyl_y(IDLER_R, y0, y1, 0, z).cut(cyl_y(1.6, y0 - 1, y1 + 1, 0, z)).edges("%CIRCLE").chamfer(0.5)
    return r if side > 0 else r.mirror("XZ")


def idler_pin(side, top):
    z = AX + IDLER_C if top else AX - IDLER_C
    p = cyl_y(1.5, Y_IN - 0.5, Y_GEAR + 0.4, 0, z)
    return p if side > 0 else p.mirror("XZ")


def lens_solid():
    l = cyl_x(21.4, 60.0, 62.5, 0, EYE_Z).edges(">X").chamfer(0.6)
    return l


# ---------------- dock ----------------
def dock_solids():
    base = cq.Workplane("XY").rect(176, 128).extrude(2.5).edges("|Z").fillet(34).translate((-4, 0, 0))
    base = base.edges(">Z").fillet(1.2)
    lane_prof = [(-72, 0), (-72, 5.0), (48, 5.0), (74, 0)]
    lanes = None
    for s in (+1, -1):
        l = cq.Workplane("XZ").polyline(lane_prof).close().extrude(-27)   # along +y
        l = l.translate((0, 23.5 if s > 0 else -50.5, 0))
        lanes = l if lanes is None else lanes.union(l)
    dock = base.union(lanes)
    dip = cyl_y(80, -60, 60, 0, AX + 5 - 1.5)
    dock = dock.cut(dip.intersect(box(-40, 40, -60, 60, 2.5, 10)).cut(box(-40, 40, -22, 22, -1, 30)))
    island = cq.Workplane("XY").rect(28, 26).extrude(16.5 - 2.5).edges("|Z").fillet(6).edges(">Z").fillet(3).translate((0, 0, 2.5))
    dock = dock.union(island)
    fin = cq.Workplane("XY").rect(12, 70).extrude(30).edges("|Z").fillet(5).edges(">Z").fillet(5).translate((-84, 0, 0))
    dock = dock.union(fin)
    dock = dock.cut(box(-79, -77, -7, 7, 18, 25))         # IR beacon window
    dock = dock.cut(box(-92, -88, -4.5, 4.5, 4, 7.5))      # USB-C
    for x in (-5, 5):
        for y in (-6, 6):
            dock = dock.cut(cyl_z(1.6, 10, 20, x, y))
    return dock


# ---------------- electronics / bought parts (datasheet envelopes) ----------------
def electronics():
    E = {}
    # main board: ESP32-S3-WROOM-1-N8R8 on a 2-layer 68x42 board
    pcb_z = 63.2
    E["main_pcb"] = box(-34, 34, -21, 21, pcb_z, pcb_z + 1.6)
    E["esp32s3_module"] = box(2, 27.5, -9, 9, pcb_z + 1.6, pcb_z + 4.7)
    E["esp32s3_module"] = E["esp32s3_module"]
    E["motor_driver"] = box(-14, -9, -12, -6, pcb_z + 1.6, pcb_z + 2.8)          # DRV8833 HTSSOP16
    E["charger_ic"] = box(-26, -21, -12, -6, pcb_z + 1.6, pcb_z + 3.1)           # TP4056 ESOP8
    E["audio_amp"] = box(-26, -23, 6, 9, pcb_z + 1.6, pcb_z + 2.6)               # MAX98357A TQFN 3x3
    E["imu"] = box(-6, -3.5, -1.5, 1.5, pcb_z + 1.6, pcb_z + 2.6)                # QMI8658 / ICM-42670 2.5x3
    E["fpc_conn"] = box(28.5, 32.5, -8, 8, pcb_z + 1.6, pcb_z + 3.6)
    # display (GC9A01 1.28in round, panel 38.5 dia x 2.6 incl. backlight)
    E["display"] = cyl_x(19.25, 57.2, 59.8, 0, EYE_Z)
    E["display_fpc"] = box(40, 57.2, -6, 6, 61, 61.3)
    # camera OV2640 module with lens barrel (8.5 x 8.5 x 5 + 8 dia barrel)
    E["camera"] = box(46, 51, -4.25, 4.25, CAM_Z - 4.25, CAM_Z + 4.25).union(cyl_x(3.2, 51, 56.5, 0, CAM_Z))
    # ToF sensors (VL53L0X 4.4x2.4x1.0 on 10x8 flex stiffener)
    E["tof_front"] = box(53.0, 54.0, -5, 5, 46, 54).union(box(54.0, 55.0, -2.2, 2.2, 48.8, 51.2))
    cx, cz = polar(R_DRUM - 4.5, -50)
    E["tof_cliff"] = box(-0.5, 0.5, -5, 5, -4, 4).union(box(0.5, 1.5, -2.2, 2.2, -1.2, 1.2)).rotate((0, 0, 0), (0, 1, 0), 50).translate((cx, 0, cz))
    # 18650 Li-ion along x, low in the pod = pendulum mass
    E["battery"] = cyl_x(9.1, -32.5, 32.5, 0, 46)
    # N20 6V gearmotors with magnetic encoder, shaft out through shoulder
    for s in (+1, -1):
        px, pz = polar(R_PIN_C, PIN_ANG[s])
        y_face = Y_DRUM - WALL
        gb = box(px - 6, px + 6, y_face - 9, y_face, pz - 5, pz + 5)
        can = cyl_y(6, y_face - 24, y_face - 9, px, pz).intersect(box(px - 7, px + 7, y_face - 25, y_face - 8, pz - 5, pz + 5))
        enc = cyl_y(6.5, y_face - 25.2, y_face - 24, px, pz).union(cyl_y(5.0, y_face - 31, y_face - 25.2, px, pz))
        m = gb.union(can).union(enc)
        shaft = cyl_y(1.5, y_face, Y_LIPIN - 0.3, px, pz)
        if s < 0:
            m = m.mirror("XZ"); shaft = shaft.mirror("XZ")
        E["motor_" + ("L" if s > 0 else "R")] = m
        E["shaft_" + ("L" if s > 0 else "R")] = shaft
    # speaker 28 mm, rear-firing
    E["speaker"] = cyl_x(14, -61.5, -57, 0, 80).union(cyl_x(9, -57, -54.5, 0, 80))
    # top mic flex with 2 MEMS mics
    E["mic_flex"] = box(-4, 5, -16, 16, 141.0, 141.3).union(box(-1.5, 2.5, -13.5, -10.5, 141.3, 142.3)).union(box(-1.5, 2.5, 10.5, 13.5, 141.3, 142.3))
    # halo LEDs: 2x WS2812B-2020 per side on tiny boards behind hub windows
    leds = None
    for s in (+1, -1):
        for ang in (45, 135):
            lx, lz = polar(R_HUB - 4.2, ang)
            b = box(-2.5, 2.5, -3, 3, -0.8, 0.8).union(box(-1, 1, -1, 1, 0.8, 1.6)).rotate((0, 0, 0), (0, 1, 0), 90 - ang).translate((lx, 34 * s, lz))
            leds = b if leds is None else leds.union(b)
    E["halo_leds"] = leds
    # belly charge/USB pads board
    pads = box(-9, 9, -10, 10, 17.4, 18.4)
    for x in (-5, 5):
        for y in (-6, 6):
            pads = pads.union(cyl_z(2.0, 14.3, 17.4, x, y))
    E["belly_pads"] = pads
    # stamped steel ballast keel: lowers pod COM (self-righting + more drive authority)
    E["ballast_keel"] = box(-7, 7, -20, 20, 18.8, 30.5)
    # dock electronics
    pogo = None
    for x in (-5, 5):
        for y in (-6, 6):
            p = cyl_z(1.5, 14.0, 16.6, x, y).union(cyl_z(0.9, 16.6, 18.2, x, y))
            pogo = p if pogo is None else pogo.union(p)
    E["dock_pogos"] = pogo
    E["dock_pcb"] = box(-12, 12, -11, 11, 12.4, 14.0).union(box(-88, -80, -4, 4, 4.3, 7.2))
    E["ir_beacon"] = cyl_x(2.5, -82, -77.5, 0, 21.5)
    return E


def build():
    front, rear, outer = pod_solids()
    P = {
        "pod_front": front, "pod_rear": rear, "eye_lens": lens_solid(),
        "ring_L": ring_solid(+1), "ring_R": ring_solid(-1),
        "tread_L": tread_solid(+1), "tread_R": tread_solid(-1),
        "pinion_L": pinion_solid(+1), "pinion_R": pinion_solid(-1),
        "dock": dock_solids(),
    }
    for s, n in ((+1, "L"), (-1, "R")):
        for top in (True, False):
            k = ("top" if top else "bot")
            P[f"idler_{n}_{k}"] = idler_solid(s, top)
            P[f"pin_{n}_{k}"] = idler_pin(s, top)
    P.update(electronics())
    return P


if __name__ == "__main__":
    import time
    t = time.time()
    P = build()
    for k, v in P.items():
        bb = v.val().BoundingBox()
        print(f"{k:16s} vol={v.val().Volume():9.0f}  x[{bb.xmin:6.1f},{bb.xmax:6.1f}] y[{bb.ymin:6.1f},{bb.ymax:6.1f}] z[{bb.zmin:6.1f},{bb.zmax:6.1f}]")
    print("t", time.time() - t)
