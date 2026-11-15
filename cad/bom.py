"""Single source of truth for Ringo BOMs -> BOM.md + site/assets/bom.json. Prices checked 2026-11-14."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (item, qty, unit USD, source/link, note)
PROTO = [
 ("Seeed XIAO ESP32-S3 Sense (MCU + OV2640 camera + PDM mic + Li-ion charger)", 1, 19.99, "https://www.seeedstudio.com/XIAO-ESP32S3-Sense-p-5639.html", "list price"),
 ("Waveshare 1.28in round LCD module (GC9A01, 240x240)", 1, 14.99, "https://www.waveshare.com/product/displays/lcd-oled/1.28inch-lcd-module.htm", "list price"),
 ("Adafruit N20 DC motor w/ magnetic encoder, 6V 1:150 (#4640)", 2, 12.50, "https://www.adafruit.com/product/4640", "list price; print pinion with long hub for the short shaft"),
 ("Adafruit DRV8833 motor driver breakout (#3297)", 1, 5.95, "https://www.adafruit.com/product/3297", "list price"),
 ("Adafruit MAX98357A I2S 3W amp (#3006)", 1, 5.95, "https://www.adafruit.com/product/3006", "list price"),
 ("Adafruit mini metal speaker 8ohm 0.5W (#1890)", 1, 1.95, "https://www.adafruit.com/product/1890", "list price"),
 ("Adafruit 18650 Li-ion 2200 mAh (#1781)", 1, 9.95, "https://www.adafruit.com/product/1781", "list price"),
 ("Adafruit MPU-6050 6-DoF IMU (#3886)", 1, 12.95, "https://www.adafruit.com/product/3886", "list price"),
 ("Adafruit VL53L0X ToF sensor (#3317)", 2, 14.95, "https://www.adafruit.com/product/3317", "list price (front + cliff)"),
 ("Adafruit NeoPixel 5050 10-pack (#1655)", 1, 4.50, "https://www.adafruit.com/product/1655", "list price; 4 used"),
 ("Adafruit magnetic pogo connector, 4 contact (#5358)", 1, 6.50, "https://www.adafruit.com/product/5358", "list price; stands in for belly pads + dock pogos"),
 ("Filament: ~320 g PETG (translucent rings + shells) + ~90 g TPU 85A (treads)", 1, 9.10, "", "estimate at ~$20/kg PETG, ~$30/kg TPU"),
 ("Ballast: ~55 g steel washers / M10 nuts", 1, 1.00, "", "estimate"),
 ("Fasteners: 4x M2.5x8 self-tap, 4x 3x13 mm dowel pins, nickel strip, wire", 1, 3.00, "", "estimate"),
]
VOLUME = [
 ("ESP32-S3-WROOM-1-N8R8 module", 1, 3.48, "https://www.lcsc.com/product-image/C2913201.html", "LCSC 1,300+ price"),
 ("OV2640 2MP DVP camera module, 24-pin", 1, 4.35, "https://www.alibaba.co.uk/product-detail/Factory-Price-Hdr-Night-Vision-Raspberry_1601403116305.html", "Alibaba ~1k pcs"),
 ("1.28in round IPS TFT, GC9A01", 1, 2.06, "https://www.alibaba.com/product-detail/1-28-240X240-Round-TFT-LCD_1600308475631.html", "Alibaba >=10k pcs"),
 ("N20 6V gearmotor with Hall encoder (TT Motor GM12-N20VA-EN class)", 2, 3.50, "https://www.alibaba.com/product-detail/N20-N30-DC-MOTOR-high-torque_1601200428436.html", "Alibaba >=1k pcs; 25 mm D-shaft option"),
 ("18650 Li-ion cell 3000 mAh (EVE 30P class)", 1, 1.70, "https://www.alibaba.co.uk/product-detail/EVE-18650-30P-3000mAh-3-6V_1601583882182.html", "Alibaba 200-600+ pcs"),
 ("ST VL53L0X ToF sensor (front + cliff)", 2, 1.50, "https://www.eboxtao.com/VL53L0XV2-Time-of-Flight-Laser-Ranging-Sensor-Serial-PWM-Output.html", "estimate from $1.14-1.80 module listings"),
 ("DRV8833 dual H-bridge", 1, 0.45, "https://www.lcsc.com/search?q=DRV8833", "estimate"),
 ("Li-ion charger + protection (TP4056 + DW01A + FS8205A)", 1, 0.15, "https://www.lcsc.com/search?q=TP4056", "estimate"),
 ("MAX98357A class-D amp", 1, 0.90, "https://www.lcsc.com/search?q=MAX98357A", "estimate"),
 ("6-axis IMU (QMI8658)", 1, 0.60, "https://www.lcsc.com/search?q=QMI8658", "estimate"),
 ("PDM MEMS microphones", 2, 0.20, "https://www.lcsc.com/search?q=PDM%20MEMS%20microphone", "estimate"),
 ("WS2812B-2020 LEDs", 4, 0.04, "https://www.lcsc.com/search?q=WS2812B-2020", "estimate"),
 ("Passives, FPC connectors, crystal-free (module) misc", 1, 0.80, "", "estimate"),
 ("Main PCB 68x42 2-layer + SMT assembly", 1, 2.20, "", "estimate at 10k"),
 ("28 mm 8 ohm speaker", 1, 0.35, "", "estimate"),
 ("Belly pad board (gold pads)", 1, 0.15, "", "estimate"),
 ("Pod shells front + rear, PC/ABS (~130 g) molded", 1, 1.00, "", "estimate: resin ~$0.40 + press time"),
 ("Halo rings x2, PC + TPU 2-shot overmold", 1, 2.40, "", "estimate"),
 ("Idlers x4 + pinions x2, POM", 1, 0.25, "", "estimate"),
 ("Eye lens PMMA, hard-coated", 1, 0.20, "", "estimate"),
 ("Steel ballast keel (stamped, 54 g) + 4 pins + 4 screws", 1, 0.22, "", "estimate"),
 ("Dock: molded shell + feet", 1, 0.65, "", "estimate"),
 ("Dock: PCB, 4 pogo pins, USB-C, IR LED", 1, 0.90, "", "estimate"),
 ("Packaging + USB-C cable (no power brick)", 1, 1.50, "", "estimate"),
 ("Final assembly + end-of-line test (~8 min)", 1, 1.20, "", "estimate"),
 ("FCC/CE certification amortised", 1, 0.40, "", "estimate: ~$40k over 100k units"),
]
TOOLING = [("Pod front + rear (family tool, P20 steel)", 22000), ("Halo ring 2-shot, 2-cavity", 25000),
           ("Idler + pinion family tool (POM)", 6000), ("Eye lens", 4000), ("Dock shell", 10000)]


def tot(rows):
    return round(sum(q * u for _, q, u, _, _ in rows), 2)


def main():
    pt, vt, tt = tot(PROTO), tot(VOLUME), sum(c for _, c in TOOLING)
    L = ["# Ringo - Bill of Materials", "", "Prices checked 14 Nov 2026 (USD). Lines marked *estimate* are engineering estimates, not quotes.", "",
         f"**Prototype (qty 1, retail parts): ${pt:.2f}**  |  **Volume (10k units, factory cost ex-freight/duty): ${vt:.2f}**  |  Target retail: $129", "",
         "## Prototype BOM (build one this week)", "", "| Item | Qty | Unit | Ext | Source | Note |", "|---|---:|---:|---:|---|---|"]
    for n, q, u, l, note in PROTO:
        L.append(f"| {n} | {q} | ${u:.2f} | ${q*u:.2f} | {'[link](' + l + ')' if l else '-'} | {note} |")
    L += [f"| **Total** | | | **${pt:.2f}** | | |", "", "## Volume BOM (10k units)", "", "| Item | Qty | Unit | Ext | Source | Note |", "|---|---:|---:|---:|---|---|"]
    for n, q, u, l, note in VOLUME:
        L.append(f"| {n} | {q} | ${u:.2f} | ${q*u:.2f} | {'[link](' + l + ')' if l else '-'} | {note} |")
    L += [f"| **Total per unit** | | | **${vt:.2f}** | | |", "", "## One-time tooling (estimate)", "", "| Tool | USD |", "|---|---:|"]
    for n, c in TOOLING:
        L.append(f"| {n} | ${c:,} |")
    L += [f"| **Total** | **${tt:,}** |", "", "Freight, duty and channel margin are not included. At $129 retail and ~$36.5 factory cost the product has room for a 40-50 % retailer margin and still leaves roughly 35 % gross margin after ~$9 of freight, duty, warranty and returns."]
    open(os.path.join(ROOT, "BOM.md"), "w").write("\n".join(L) + "\n")
    json.dump({"proto_total": pt, "volume_total": vt, "tooling_total": tt, "retail": 129,
               "proto_lines": len(PROTO), "volume_lines": len(VOLUME)}, open(os.path.join(ROOT, "site", "assets", "bom.json"), "w"))
    print(pt, vt, tt)


if __name__ == "__main__":
    main()
