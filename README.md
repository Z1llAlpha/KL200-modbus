XKC-KL200 library is based on [RaptorSDS/KL200-python](https://github.com/RaptorSDS/KL200-pyhton/tree/main) project. It was rewritten to use non-blocking asynchronous uart functions.

You can use any ESP32 - ESP32,ESP32-C3,ESP32-C6,ESP32-S2,ESP32-S3 and etc.\
ESP32 are required because they have 2-3 channel hardware uart support. Check Espressif documentation for channel count for your chip.\
If you are using 2-channel chip - replace uart_id from 2 to 0, remove all "print" statements - they wont work correctly, and change RX/TX pins to default (1,3), so REPL will continue to work on UART0 that will still use pins connected to onboard TTL-USB converter, and you will be able to use it when TTL-RS485 converter is disconnected.

Main.py is really simple and can be easily modified for your needs.\
Running this script, ESP32 acts as Modbus RTU slave with default device address 20 (in decimal) and holding register adress 0, value type is 16bit integer.\
Default communcation parameters are: 8bit data, no parity, 1 stop bit, 115200 Modbus speed, 9600 Sensor speed. They can be easily configured, to do this - check MicroPython UART documentation.\
Default Sensor TX/RX pins are 10/9 (connect ESP TX to sensor RX, ESP RX to sensor TX)\
Default TTL-RS485 Converter TX/RX pins are 5/6 (Connect ESP TX to converter TX, ESP RX to converter RX)\
Modbus-related code is designed for TTL-RS485 converters with automatic flow control (without RE/DE pins)

Modbus communication function can be easily adjusted, you can set register type by changing function_code comparasion from 3 to required FC according to Modbus RTU Standart.

No external modules installation required
