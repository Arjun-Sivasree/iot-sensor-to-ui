# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import sys
import asyncio
import json
from board import D4
import adafruit_dht
from six.moves import input
from azure.iot.device.aio import IoTHubModuleClient

# Initial the dht device
dhtDevice = adafruit_dht.DHT11(D4)

async def main():
    try:
        print("IoT Hub Client for Python")

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()
        print("object created once")

        # connect the client.
        await module_client.connect()
        print("connected to client, new iothub user")

        while True:
            try:
                # Print the values to the serial port
                temperature_c = dhtDevice.temperature
                temperature_f = temperature_c * (9 / 5) + 32
                humidity = dhtDevice.humidity

                # define behavior for receiving an input message on input1
                #async def input1_listener(module_client):
                #while True:
                input_message = {"temperature_c": temperature_c,
                                "temperature_f": temperature_f,
                                "humidity": humidity}
                print("forwarding mesage to temperatureHumidityOutput, ", input_message)
                await module_client.send_message_to_output(json.dumps(input_message), "temperatureHumidityOutput")

                # Finally, disconnect
                await module_client.disconnect()
            
            except Exception as e:
                print("Unexpected error while reading dht11 data %s " % e.args)            

            time.sleep(10)

    except Exception as e:
        print("Unexpected error while connecting to iot hub%s " % e.args)

if __name__ == "__main__":
    asyncio.run(main())