import math
from datetime import datetime, timedelta
from queue import Queue, Empty
import signal
import sys
import time
import threading
from serial import Serial

def serial_reader(serial, start_time, revolutions):
    while True:
        # blocking until newline or EOF
        line = serial.readline().decode()

        # Convert milliseconds-since-arduino-start to a datetime
        millis = int(line.strip())
        rev_timestamp = start_time + timedelta(milliseconds=millis)
        #print(rev_timestamp.strftime('%H:%M:%S.%f'))

        revolutions.append(rev_timestamp)


def calcs(revolutions):
    while True:
        if len(revolutions) < 2:
            continue

        wheel_radius_cm = 13.0
        wheel_circumference_cm = 2 * math.pi * wheel_radius_cm

        rotation_distance_km = wheel_circumference_cm / 100000

        def get_rpm(revolutions, now, window):
            threshold = now - window
            rpm = 0.0

            stamps = []
            for ts in reversed(revolutions):
                if ts < threshold:
                    break
                stamps.append(ts)

            if len(stamps) < 2:
                return None, 0.0

            elapsed = 0.0
            # remember stamps is reversed
            for idx, ts in enumerate(stamps[1:]):
                elapsed += (stamps[idx] - stamps[idx-1]).total_seconds()
            elapsed = elapsed / (len(stamps) - 1)

            return elapsed, 1 / elapsed * 60


        elapsed, rpm = get_rpm(revolutions, datetime.now(), timedelta(seconds=5))
        if elapsed is None:
            print("STOPPED")
            time.sleep(1)
            continue
       
        km_per_sec = rotation_distance_km / elapsed
        km_per_hr = km_per_sec * 3600

        # 1 = 1 complete rotation (as we have 1 sensor)
        # 60 = desired 'per' window (i.e. 60 seconds)
        rpm = 1 / elapsed * 60

        rotations = len(revolutions)
        distance_travelled_km = rotation_distance_km * rotations

        secs_per_km = 1 / km_per_sec
        pace = timedelta(seconds=secs_per_km)

        print("%.2f km/h\t%.1f RPM\t%.2f KM\t%s/km" % (km_per_hr, rpm, distance_travelled_km, str(pace)))
        time.sleep(1)


def main():
    serial = Serial('/dev/ttyACM0', 9600)
    start_time = datetime.now()

    revolutions = []

    # Kick off the reader
    reader = threading.Thread(target=serial_reader, args=(serial, start_time, revolutions))
    reader.daemon = True
    reader.start()

    rpm = threading.Thread(target=calcs, args=(revolutions,))
    rpm.daemon = True
    rpm.start()

    try:
        while True:
            reader.join(1)
    except KeyboardInterrupt:
        print("Stopping")
    
main()

