import time
from datetime import timedelta

def reporter_thread(calc, print_every=None):
    if print_every is None:
        print_every = timedelta(seconds=0.5)

    while True:
        stats = calc.stats()

        line = [
                "%(km_per_hr).2f KM/H" % stats,
                "%(rpm)d RPM" % stats,
                "%(distance_travelled_km).2f KM" % stats,
                "Pace: %s" % stats['pace'],
                ]

        print("\t".join(line))

        time.sleep(print_every.seconds)

