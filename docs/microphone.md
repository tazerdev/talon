# Talon NFC Station

## Hardware

Many of the components listed below are optional, or may have cheaper alternatives. I chose to go with a balanced XLR based microphone for it's exceptional noise rejection. Because of that choice I needed an XLR compatible audio device. The microphone I chose can be built using a standard microphone jack, which greatly increases the compatibility with standard sound cards while decreasing costs, however it comes at the cost of increased noise and reduced cable length.

CAT6 UTP has excellent noise cancellation by its very nature. The XLR micrphone is powered via 48V phantom power which results in no detectable noise/interference in recordings.

Another benefit of this microphone is weather proofing. I've had trouble using a plastic sheet to cover the 'bucket', so I simply wrapped a bit of cling wrap around the mic itself and that's been working just fine. I now consider the mic 'all-weather' as it's effectively rain-proof and can tolerate temps within -22F to 158F.

The Roland Rubix22 has 2 channels for input and gain can be adjusted independently for each channel.

The squirrel baffle probably only increases signal a tiny bit, but it is very directional thus reducing a bunch of local noise. This means it doesn't 'hear" as much of the sky as it could.

The Raspberry Pi is also optional. You can have 30-60ft of CAT6 cable which should easily accommodate a long run to an internal system. I chose the RPI because I can put it in a box with a battery and leave it outside.

### Raspberry Pi5

The NVMe case and drive are optional. You can pick up a Pi case for as little as $10. A case with a fan is desirable. Also, if you intend to use the Pi off the network, you should pick up an RTC battery for $10. This will allow the Pi to retain its time relatively accurately (may be off by a second or two per day.)

```
-  $92.99 - Raspberry Pi5 $92.99
-  $12.99 - MicroSD Card (Amazon Basics)
-  $38.00 - Argon NEO 5 M.2 NVME PCIE Case
-  $31.00 - Crucial 1TB NVMe Drive
-   $5.00 - Raspberry Pi5 RTC Battery (optional)
-------------------------------------------------------------------
  $152.37
```

### Audio Device

I've read that the Scarlet 2i2 works well under Linux, but is about $20 more than the Roland. I believe it used to be much cheaper but the price has gone up substantnially.

```
- $174.99 - Roland Rubix22
-------------------------------------------------------------------
  $174.99
```

### Microphone (durable, nearly all-weather if using plastic wrap)

Resistor and capacitor can be changed, to some degree, to alter low frequency nose rejection. Cable length can be extended up to 50ft from what I've ready, perhaps longer. Microphone based on (https://potardesign.com/simple-p48-for-electret-mic-capsules/).

```
-   $3.75 - 1 GLS Audio XLR Male Plugs Connectors
-   $0.08 - 1 68K Ohm resistor
-   $0.19 - 1 Panasonic 3.3uF, 63V, aluminum electrolytic capacitor
-   $2.73 - 1 PUI Audio AOM-5024L-HD-R Electret microphone capsule
-   $5.61 - 1 30ft CAT6 cable
-------------------------------------------------------------------
   $12.36
```

### Microphone Parabolic Bucket (optional)

The 10" Birds Choice Protective Dome seems to be as effective as the PFNRTH, and only $18.99. You'll need to downsize the plant pot accordingly.

```
-   $3.48 - 1 12" plant pot from Lowe's
-   $2.00 - 2 'erector set' like hobbyist components from Lowe's (estimate)
-   $1.48 - 2 short screws
-   $1.48 - 1 long screw
-   $4.34 - 2 big washers
-  $30.99 - 1 12" PFNRTH parabolic squirrel baffle
-   $6.99 - 1 arca-swiss plate (for tripod mounting)
-------------------------------------------------------------------
   $50.76
```

### Miscellaneous

The Plano field box works, but the Pi gets hot once the morning sun hits it. It killed one of my Pi's before I learned to hide it in the shade. A bigger box would be better as there's more air to absorb the heat.

```
-  $11.99 - 1 Plano 131250 field box $11.99
-   $4.78 - 1 2" cable pass-through grommet (Lowe's) $4.78
- $129.99 - 1 Anker 737 Power Bank (optional)
-------------------------------------------------------------------
  $146.76
```
