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
        if not sys.version >= "3.5.3":
            raise Exception(
                "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version)
        print("IoT Hub Client for Python")

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()
        print("object created")

        # connect the client.
        await module_client.connect()
        print("connected to client, new gpio user")

        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity

        # define behavior for receiving an input message on input1
        async def input1_listener(module_client):
            while True:
                input_message = {"temperature_c": temperature_c,
                                "temperature_f": temperature_f,
                                "humidity": humidity}
                print("forwarding mesage to temperatureHumidityOutput, ", input_message)
                await module_client.send_message_to_output(json.dumps(input_message), "temperatureHumidityOutput")
                time.sleep(10)

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)

        # Schedule task for C2D Listener
        listeners = asyncio.gather(input1_listener(module_client))

        print("The sample is now waiting for messages.")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()

        time.sleep(5)

    except Exception as e:
        print("Unexpected error %s " % e.args)
        #raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())
