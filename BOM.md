# Ringo - Bill of Materials

Prices checked 14 Nov 2026 (USD). Lines marked *estimate* are engineering estimates, not quotes.

**Prototype (qty 1, retail parts): $150.73**  |  **Volume (10k units, factory cost ex-freight/duty): $36.47**  |  Target retail: $129

## Prototype BOM (build one this week)

| Item | Qty | Unit | Ext | Source | Note |
|---|---:|---:|---:|---|---|
| Seeed XIAO ESP32-S3 Sense (MCU + OV2640 camera + PDM mic + Li-ion charger) | 1 | $19.99 | $19.99 | [link](https://www.seeedstudio.com/XIAO-ESP32S3-Sense-p-5639.html) | list price |
| Waveshare 1.28in round LCD module (GC9A01, 240x240) | 1 | $14.99 | $14.99 | [link](https://www.waveshare.com/product/displays/lcd-oled/1.28inch-lcd-module.htm) | list price |
| Adafruit N20 DC motor w/ magnetic encoder, 6V 1:150 (#4640) | 2 | $12.50 | $25.00 | [link](https://www.adafruit.com/product/4640) | list price; print pinion with long hub for the short shaft |
| Adafruit DRV8833 motor driver breakout (#3297) | 1 | $5.95 | $5.95 | [link](https://www.adafruit.com/product/3297) | list price |
| Adafruit MAX98357A I2S 3W amp (#3006) | 1 | $5.95 | $5.95 | [link](https://www.adafruit.com/product/3006) | list price |
| Adafruit mini metal speaker 8ohm 0.5W (#1890) | 1 | $1.95 | $1.95 | [link](https://www.adafruit.com/product/1890) | list price |
| Adafruit 18650 Li-ion 2200 mAh (#1781) | 1 | $9.95 | $9.95 | [link](https://www.adafruit.com/product/1781) | list price |
| Adafruit MPU-6050 6-DoF IMU (#3886) | 1 | $12.95 | $12.95 | [link](https://www.adafruit.com/product/3886) | list price |
| Adafruit VL53L0X ToF sensor (#3317) | 2 | $14.95 | $29.90 | [link](https://www.adafruit.com/product/3317) | list price (front + cliff) |
| Adafruit NeoPixel 5050 10-pack (#1655) | 1 | $4.50 | $4.50 | [link](https://www.adafruit.com/product/1655) | list price; 4 used |
| Adafruit magnetic pogo connector, 4 contact (#5358) | 1 | $6.50 | $6.50 | [link](https://www.adafruit.com/product/5358) | list price; stands in for belly pads + dock pogos |
| Filament: ~320 g PETG (translucent rings + shells) + ~90 g TPU 85A (treads) | 1 | $9.10 | $9.10 | - | estimate at ~$20/kg PETG, ~$30/kg TPU |
| Ballast: ~55 g steel washers / M10 nuts | 1 | $1.00 | $1.00 | - | estimate |
| Fasteners: 4x M2.5x8 self-tap, 4x 3x13 mm dowel pins, nickel strip, wire | 1 | $3.00 | $3.00 | - | estimate |
| **Total** | | | **$150.73** | | |

## Volume BOM (10k units)

| Item | Qty | Unit | Ext | Source | Note |
|---|---:|---:|---:|---|---|
| ESP32-S3-WROOM-1-N8R8 module | 1 | $3.48 | $3.48 | [link](https://www.lcsc.com/product-image/C2913201.html) | LCSC 1,300+ price |
| OV2640 2MP DVP camera module, 24-pin | 1 | $4.35 | $4.35 | [link](https://www.alibaba.co.uk/product-detail/Factory-Price-Hdr-Night-Vision-Raspberry_1601403116305.html) | Alibaba ~1k pcs |
| 1.28in round IPS TFT, GC9A01 | 1 | $2.06 | $2.06 | [link](https://www.alibaba.com/product-detail/1-28-240X240-Round-TFT-LCD_1600308475631.html) | Alibaba >=10k pcs |
| N20 6V gearmotor with Hall encoder (TT Motor GM12-N20VA-EN class) | 2 | $3.50 | $7.00 | [link](https://www.alibaba.com/product-detail/N20-N30-DC-MOTOR-high-torque_1601200428436.html) | Alibaba >=1k pcs; 25 mm D-shaft option |
| 18650 Li-ion cell 3000 mAh (EVE 30P class) | 1 | $1.70 | $1.70 | [link](https://www.alibaba.co.uk/product-detail/EVE-18650-30P-3000mAh-3-6V_1601583882182.html) | Alibaba 200-600+ pcs |
| ST VL53L0X ToF sensor (front + cliff) | 2 | $1.50 | $3.00 | [link](https://www.eboxtao.com/VL53L0XV2-Time-of-Flight-Laser-Ranging-Sensor-Serial-PWM-Output.html) | estimate from $1.14-1.80 module listings |
| DRV8833 dual H-bridge | 1 | $0.45 | $0.45 | [link](https://www.lcsc.com/search?q=DRV8833) | estimate |
| Li-ion charger + protection (TP4056 + DW01A + FS8205A) | 1 | $0.15 | $0.15 | [link](https://www.lcsc.com/search?q=TP4056) | estimate |
| MAX98357A class-D amp | 1 | $0.90 | $0.90 | [link](https://www.lcsc.com/search?q=MAX98357A) | estimate |
| 6-axis IMU (QMI8658) | 1 | $0.60 | $0.60 | [link](https://www.lcsc.com/search?q=QMI8658) | estimate |
| PDM MEMS microphones | 2 | $0.20 | $0.40 | [link](https://www.lcsc.com/search?q=PDM%20MEMS%20microphone) | estimate |
| WS2812B-2020 LEDs | 4 | $0.04 | $0.16 | [link](https://www.lcsc.com/search?q=WS2812B-2020) | estimate |
| Passives, FPC connectors, crystal-free (module) misc | 1 | $0.80 | $0.80 | - | estimate |
| Main PCB 68x42 2-layer + SMT assembly | 1 | $2.20 | $2.20 | - | estimate at 10k |
| 28 mm 8 ohm speaker | 1 | $0.35 | $0.35 | - | estimate |
| Belly pad board (gold pads) | 1 | $0.15 | $0.15 | - | estimate |
| Pod shells front + rear, PC/ABS (~130 g) molded | 1 | $1.00 | $1.00 | - | estimate: resin ~$0.40 + press time |
| Halo rings x2, PC + TPU 2-shot overmold | 1 | $2.40 | $2.40 | - | estimate |
| Idlers x4 + pinions x2, POM | 1 | $0.25 | $0.25 | - | estimate |
| Eye lens PMMA, hard-coated | 1 | $0.20 | $0.20 | - | estimate |
| Steel ballast keel (stamped, 54 g) + 4 pins + 4 screws | 1 | $0.22 | $0.22 | - | estimate |
| Dock: molded shell + feet | 1 | $0.65 | $0.65 | - | estimate |
| Dock: PCB, 4 pogo pins, USB-C, IR LED | 1 | $0.90 | $0.90 | - | estimate |
| Packaging + USB-C cable (no power brick) | 1 | $1.50 | $1.50 | - | estimate |
| Final assembly + end-of-line test (~8 min) | 1 | $1.20 | $1.20 | - | estimate |
| FCC/CE certification amortised | 1 | $0.40 | $0.40 | - | estimate: ~$40k over 100k units |
| **Total per unit** | | | **$36.47** | | |

## One-time tooling (estimate)

| Tool | USD |
|---|---:|
| Pod front + rear (family tool, P20 steel) | $22,000 |
| Halo ring 2-shot, 2-cavity | $25,000 |
| Idler + pinion family tool (POM) | $6,000 |
| Eye lens | $4,000 |
| Dock shell | $10,000 |
| **Total** | **$67,000** |

Freight, duty and channel margin are not included. At $129 retail and ~$36.5 factory cost the product has room for a 40-50 % retailer margin and still leaves roughly 35 % gross margin after ~$9 of freight, duty, warranty and returns.
