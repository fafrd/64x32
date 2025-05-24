import subprocess
import time
import csv
from datetime import datetime
from zoneinfo import ZoneInfo

# spawn display‑text process
def start_proc(brightness):
    return subprocess.Popen(
        [
            "sudo",
            "/home/pi/bin/text",
            "--led-no-hardware-pulse",
            "--led-gpio-mapping=adafruit-hat",
            "--led-cols=64",
            "--led-rows=32",
            f"--led-brightness={brightness}",
            "-f",
            "/home/pi/rpi-rgb-led-matrix/fonts/9x15.bdf"
        ],
        stdin=subprocess.PIPE,
        text=True
    )

# load sunrise/sunset lookup
ss = {}
with open("sunrise_sunset.csv") as f:
    rd = csv.DictReader(f)
    for row in rd:
        key = (int(row["month"]), int(row["day"]))
        ss[key] = (row["sunrise"], row["sunset"])

TZ = ZoneInfo("America/Los_Angeles")
cur_brightness = None
proc = None
last_date = None

# update once a minute if day rolls over
while True:
    now = datetime.now(TZ)
    today = (now.month, now.day)

    sr, sn = ss.get(today)

    # Get times as datetime objects to determine brightness
    h, m = map(int, sr.split(":"))
    sunrise = now.replace(hour=h, minute=m, second=0, microsecond=0)
    h, m = map(int, sn.split(":"))
    sunset = now.replace(hour=h, minute=m, second=0, microsecond=0)

    # convert from 24h to 12h
    sr = sr[1:] + 'a'
    sn = str(int(sn[0:2]) - 12) + sn[2:] + 'p'

    want = 10 if now < sunrise or now > sunset else 25
    if want != cur_brightness:
        # update brightness if after sunset
        if proc:
            proc.terminate()
            proc.wait()
        proc = start_proc(want)
        cur_brightness = want
        last_date = None

    if today != last_date:
        print(f"{today} ● {sr} ◌ {sn}")
        proc.stdin.write(f"● {sr}\n")
        proc.stdin.write(f"◌ {sn}\n")
        proc.stdin.flush()
        last_date = today

    time.sleep(60)
