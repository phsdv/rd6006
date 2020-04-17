from datetime import datetime
import minimalmodbus
minimalmodbus.TIMEOUT = 0.5

class RD6006:
    """Interface to RD6006 power supply"""
    def __init__(self, port, address=1, baudrate=115200, synctime=False):
        """ port is name of serial port
            adress is modbus slaveaddress
            baudrate the serial bus speed
            synctime: if true the internal datetime will be set same as local
        """
        self.port = port
        self.address = address
        self.instrument = minimalmodbus.Instrument(port=port, slaveaddress=address)
        self.instrument.serial.baudrate = baudrate
        regs = self._read_registers(0, 4)
        self.model = regs[0]
        self.sn = regs[1]<<16 | regs[2]
        self.fw = regs[3]/100
        if synctime:
            now = datetime.now()
            self.date = [now.year, now.month, now.day]
            self.time = [now.hour, now.minute, now.second]

    def __repr__(self):
        return f"RD6006 SN:{self.sn} FW:{self.fw}"

    def _read_register(self, register):
        try:
            return self.instrument.read_register(register)
        except minimalmodbus.NoResponseError:
            return self._read_register(register)

    def _read_registers(self, start, length):
        try:
            return self.instrument.read_registers(start, length)
        except minimalmodbus.NoResponseError:
            return self._read_registers(start, length)
        except minimalmodbus.InvalidResponseError:
            return self._read_registers(start, length)

    def _write_register(self, register, value):
        try:
            return self.instrument.write_register(register, value)
        except minimalmodbus.NoResponseError:
            return self._write_register(register, value)

    def _write_registers(self, start, values):
        """writes multiple values starting at start. Values must be a list"""
        try:
            return self.instrument.write_registers(start, values)
        except minimalmodbus.NoResponseError:
            return self._write_registers(start, values)
        except minimalmodbus.InvalidResponseError:
            return self._write_registers(start, values)
        
    def _unsigned2signed(self, regs):
        """convert the 2 register temperature in a single signed integer
           expects a list of 2 values with [sign, value]"""
        sign = regs[0]
        value = regs[1]
        if sign == 0:
            return value
        elif sign == 1:
            return -value
        else:
            Exception(f"Unknown value for sign: {sign}")

    def _mem(self, M=0):
        """reads the 4 register of a Memory[0-9] and print on a single line"""
        regs = self._read_registers(M*4 + 80, 4)
        print(f"M{M}: {regs[0]/100:4.1f}V, {regs[1]/1000:3.3f}A, OVP:{regs[2]/100:4.1f}V, OCP:{regs[3]/1000:3.3f}A")

    def _memall(self):
        """reads the all memory registers at once and print per line
           which is faster than reading each memory one by one"""
        regs = self._read_registers(80, 40)
        for m in range(10):
            print(f"M{m}: {regs[m*4]/100:5.2f} V, {regs[m*4+1]/1000:3.3f} A, OVP={regs[m*4+2]/100:5.2f} V, OCP={regs[m*4+3]/1000:3.3f} A")
        
    def status(self):
        regs = self._read_registers(0, 84)
        print("== Device")
        print(f"Model   : {regs[0]/10}")
        print(f"SN      : {(regs[1]<<16 | regs[2]):08d}")
        print(f"Firmware: {regs[3]/100}")
        print(f"Input   : {regs[14]/100}V")
        if regs[4]:
            sign = -1
        else:
            sign = +1
        print(f"Temp    : {sign * regs[5]}°C")
        if regs[34]:
            sign = -1
        else:
            sign = +1
        print(f"TempProb: {sign * regs[35]}°C")
        print("== Output")
        print(f"Voltage : {regs[10]/100}V")
        print(f"Current : {regs[11]/1000}A")
        print(f"Energy  : {regs[12]/1000}Ah")
        print(f"Power   : {regs[13]/100}W")
        print("== Settings")
        print(f"Voltage : {regs[8]/100}V")
        print(f"Current : {regs[9]/1000}A")
        print("== Protection")
        print(f"Voltage : {regs[82]/100}V")
        print(f"Current : {regs[83]/1000}A")
        print("== Battery")
        if regs[32]:
            print("Active")
            print(f"Voltage : {regs[33]/100}V")
        print(f"Capacity: {(regs[38] <<16 | regs[39])/1000}Ah")   # TODO check 8 or 16 bits?
        print(f"Energy  : {(regs[40] <<16 | regs[41])/1000}Wh")   # TODO check 8 or 16 bits?
        print("== Memories")
        self._memall()

    @property
    def input_voltage(self):
        return self._read_register(14)/100

    @property
    def voltage(self):
        return self._read_register(8)/100

    @property
    def meastemp(self):
        return self._unsigned2signed(self._read_registers(4, 2))

    @property
    def meastempprobe(self):
        return self._unsigned2signed(self._read_registers(34, 2))

    @property
    def meastempf(self):
        return self._unsigned2signed(self._read_registers(36, 2))

    @voltage.setter
    def voltage(self, value):
        self._write_register(8, int(value*100))

    @property
    def measvoltage(self):
        return self._read_register(10)/100

    @property
    def meascurrent(self):
        return self._read_register(11)/1000

    @property
    def measpower(self):
        return self._read_register(13)/100

    @property
    def charge(self): # used to be called measah
        return (self._read_register(38) <<16 | self._read_register(39))/1000

    @property
    def energy(self): # used to be called measwh
        return (self._read_register(40) <<16 | self._read_register(41))/1000

    @property
    def battmode(self):
        return self._read_register(32)

    @property
    def battvoltage(self):
        return self._read_register(33)

    @property
    def current(self):
        return self._read_register(9)/1000
    @current.setter
    def current(self, value):
        self._write_register(9, int(value*1000))

    @property
    def voltage_protection(self):
        return self._read_register(82)/100
    @voltage_protection.setter
    def voltage_protection(self, value):
        self._write_register(82, int(value*100))

    @property
    def current_protection(self):
        return self._read_register(83)/1000
    @current_protection.setter
    def current_protection(self, value):
        self._write_register(83, int(value*1000))

    @property
    def enable(self):
        return self._read_register(18)
    @enable.setter
    def enable(self, value):
        self._write_register(18, int(value))
    
    @property
    def ocpovp(self):
        return self._read_register(16)

    @property
    def CVCC(self):
        return self._read_register(17)
    
    @property
    def backlight(self):
        return self._read_register(72)
    @backlight.setter
    def backlight(self, value):
        self._write_register(72, value)

    @property
    def date(self):
        """returns the date as tuple: (year, month, day)"""
        y, m, d = self._read_registers(48, 3)
        return(y, m, d)  
    @date.setter
    def date(self, value):
        """Sets the date, value needs to be list with: (year, month, day)"""
        if len(value) == 3:
            self._write_registers(48, value)
        else:
            raise Exception("Date must be list with 3 values: [year,month,date]")

    @property
    def time(self):
        """returns the time as tuple: (h, m, s)"""
        h,m,s = self._read_registers(51, 3)
        return(h, m, s)  
    @time.setter
    def time(self, value):
        """"sets the time. Value must be list: [hour, minute, second]"""
        if len(value) == 3:
            self._write_registers(51, value)
        else:
            raise Exception("Time must be list with 3 values: [hour, minute, second]")

if __name__ == "__main__":
    import serial.tools.list_ports
    for port in serial.tools.list_ports.comports():
        if 'CH340' in port[1]:
            break
    else:
        raise Exception("No port not found, is USB cable plugged in?")
        
    ps1 = RD6006(port[0], synctime=True)
    ps1.status()
