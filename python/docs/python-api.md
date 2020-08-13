<a name="bot_api"></a>
# Python 3 API Reference

<a name="bot_api.BotController"></a>
## BotController

```python
class BotController()
```

---

<a name="bot_api.BotController.get_health"></a>
#### get\_health()

Gets the health of the bot.

**Returns**:

- `health` _float_ - the current health of the bot between 0 and 100.

---

<a name="bot_api.BotController.get_energy"></a>
#### get\_energy()

Gets the energy of the bot.

**Returns**:

- `energy` _float_ - the current energy of the bot between 0 and 1000.

---

<a name="bot_api.BotController.get_position"></a>
#### get\_position()

Gets the position of the bot.

**Returns**:

- `position` _float, float_ - the 2D coordinates of the bot in world space.

---

<a name="bot_api.BotController.get_angle"></a>
#### get\_angle()

Gets the angle of the bot.

**Returns**:

- `angle` _float_ - the angle of the bot in degrees, anti-clockwise relative to the x-axis.

---

<a name="bot_api.BotController.get_distances"></a>
#### get\_distances()

Gets readings from all distance sensors on the bot.

**Returns**:

- `distances` _DistanceSensors_ - the readings from each distance sensor on the bot.

---

<a name="bot_api.BotController.get_visible_objects"></a>
#### get\_visible\_objects()

Gets list of all objects visible to the bot.

**Returns**:

- `visible_objects` _VisibleObjects_ - lists of all objects visible to the bot.
---
<a name="bot_api.BotController.set_speed"></a>
#### set\_speed(speed)

Sets the desired speed of the bot.

**Arguments**:

- `speed` _float_ - value between 0 (stopped) and 100 (maximum speed).

---

<a name="bot_api.BotController.set_angle"></a>
#### set\_angle(angle)

Sets the desired angle of the bot.

**Arguments**:

- `angle` _float_ - the desired angle of the bot in degrees, anti-clockwise relative to the x-axis.

---

<a name="bot_api.BotController.consume_energy"></a>
#### consume\_energy()

Attempts to consume a nearby, active energy source.

**Returns**:

- `success` _bool_ - a boolean value indicating whether the source was successfully consumed.

---

<a name="bot_api.BotController.shoot"></a>
#### shoot()

Attempts to shoot a bullet if the bot has enough energy.

**Returns**:

- `success` _bool_ - a boolean value indicating whether the bullet was fired.

---

<a name="bot_api.BotController.overcharge"></a>
#### overcharge()

Attempts to activate an overcharge attack if the bot has enough energy.

**Returns**:

- `success` _bool_ - a boolean value indicating whether the overcharge was successfully activated.

---

<a name="bot_api.BotController.wait"></a>
#### wait()

Does nothing for one in-game tick.

---
