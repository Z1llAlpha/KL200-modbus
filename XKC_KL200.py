import machine
import uasyncio as asyncio
from machine import UART, Pin

class XKC_KL200:
    def __init__(self, uart_id, baudrate=9600, tx_pin=10, rx_pin=9):
        self.uart = UART(uart_id, baudrate, tx=tx_pin, rx=rx_pin)
        self.available = False
        self.distance = 0
        self.last_received_distance = 0
        self.reader = asyncio.StreamReader(self.uart)

    async def send_command(self, command):
        checksum = self.calculate_checksum(command)
        command.append(checksum)
        self.uart.write(bytearray(command))

    @staticmethod
    def calculate_checksum(data):
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum

    def begin(self, baudrate):
        self.uart.init(baudrate)

    async def read_distance(self):
        command = [0x62, 0x33, 0x09, 0xFF, 0xFF, 0x00, 0x00, 0x00]
        await self.send_command(command)

        try:
            response = await asyncio.wait_for_ms(self.reader.readexactly(9), 1000)
            if response[0] == 0x62 and response[1] == 0x33:
                length = response[2]
                address = (response[3] << 8) | response[4]
                raw_distance = (response[5] << 8) | response[6]
                checksum = response[8]
                calc_checksum = self.calculate_checksum(response[:8])
                if checksum == calc_checksum:
                    self.distance = raw_distance
                    self.last_received_distance = raw_distance
                    self.available = True
        except asyncio.TimeoutError:
            # Handle timeout if no response is received
            print("Timeout waiting for sensor response")
        
        return self.distance

    def available(self):
        return self.available

    def get_distance(self):
        self.available = False
        return self.distance
  
    async def restore_factory_settings(self, hard_reset=True):
        reset_byte = 0xFE if hard_reset else 0xFD
        command = [0x62, 0x39, 0x09, 0xFF, 0xFF, 0xFF, 0xFF, reset_byte]
        await self.send_command(command)

    async def change_address(self, address):
        if address > 0xFFFE:
            raise ValueError("Address out of range")
        command = [0x62, 0x32, 0x09, 0xFF, 0xFF, (address >> 8) & 0xFF, address & 0xFF]
        await self.send_command(command)

    async def change_baud_rate(self, baud_rate):
        if baud_rate > 9:
            raise ValueError("Baud rate out of range")
        command = [0x62, 0x30, 0x09, 0xFF, 0xFF, baud_rate]
        await self.send_command(command)

    async def set_upload_mode(self, auto_upload):
        mode = 1 if auto_upload else 0
        command = [0x62, 0x34, 0x09, 0xFF, 0xFF, mode]
        await self.send_command(command)

    async def set_upload_interval(self, interval):
        if interval < 1 or interval > 100:
            raise ValueError("Interval out of range")
        command = [0x62, 0x35, 0x09, 0xFF, 0xFF, interval]
        await self.send_command(command)

    async def set_led_mode(self, mode):
        if mode > 3:
            raise ValueError("LED mode out of range")
        command = [0x62, 0x37, 0x09, 0xFF, 0xFF, mode]
        await self.send_command(command)

    async def set_relay_mode(self, mode):
        if mode > 1:
            raise ValueError("Relay mode out of range")
        command = [0x62, 0x38, 0x09, 0xFF, 0xFF, mode]
        await self.send_command(command)

    async def set_communication_mode(self, mode):
        if mode > 1:
            raise ValueError("Communication mode out of range")
        command = [0x62, 0x31, 0x09, 0xFF, 0xFF, mode]
        await self.send_command(command)
  
    def get_last_received_distance(self):
        return self.last_received_distance
