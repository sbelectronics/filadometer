""" Nixie Tube Filodometer
    Scott Baker
    http://www.smbaker.com/
"""

import requests
import threading
import time
import traceback
from smbpi.nixie_shift import NixieShift, PIN_DATA, PIN_LATCH, PIN_CLK

PROMETHEUS_URL = "http://198.0.0.246:8000/"


class Filodometer(threading.Thread):
    def __init__(self, nixie):
        super(Filodometer, self).__init__()
        self.nixie = nixie
        self.daemon = True
        self.extrusion_print = 0
        self.progress = 0
        self.last_value = -1

    def run_once(self):
        r = requests.get(PROMETHEUS_URL)
        if r.status_code != 200:
            return

        for line in r.text.split("\n"):
            line = line.strip()
            if line.startswith("extrusion_print "):
                parts = line.split(" ")
                self.extrusion_print = float(parts[1])
                # print "extrusion_print", self.extrusion_print
            elif line.startswith("progress "):
                parts = line.split(" ")
                self.progress = float(parts[1])
                # print "progress", self.progress
            elif line.startswith("printing "):
                parts = line.split(" ")
                self.printing = float(parts[1]) > 0

        if self.printing:
            value = int(self.extrusion_print/10)*10000 + int(self.progress*10) + 2
        else:
            value = None

        if value != self.last_value:
            if (value is not None):
                print "update extrusion %0.1f progress %d%%" % (self.extrusion_print/10.0, self.progress)
                self.nixie.set_blank([1])
                self.nixie.set_value(value)
            else:
                print "blanking the display"
                self.nixie.set_blank([1, 2, 3, 4, 5, 6, 7, 8])
                self.nixie.set_value(0)
            self.last_value = value

    def run(self):
        while True:
            try:
                self.run_once()
            except Exception:
                traceback.print_exc()
                time.sleep(10)
            time.sleep(0.1)


def main():
    n = NixieShift(PIN_DATA, PIN_LATCH, PIN_CLK, 8, True, blank=[1])

    Filodometer(n).start()

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
