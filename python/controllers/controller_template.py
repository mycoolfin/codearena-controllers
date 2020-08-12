import math, random, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from api.bot_api import BotController

def main(bot):
    while True:
        # Write your code here! Uncomment the lines below for a basic example.

        # bot.set_angle(bot.get_angle() + 5)
        # bot.set_speed(10)
        # bot.shoot()

BotController(main)