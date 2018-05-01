# RaspberryPi cycle computer

Hack project after I broke my cycle computer. Consists of a Python server that
counts cadence from the reed switch (in most cheap exercise bikes), calculates
telemetry (speed, distance, pace), and delivers it to a React dashboard via
websocket.

## Todo before human consumption

*   [x] Wheel build
*   [ ] Configuration file

## Usage (at risk)

1.  Setup a Raspberry Pi with internet connectivity, and install:
    1.  `apt-get install -y python3 python3-pip`
    2.  `pip3 install wheel`
2.  Pull the repo
3.  In `onboard/`:
    1.  Run `make wheel`
    2.  Copy the `.whl` file to the rpi and run `pip3 install cycles.onboard.whl`
4.  In `web/`:
    1.  Hack in your rpi IP to `web/app/components/Dashboard/index.jsx` in `new Websocket(...)`
    2.  In `web/`, run `webpack --mode=production`
5.  On the rpi, run `onboard`
6.  Load the web dashboard

