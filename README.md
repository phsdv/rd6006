# RIDEN RD6006 Python module

This module allows to control a RD6006 via the USB interface using Python.

As with previous models, the RD6006 uses the Modbus protocol over serial, the
registers however are different than the DPS models. The registers are described
in the [registers.md](registers.md) file.

## Features

It allows to control the following options :
 * Output voltage and current
 * Protection voltage and current
 * Backlight
 * Enable status

## Installation
```
$ python setup.py install --user
```

## Usage

```
In [1]: from rd6006 import RD6006
In [2]: r = RD6006('/dev/ttyUSB3')                                                                         
In [3]: r.status()                                                                                                
== Device
Model   : 60062
SN      : 3917
Firmware: 1.26
Input   : 12.28V
Temp    : 26°C
== Output
Voltage : 0.0V
Current : 0.0A
Power   : 0.0W
== Settings
Voltage : 3.33V
Current : 0.2A
== Protection
Voltage : 3.4V
Current : 0.2A

In [8]: r.voltage=1.8                                                                                             
In [10]: r.enable=True                                                                                            
In [11]: r.status()                                                                                               
== Device
Model   : 60062
SN      : 00007222
Firmware: 1.26
Input   : 24.09 V
Temp    : 29 °C
TempProb: 25 °C
== DateTime
Date    : 2020-4-17
Time    : 10:57:57
== Settings
Voltage : 13.50 V
Current : 0.100 A
OVP     : 15.00 V
OCP     : 1.000 A
== Output
Voltage : 13.04 V
Current : 0.098 A
Power   : 1.27 W
== Energy
Charge  : 0.0 Ah
Energy  : 0.003 Wh
== Battery
Active
Voltage : 13.01 V
== Memories
M0: 13.50 V, 0.100 A, OVP=15.00 V, OCP=1.000 A
M1:  5.00 V, 6.100 A, OVP=62.00 V, OCP=6.200 A
M2: 12.00 V, 0.100 A, OVP=13.00 V, OCP=0.200 A
M3:  3.01 V, 2.000 A, OVP=55.00 V, OCP=2.000 A
M4:  5.00 V, 6.100 A, OVP=62.00 V, OCP=6.200 A
M5:  5.00 V, 6.100 A, OVP=62.00 V, OCP=6.200 A
M6:  5.00 V, 6.100 A, OVP=62.00 V, OCP=6.200 A
M7:  5.00 V, 6.100 A, OVP=62.00 V, OCP=6.200 A
M8:  7.89 V, 1.234 A, OVP=62.00 V, OCP=6.200 A
M9:  1.00 V, 2.000 A, OVP= 3.00 V, OCP=4.000 A
```
