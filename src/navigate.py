
import pyhop
import map

class State(pyhop.State):
    def __init__(self):
        self.__name__ = "s1"
        self.pos = {}           # positions of me and boxes
        self.doors = {}         # doors' status: closed or open
        self.carry = None       # what boxes the me is carrying
        self.crossed = []       # list of doors tried so far during planning
        self.visited = []       # list of positions tried so far during planning


# Helper function to find an item in a list that matches a predicate
def some(predicate, candidates):
    for x in candidates:
        if predicate(x):
            return x
    return False


###############################################################################
# OPERATORS
# First argument is current state, others are the operator's parameters.
###############################################################################

def moveto(state, p):
    state.pos['me'] = p # Updates the position of 'me' to p
    return state


def cross(state, d, p):
    state.crossed.append(d) # Logs the crossing of a door
    state.pos['me'] = p      # Moves 'me' to position p after crossing a door
    return state

# Registering operators with the Pyhop planner
pyhop.declare_operators(moveto, cross)


# #################################################
# METHODS
# First argument is current state, others are the method's parameters.
# They may call other methods, or executable operators.
# #################################################

# Methods to move inside a room

def move_in_room_same_point(state, p):
    if state.pos['me'] == p:
        return []
    else:
        return False


def move_in_room_another_point(state, p):
    if map.room_of(state.pos['me']) == map.room_of(p):
        return [('moveto', p)]
    else:
        return False


pyhop.declare_methods('move_in_room', move_in_room_same_point, move_in_room_another_point)


# Methods to cross a door

############################
def cross_door_to_p2(state, d):
    p1, p2 = map.doors[d]
    if state.doors[d] == 'open' and state.pos['me'] == p1:
        return [('cross', d, p2)]
    return False


def cross_door_to_p1(state, d):
    p1, p2 = map.doors[d]
    if state.doors[d] == 'open' and state.pos['me'] == p2:
        return [('cross', d, p1)]
    return False


pyhop.declare_methods('cross_door', cross_door_to_p2, cross_door_to_p1)

def open(state, d):
    state.doors[d] = 'open'  # Marks the door as open in the state
    return state

def close(state, d):
    state.doors[d] = 'close'  # Marks the door as closed in the state
    return state


# Registers the 'open' and 'close' functions as Pyhop operators for modifying the state
pyhop.declare_operators(open, close)

# Method to handle the process of opening a door from one side
def openFirstDoor(state, d):
    p1, p2 = map.doors[d]
    if state.doors[d] == 'close' and state.pos['me'] == p1:
            return [('open', d), ('cross', d, p2), ('close', d)]
    return False


# Method to handle the process of opening a door from the opposite side
def openSecondDoor(state, d):
    p1, p2 = map.doors[d]
    if state.doors[d] == 'close' and state.pos['me'] == p2:
            return [('open', d), ('cross', d, p1), ('close', d)]
    return False

# Register methods for the 'open_door' task to handle both scenarios of door opening
pyhop.declare_methods('open_door', openFirstDoor, openSecondDoor)


def pickup(state, box):
    state.carry = box  # Updates the state to show that 'me' is carrying the box
    return state


def putdown(state, box):
    if state.carry == box:
        state.carry = None  # Clears the carried object from the state
        state.pos[box] = state.pos['me']  # Updates the box's location to 'me's current position
        return state
    else:
        return False  # Returns False if 'me' is not carrying the box

pyhop.declare_operators(pickup, putdown)


# Method to define how to fetch an object
def ToFetch(state, box):
    r = state.pos['me']
    r2 = state.pos[box]
    if(r != r2):
        return [('navigate_to', r2), ('pickup', box)]
    elif(r == r2):
        return [('pickup', box)]
    else:
        return False

pyhop.declare_methods('fetch', ToFetch)


# Method to define how to transport an object
def transportFunction(state, box, p1):
        # Various conditions to handle the state changes needed to transport a bo
    if(state.carry == box and p1 == state.pos['me']):
        return [('putdown', box)]
    elif(state.carry == box and p1 != state.pos['me']):
        return [('navigate_to', p1),('putdown', box)]
    elif(state.carry == None and state.pos[box]==state.pos['me'] and p1 != state.pos['me']):
        return [('pickup', box), ('navigate_to', p1),('putdown', box)]
    elif((state.carry == None and state.pos[box] != state.pos['me'] and p1 != state.pos['me'])):
        return [('navigate_to', state.pos[box]), ('pickup', box), ('navigate_to', p1),('putdown', box)]
    elif((state.carry == None and state.pos[box] != state.pos['me'] and p1 == state.pos['me'])):
        return [('navigate_to', state.pos[box]), ('pickup', box), ('navigate_to', p1),('putdown', box)]
    else:
        return False

pyhop.declare_methods('transport', transportFunction)



# Top level navigation methods

# Method for staying at the same position if already there
def navigate1(state, p):
    if p == state.pos['me']:
        return []
    else:
        return False


# Method for navigating within the same room
def navigate2(state, p):
    if map.room_of(p) == map.room_of(state.pos['me']):
        return [('move_in_room', p)]
    else:
        return False


# Method for navigating to a position in another room through a door
def navigate3(state, p):
    r = map.room_of(state.pos['me'])
    d = some(lambda x: x not in state.crossed, map.doors_of(r))
    if d:
        state.crossed.append(d)
        p2 = map.side_of(d, r)
        if state.doors[d] == 'close':
            return [('move_in_room', p2), ('open_door', d), ('navigate_to', p)]
        else:
            return [('move_in_room', p2), ('cross_door', d), ('navigate_to', p)]
    else:
        return False


def navigate4(state, p):
    if p not in state.visited:
        state.visited.append(p)
        return [('navigate_to', p)]
    else:
        return False


pyhop.declare_methods('navigate_to', navigate1, navigate2, navigate3, navigate4)

