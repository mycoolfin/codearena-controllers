import inspect
import json
import socket
import sys
from argparse import ArgumentParser
from collections import namedtuple
from threading import Thread

class _Client:
    def __init__(self, port):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect(("localhost", self.port))
        except ConnectionError:
            print(f"Could not connect to server on port {port}.")
            sys.exit()

    def send_data(self, body):
        try:
            self.socket.sendall(bytes(json.dumps(body), "utf-8"))
        except BrokenPipeError:
            print(f"The server on port {self.port} closed the connection.")
            sys.exit()
        received = str(self.socket.recv(1024), "utf-8")
        if received == "":
            print(f"The server on port {self.port} closed the connection.")
            sys.exit()
        return received

class _TracerClient(_Client):
    def __init__(self, port):
        super().__init__(port)
        self.data_to_send = None
        self.sender_thread = Thread(target=self.run)
        self.sender_thread.daemon = True
        self.sender_thread.start()

    def send_source(self, source_code):
        self.send_data({"sourceCode": source_code})

    def send_line(self, line_no):
        self.send_data({"currentLine": line_no})

    def trace_lines(self, frame, event, source_filename):
        if frame.f_code.co_filename != source_filename:
            return
        line_no = frame.f_lineno
        if event == "line":
            self.data_to_send = line_no

    def run(self):
        while True:
            if self.data_to_send:
                self.send_line(self.data_to_send)
                self.data_to_send = None

class _BotClient(_Client):
    def send_command(self, command, *args):
        response = json.loads(self.send_data({"command": command, "args": args}))["response"]
        if response is None:
            print(f"The server refused the command '{command}'.")
        return response

class _Command:
    GetHealth = "GetHealth"
    GetEnergy = "GetEnergy"
    GetPosition = "GetPosition"
    GetAngle = "GetAngle"
    GetDistances = "GetDistances"
    GetVisibleObjects = "GetVisibleObjects"
    SetSpeed = "SetSpeed"
    SetAngle = "SetAngle"
    ConsumeEnergy = "ConsumeEnergy"
    Shoot = "Shoot"
    Overcharge = "Overcharge"
    Wait = "Wait"

DistanceSensors = namedtuple("DistanceSensors", ["left", "front_left", "front_center", "front_right", "right", "back"])
VisibleObjects = namedtuple("VisibleObjects", ["bots", "energy_sources", "bullets"])
VisibleBot = namedtuple("VisibleBot", ["x", "y", "angle", "health", "energy"])
VisibleEnergySource = namedtuple("VisibleEnergySource", ["x", "y", "angle", "can_consume"])
VisibleBullet = namedtuple("VisibleBullet", ["x", "y", "angle"])

class BotController:
    def __init__(self, controller_function):
        parser = ArgumentParser()
        parser.add_argument('-p','--port', help='The port that the controller will connect to.', type=int, required=True)
        parser.add_argument('-t','--trace', help='Enable line tracing for this controller.', action='store_true')
        args = parser.parse_args()
        self.bot_client = _BotClient(args.port)

        if args.trace: # Enable tracing.
            self.tracer_client = _TracerClient(5555)
            source_code = inspect.getsourcelines(inspect.getmodule(controller_function))[0]
            self.tracer_client.send_source(source_code)
            sys.settrace(lambda *_: (lambda frame, event, _: self.tracer_client.trace_lines(frame, event, inspect.getfile(controller_function))))

        self.wait() # Wait for the game to start.
        controller_function(self) # Run bot controller function.

    def get_health(self):
        """Gets the health of the bot.

        Returns:
            health (float): the current health of the bot between 0 and 100.
        """
        return self.bot_client.send_command(_Command.GetHealth)

    def get_energy(self):
        """Gets the energy of the bot.

        Returns:
            energy (float): the current energy of the bot between 0 and 1000.
        """
        return self.bot_client.send_command(_Command.GetEnergy)

    def get_position(self):
        """Gets the position of the bot.

        Returns:
            position (float, float): the 2D coordinates of the bot in world space.
        """
        return self.bot_client.send_command(_Command.GetPosition)

    def get_angle(self):
        """Gets the angle of the bot.

        Returns:
            angle (float): the angle of the bot in degrees, anti-clockwise relative to the x-axis.
        """
        return self.bot_client.send_command(_Command.GetAngle)

    def get_distances(self):
        """Gets readings from all distance sensors on the bot.

        Returns:
            distances (DistanceSensors): the readings from each distance sensor on the bot.
        """
        return DistanceSensors(*self.bot_client.send_command(_Command.GetDistances))

    def get_visible_objects(self):
        """Gets list of all objects visible to the bot.

        Returns:
            visible_objects (VisibleObjects): lists of all objects visible to the bot.
        """
        visible_objects = self.bot_client.send_command(_Command.GetVisibleObjects)
        bots = [VisibleBot(**x) for x in visible_objects["bots"]]
        energy_sources = [VisibleEnergySource(**x) for x in visible_objects["energy_sources"]]
        bullets = [VisibleBullet(**x) for x in visible_objects["bullets"]]
        return VisibleObjects(bots, energy_sources, bullets)

    def set_speed(self, speed):
        """Sets the desired speed of the bot.

        Args:
            speed (float): value between 0 (stopped) and 100 (maximum speed).
        """
        return self.bot_client.send_command(_Command.SetSpeed, speed)

    def set_angle(self, angle):
        """Sets the desired angle of the bot.

        Args:
            angle (float): the desired angle of the bot in degrees, anti-clockwise relative to the x-axis.
        """
        return self.bot_client.send_command(_Command.SetAngle, angle)

    def consume_energy(self):
        """Attempts to consume a nearby, active energy source.

        Returns:
            success (bool): a boolean value indicating whether the source was successfully consumed.
        """
        return self.bot_client.send_command(_Command.ConsumeEnergy)

    def shoot(self):
        """Attempts to shoot a bullet if the bot has enough energy.

        Returns:
            success (bool): a boolean value indicating whether the bullet was fired.
        """
        return self.bot_client.send_command(_Command.Shoot)

    def overcharge(self):
        """Attempts to activate an overcharge attack if the bot has enough energy.

        Returns:
            success (bool): a boolean value indicating whether the overcharge was successfully activated.
        """
        return self.bot_client.send_command(_Command.Overcharge)

    def wait(self):
        """Does nothing for one in-game tick.
        """
        return self.bot_client.send_command(_Command.Wait)
