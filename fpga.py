#
# FPGA class for ICE-V w/ Micropython
# 07-05-22 E. Brombaugh
#

from machine import Pin, SPI
import time

class FPGA:
    def setup(self):
        # set up SPI and GPIO to talk to FPGA
        self.SPI = SPI(1, 10000000, polarity=0, phase=0, sck=Pin(5), mosi=Pin(7), miso=Pin(4))
        self.CS = Pin(6, Pin.OUT)
        self.CRST = Pin(1, Pin.OUT)
        self.CDONE = Pin(0, Pin.IN)
        self.CRST.value(1)
        self.CS.value(1)

    def FPGA_Config_begin(self):
        # reset FPGA to start configuration
        self.CRST.value(0)
        time.sleep_us(1)
        self.CS.value(0)
        time.sleep_us(200)
        timeout = 100

        # wait for CDONE to go low
        while (timeout > 0) & (self.CDONE.value() == 1):
            timeout = timeout - 1

        # if CDONE didn't go low in time then error out
        if timeout == 0:
            self.CS.value(1)
            self.CRST.value(1)
            return 1

        # release reset
        self.CRST.value(1)
        
        # delay > 1200 us to allow FPGA to clear
        time.sleep_us(2000)
    
    def FPGA_Config_end(self):
        # send 160 clocks to finish configuration
        dummy = bytearray(20)
        self.SPI.write(dummy)

        # check for CDONE
        if self.CDONE.value() == 1:
            # CDONE high -> good load
            return 0
        else:
            # CDONE low -> error
            return 2

    def FPGA_Config_File(self, bitstream):
        # configure the FPGA from a file
        f = open(bitstream, 'rb')
        
        # start configuration
        self.FPGA_Config_begin()
        
        # send data 16kB at a time
        while buffer := f.read(16384):
            self.SPI.write(buffer)
        
        # finish configuration
        self.FPGA_Config_end()
        
    def FPGA_CSR_Write(self, reg, Data):
        tx = bytearray([reg & 0x7f]) + Data.to_bytes(4, 'big')
        self.CS.value(0)
        self.SPI.write(tx)
        self.CS.value(1)

    def FPGA_CSR_Read(self, reg):
        tx = bytearray(5)
        tx[0] = reg | 0x80
        rx = bytearray(5)
        self.CS.value(0)
        self.SPI.write_readinto(tx, rx)
        self.CS.value(1)
        Data = int.from_bytes(rx[1:], 'big')
        return Data
