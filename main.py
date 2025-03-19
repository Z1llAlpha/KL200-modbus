import uasyncio as asyncio
from machine import UART, Pin
from XKC_KL200 import XKC_KL200

# Initialize sensor on UART1
sensor = XKC_KL200(uart_id=1, baudrate=9600, tx_pin=10, rx_pin=9)
sensor.begin(9600)

# Initialize UART2 for Modbus communication
uart2 = UART(2, baudrate=115200, tx=5, rx=6)

MODBUS_SLAVE_ADDRESS = 20

def crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc = crc ^ byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc = crc >> 1
    return crc

async def modbus_slave():
    # Create a StreamReader&StreamWriter for UART2
    reader, writer = asyncio.StreamReader(uart2), asyncio.StreamWriter(uart2, {})
    
    while True:
        try:
            # Attempt to read 8 bytes with non-blocking function
            command = await asyncio.wait_for_ms(reader.readexactly(8), 100)
            if command[0] == MODBUS_SLAVE_ADDRESS:  # Check if it's for our device
                function_code = command[1]
                if function_code == 3:  # If function code is "Read Holding Registers"
                    # Assuming request for single register at address 0
                    response = bytearray([MODBUS_SLAVE_ADDRESS, 3, 2, 0, 0])
                    distance = await sensor.read_distance()
                    response[3:5] = distance.to_bytes(2, 'big')
                    checksum = crc16(response)
                    response.append(checksum & 0xFF)
                    response.append((checksum >> 8) & 0xFF)
                    writer.write(response)
                    await writer.drain()
        except asyncio.TimeoutError:
            # If there's no data within 100ms, continue the loop without blocking
            pass
        except Exception as e:
            # Handle any other exceptions
            print(f"Error in Modbus communication: {e}")
        
        # Small delay to prevent CPU hogging and REPL correct work
        await asyncio.sleep_ms(10)

async def main():
    asyncio.create_task(modbus_slave()) #Run Modbus communication function
    while True:
        # Print distance
        distance = await sensor.read_distance()
        print(f"Distance: {distance}")
        await asyncio.sleep(1)

# Run the main coroutine
asyncio.run(main())

