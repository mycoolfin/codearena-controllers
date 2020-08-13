import math, random, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from api.bot_api import BotController

SLOW_SPEED = 30
STANDARD_SPEED = 50
ESCAPE_SPEED = 100

def angle_between(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

def distance_between(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

def delta_angle(angle1, angle2):
    diff = (angle1 - angle2) % 360.0
    return diff - 360.0 if diff >= 180.0 else diff

def find_nearest_energy(my_x, my_y, energy_sources):
    charged_sources = [x for x in energy_sources if x.can_consume]
    if not charged_sources:
        return None
    return sorted(charged_sources, key=lambda e: distance_between(my_x, my_y, e.x, e.y))[0]

def get_world_info(bot):
    health = bot.get_health()
    energy = bot.get_energy()
    my_x, my_y = bot.get_position()
    my_angle = bot.get_angle()
    objects_in_view = bot.get_visible_objects()
    enemy = next((x for x in objects_in_view.bots), None)
    energy_sources = objects_in_view.energy_sources
    bullets = objects_in_view.bullets
    return health, energy, my_x, my_y, my_angle, enemy, energy_sources, bullets

def avoid_obstacles(bot, my_angle, bullets):
    avoiding = False

    # Check for incoming bullets.
    for bullet in bullets:
        diff = delta_angle(my_angle, (180 - bullet.angle))
        collision_imminent = abs(diff) < 20
        if collision_imminent: # Recoil backwards at an angle.
            avoiding = True
            bot.set_speed(-ESCAPE_SPEED)
            if diff > 0:
                bot.set_angle(my_angle + 45)
            else:
                bot.set_angle(my_angle + 45)
            break

    # Check for other obstacles.
    _, front_left, front_center, front_right, _, _ = bot.get_distances()
    front_distances = [front_left, front_center, front_right]
    min_dist = min(front_distances)
    if min_dist < 0.1:
        avoiding = True
        bot.set_speed(-ESCAPE_SPEED)
        bot.set_angle(my_angle + 180)
    elif min_dist < 1:
        avoiding = True
        bot.set_speed(0)
        sorted_distances = sorted(range(len(front_distances)), key=lambda i: front_distances[i])
        min_index = sorted_distances[0]
        max_index = sorted_distances[-1]
        if min_index == 1 or max_index == 1:
            bot.set_angle(my_angle + 180)
        elif min_index == 0:
            bot.set_angle(my_angle - 45)
        elif min_index == 2:
            bot.set_angle(my_angle + 45)
        else:
            avoiding = False

    return avoiding

def react_to_enemy(bot, my_x, my_y, my_angle, energy, enemy):
    if energy >= 600:
        bot.set_speed(ESCAPE_SPEED)
        bot.set_angle(angle_between(my_x, my_y, enemy.x, enemy.y))

        # If we're within range and we have enough energy, overcharge!
        if distance_between(my_x, my_y, enemy.x, enemy.y) < 2:
            bot.overcharge()
        return True
    else:
        return False

def react_to_energy(bot, my_x, my_y, my_angle, nearest_energy):
    e_x, e_y = (nearest_energy.x, nearest_energy.y)
    dist = distance_between(my_x, my_y, e_x, e_y)
    if dist > 0.5:
        new_angle = angle_between(my_x, my_y, e_x, e_y)
        bot.set_angle(new_angle)
    if dist < 0.5:
        bot.set_speed(0)
        bot.consume_energy()
        bot.set_angle(random.random() * 360)
    elif dist < 2:
        bot.set_speed(SLOW_SPEED)
    else:
        bot.set_speed(STANDARD_SPEED)

def main(bot):
    while True:
        health, energy, my_x, my_y, my_angle, enemy, energy_sources, bullets = get_world_info(bot)
        avoiding = avoid_obstacles(bot, my_angle, bullets)
        if avoiding:
            continue

        if enemy is not None:
            attacking = react_to_enemy(bot, my_x, my_y, my_angle, energy, enemy)
            if attacking:
                continue

        if energy < 700:
            nearest_energy = find_nearest_energy(my_x, my_y, energy_sources)
            if nearest_energy is not None:
                react_to_energy(bot, my_x, my_y, my_angle, nearest_energy)
                continue

        bot.set_speed(STANDARD_SPEED)

BotController(main)
