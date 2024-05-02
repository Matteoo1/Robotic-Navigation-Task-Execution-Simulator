import time
import random
import dsim

USE_GUI = True
DYNAMIC_WORLD = False


class GUI:
    map = None
    robot = None

    def start(self):
        dsim.make_window()
        self.map = dsim.SimMap()
        self.robot = dsim.Robot()


# *************************************************
# - Class Map includes the attributes and functions
#       for defining the "map property of robot object".
# - "rooms", "nodes", and "doors" should be compatible
#       with variables in map.py.
# NOTE: the data-structure of variables in Map class are slightly
#       different than variables in map.py (compare "rooms",
#       "nodes", and "doors" in this class and map.py).
# *************************************************
class Map:
    rooms = {'room1': ['Bed'], 'room2': ['Stove'], 'room3': ['Table']}
    nodes = {'p1': 'room1', 'p2': 'room1', 'p3': 'room1',
            'p4': 'room2', 'p5': 'room2', 'p6': 'room2',
            'p7': 'room3', 'p8': 'room3', 'p9': 'room3'}
    arcs = {}
    # change the status of the doors from 'open' to 'closed' to test your planner for task 1.4
    doors = {'door1': ['p2', 'p8', 'close'],
            'door2': ['p6', 'p7', 'open'], 
            'door3': ['p3', 'p4', 'open']}
    boxes = {'box1': 'p4', 'box2': 'p9', 'box3': 'p1'}

    def __init__(self):
        self.make_graph()
        self.gui = GUI()
        if USE_GUI:
            # threading.Thread(target=self.start_gui).start()
            self.start_gui()
            for d in self.doors:
                if self.doors[d][2] == 'open':
                    self.gui.robot.open_door("open", d)
                else:
                    self.gui.robot.open_door("close", d)

    def start_gui(self):
        self.gui.start()

    def make_graph(self):
        for p in self.nodes:
            r = self.nodes[p]
            if p not in self.arcs:
                self.arcs[p] = []
            for q in self.nodes:
                if q != p and self.nodes[q] == r:
                    self.arcs[p].append(q)
            for d in self.doors:
                if self.doors[d][0] == p:
                    self.arcs[p].append(self.doors[d][1])
                if self.doors[d][1] == p:
                    self.arcs[p].append(self.doors[d][0])

    def reshuffle(self, probability=0.5):
        """
        Changes things in the world at random. For now, only the position of boxes.
        :param probability: probability that a change will occur
        """
        for b in self.boxes:
            if self.boxes[b] in self.nodes.keys():
                if random.random() > probability:
                    oldpos = self.boxes[b]
                    self.boxes[b] = random.choice(list(self.nodes.keys()))
                    print("* Reshuffling:", b, "moved from",
                          oldpos, "to", self.boxes[b])

    def print(self):
        print('-'.__mul__(30))
        print('{:<10}{}'.format('ROOM:', 'POINTS:'))
        for r in self.rooms:
            ps = []
            for p in self.nodes.keys():
                if self.nodes[p] == r:
                    ps.append(p)
            print('{:<10}'.format(r) + ', '.join([p for p in ps]))
        print('-'.__mul__(30))
        print('{:<10}{}'.format('DOOR:', 'STATUS:'))
        for d in self.doors:
            print('{:<10}'.format(d) + self.doors[d][2])
        print('-'.__mul__(30))
        print('{:<10}{}'.format('BOX:', 'LOCATION:'))
        for b in self.boxes:
            print('{:<10}'.format(b) + self.boxes[b])
        print('-'.__mul__(30))

# *************************************************
# Class Map includes the attributes and functions
#       for defining a robot instance/object.
# Note: an argument of the initialisation function is a "map object"
#       that is an instance of the Map class.
# *************************************************


class Robot:

    # Initializes the Robot instance with a name, map, and an optional starting position.
    def __init__(self, name, simmap, start='p1'):
        self.name = name
        self.map = simmap
        self.pos = start
        self.carry = None
        # self.drobot = dsim.Robot()

    # Creates a visual delay in the output to simulate suspense during operations
    def suspence(self, delay=5):
        for i in range(delay):
            print('.', end='', flush=True)
            time.sleep(0.2)
        print(" done")

    # Moves the robot to a new location if possible
    def moveto(self, newloc):
        if newloc in self.map.arcs[self.pos]:
            print("Moving from", self.pos, "to", newloc, end='')
            if USE_GUI:
                self.map.gui.robot.move_to(newloc)
            self.suspence()
            if DYNAMIC_WORLD:
                self.map.reshuffle()
            self.pos = newloc
            return True
        else:
            print("Cannot move from", self.pos, "to", newloc)
            return False


    # Crosses a specified door to a new location if possible
    def cross(self, door, newloc):
        if newloc in self.map.arcs[self.pos]:
            print("Crossing", door, "from", self.pos, "to", newloc, end='')
            if USE_GUI:
                self.map.gui.robot.move_to(newloc)
            self.suspence()
            self.pos = newloc
            return True
        else:
            print("Cannot cross", door, "from", self.pos, "to", newloc)
            return False

    # Opens a door
    def open(self, door):
        print("Opening", door, end='')
        if USE_GUI:
            self.map.gui.robot.open_door("open", door)
        self.suspence()
        self.map.doors[door][2] = 'open'
        return True

    # Closes a door
    def close(self, door):
        print("Closing", door, end='')
        if USE_GUI:
            self.map.gui.robot.open_door("close", door)
        self.suspence()
        self.map.doors[door][2] = 'closed'
        return True

    # Picks up a specified box if it is at the robot's current location
    def pickup(self, box):
        if self.pos == self.map.boxes[box]:
            print("Picking up", box, end='')
            self.suspence()
            self.carry = box
            self.map.boxes[box] = self.name
            return True
        else:
            print("Cannot pick up", box)
            return False


    # Puts down a box that the robot is carrying
    def putdown(self, box):
        if self.map.boxes[box] == self.name:
            print("Putting down", box, end='')
            self.suspence()
            self.carry = None
            self.map.boxes[box] = self.pos
            return True
        else:
            print("Cannot put down", box)
            return False

    # Returns the room the robot is currently in
    def in_room(self):
        return self.map.nodes[self.pos]

    # Perceives the environment of the room the robot is in
    def perceive(self):
        return self.map.rooms[self.in_room()]

    # Prints the current status of the robot including location and what it's carrying
    def print(self):
        print('-'.__mul__(30))
        print("ROBOT:", self.name, "at", self.pos, "carrying", self.carry)
        print('-'.__mul__(30))
