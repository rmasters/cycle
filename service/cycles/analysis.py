from datetime import datetime, timedelta
import math


class RevolutionCalculator:
    def __init__(self, wheel_radius_cm):
        self.wheel_radius_cm = wheel_radius_cm

        self.revolutions = []

        self.setup()

    def setup(self):
        self.wheel_circumference_cm = 2 * math.pi * self.wheel_radius_cm
        self.rotation_distance_km = self.wheel_circumference_cm / 100000

    def record_revolutions(self, *args):
        self.revolutions.extend(args)

    def stats(self, now=None, window=None):
        now = now if now is not None else datetime.utcnow()
        window = window if window is not None else timedelta(seconds=5)

        # Get revolutions so far to calculate distance travelled in KM
        rotations = len(self.revolutions)
        distance_travelled_km = self.rotation_distance_km * rotations

        result = {
                # Aggregate metrics
                'revolutions': rotations,
                'distance_travelled_km': distance_travelled_km,
                # Live metrics
                'km_per_hr': 0.0,
                'm_per_sec': 0.0,
                'rpm': 0.0,
                'pace': timedelta(seconds=0)
                }

        # Find elapsed time in constant window to find RPM
        elapsed, rpm = self.get_rpm(now, window)
        if elapsed is None:
            # No revolutions detected in the window - cyclist has stopped
            return result
       
        km_per_sec = self.rotation_distance_km / elapsed
        result['km_per_hr'] = km_per_sec * 3600
        result['m_per_sec'] = km_per_sec / 1000

        result['rpm'] = rpm

        # Find pace
        secs_per_km = 1 / km_per_sec
        result['pace'] = timedelta(seconds=secs_per_km)

        return result

    def get_rpm(self, now, window):
        threshold = now - window
        rpm = 0.0

        stamps = []
        for ts in reversed(self.revolutions):
            if ts < threshold:
                break
            stamps.append(ts)

        if len(stamps) < 2:
           return None, 0.0

        # Average the deltas between timestamps
        elapsed = 0.0
        # remember stamps is reversed
        for idx, ts in enumerate(stamps[1:]):
            elapsed += (stamps[idx] - stamps[idx-1]).total_seconds()
        elapsed = elapsed / (len(stamps) - 1)

        # RPM:
        # 1 = 1 complete rotation (as we have 1 sensor)
        # 60 = desired 'per' window (i.e. 1 minute)
        rpm = 1 / elapsed * 60

        return elapsed, rpm

