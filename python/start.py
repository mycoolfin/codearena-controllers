import sys
from subprocess import Popen

BLUE_SCRIPT = "controllers/shy_steve.py"
ORANGE_SCRIPT = "controllers/kamikaze_kevin.py"

BLUE_PORT = 7777
ORANGE_PORT = 8888

blue = Popen([sys.executable, BLUE_SCRIPT, f"-p {BLUE_PORT}"])
orange = Popen([sys.executable, ORANGE_SCRIPT, f"-p {ORANGE_PORT}", "-t"])
blue.wait()
orange.wait()