import asyncio
from bleak import BleakClient
import json
import requests

from pycycling.cycling_power_service import CyclingPowerService

core_running=False

async def run(trainer_address, warp_core_address):
    async with BleakClient(trainer_address) as client:
        def my_measurement_handler(data):
            global core_running
            speed = data.instantaneous_power

            speed = int(speed/500*255)

            segments = []
            segments.append({"on": True})

            for segment in range(1,10):
                if speed > 0:
                    if not core_running:
                        segments.append({"on": True, "sx":speed})
                    else:
                        segments.append({"sx":speed})
                else:
                    segments.append({"on": False})

            if speed > 0:
                if not core_running:
                    core_running = True
            else:
                core_running = False

            command = {"seg":segments}
            requests.post(f"http://{warp_core_address}/json/state", json=command)

        await client.is_connected()
        trainer = CyclingPowerService(client)
        trainer.set_cycling_power_measurement_handler(my_measurement_handler)
        await trainer.enable_cycling_power_measurement_notifications()
        while True:
            await asyncio.sleep(120)
#        await trainer.disable_cycling_power_measurement_notifications()


if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    trainer_address = "CF:1D:0F:D9:7C:6D"
    warp_core_address = "wled-48fc18.local"

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(trainer_address, warp_core_address))
