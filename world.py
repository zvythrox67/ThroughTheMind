WOOD = (222, 160, 140)
WOOD_DK = (176, 112, 120)
PINK = (251, 107, 162)
CORAL = (255, 152, 154)
LAV = (142, 105, 230)
LAV_LT = (190, 160, 245)
BLUE = (86, 97, 211)
YELLOW = (250, 229, 114)
CREAM = (255, 243, 196)
GREEN = (120, 222, 178)
GRAY = (196, 190, 230)


class Obj:
    def __init__(self, label, action, x, y, w, h, color, kind="box", deco=False, exit=False, npcs=None):
        self.label, self.action = label, action
        self.x, self.y, self.w, self.h = x, y, w, h
        self.color = color
        self.kind = kind
        self.deco, self.exit = deco, exit
        self.npcs = npcs or [] 
        self.to = None
        self.via = None
        self.minutes = 0
        self.sx = self.sy = 0

    @staticmethod
    def exit_to(label, to, minutes, sx, sy, x, y, w, h):
        o = Obj(label, None, x, y, w, h, (150, 100, 90), kind="door", exit=True)
        o.to, o.minutes, o.sx, o.sy = to, minutes, sx, sy
        return o

    @staticmethod
    def travel(to, minutes, sx, sy, via=None):
        o = Obj.exit_to("", to, minutes, sx, sy, 0, 0, 0, 0)
        o.via = via
        return o

    def dist(self, px, py):
        cx = max(self.x, min(px, self.x + self.w))
        cy = max(self.y, min(py, self.y + self.h))
        return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5


class Room:
    def __init__(self, rid, name, floor, wall, crowd, outdoor=False, decor=""):
        self.id, self.name, self.floor, self.wall, self.crowd = rid, name, floor, wall, crowd
        self.outdoor, self.decor = outdoor, decor
        self.objs = []

    def add(self, label, action, x, y, w, h, color, kind="box", npcs=None):
        self.objs.append(Obj(label, action, x, y, w, h, color, kind, npcs=npcs))

    def deco(self, label, x, y, w, h, color, kind="box"):
        self.objs.append(Obj(label, None, x, y, w, h, color, kind, deco=True))

    def door(self, label, to, minutes, sx, sy, x, y, w, h):
        self.objs.append(Obj.exit_to(label, to, minutes, sx, sy, x, y, w, h))


ROOMS = {}


def _room(rid, name, floor, wall, crowd, outdoor=False, decor=""):
    r = Room(rid, name, floor, wall, crowd, outdoor, decor)
    ROOMS[rid] = r
    return r


def crowd_of(rid):
    if rid == "bus":
        return 2
    r = ROOMS.get(rid)
    return r.crowd if r else 0


def _build():
    h = _room("home", "Home", ((90, 63, 143), (82, 56, 132)), (59, 42, 110), 0, decor="home")
    h.add("Bed", "bed", 60, 440, 200, 110, PINK, "bed")
    h.add("Kitchen table", "breakfast", 360, 200, 200, 80, CORAL, "table")
    h.add("Family", "family", 610, 215, 70, 60, LAV_LT, "sofa")
    h.add("Desk", "homework", 800, 200, 170, 80, WOOD, "desk")
    h.door("Front door", "bus_stop", 10, 110, 420, 930, 430, 70, 120)

    b = _room("bus_stop", "Bus stop", ((58, 47, 125), (52, 41, 116)), None, 2, outdoor=True)
    b.deco("Bench", 420, 230, 180, 45, WOOD, "bench")
    b.add("Classmates", "classmates", 620, 320, 110, 30, LAV, "npcs", npcs=[("asher", 28, 30), ("lamar", 84, 30)])
    b.add("School bus", "bus", 780, 190, 200, 110, YELLOW, "bus")
    b.door("Walk home", "home", 10, 880, 470, 40, 440, 80, 120)
    b.door("Coffee shop", "coffee", 3, 512, 430, 430, 520, 140, 70)

    hl = _room("hall", "School hallway", ((106, 95, 179), (98, 87, 170)), (74, 63, 143), 3, decor="hall")
    hl.deco("Bench", 300, 390, 140, 40, WOOD, "bench")
    hl.deco("Bench", 650, 390, 140, 40, WOOD, "bench")
    hl.door("Front doors (bus stop)", "bus_stop", 5, 800, 400, 30, 300, 60, 130)
    hl.door("Classroom", "classroom", 2, 200, 540, 300, 100, 130, 90)
    hl.door("Bathroom", "bathroom", 2, 200, 540, 480, 100, 130, 90)
    hl.door("Guidance room", "guidance", 2, 200, 540, 680, 100, 130, 90)
    hl.door("Lunchroom", "lunchroom", 2, 520, 260, 450, 545, 150, 70)

    c = _room("classroom", "Classroom", ((122, 99, 192), (114, 91, 184)), (82, 65, 143), 2, decor="classroom")
    c.deco("Whiteboard", 330, 100, 360, 45, CREAM, "whiteboard")
    c.add("Teacher", "teacher", 280, 215, 70, 40, BLUE, "npcs", npcs=[("teacher", 35, 40)])
    c.add("Your desk", "class_desk", 430, 330, 110, 60, WOOD, "desk")
    c.add("Group table", "group", 700, 300, 170, 100, CORAL, "table", npcs=[("noah", 52, 8), ("estella", 120, 8)])
    c.deco("Desk", 300, 440, 110, 50, WOOD, "desk")
    c.deco("Desk", 560, 440, 110, 50, WOOD, "desk")
    c.door("Door (hallway)", "hall", 2, 360, 260, 50, 500, 60, 100)

    t = _room("bathroom", "Bathroom", ((127, 143, 224), (117, 133, 216)), (87, 102, 196), 0, decor="bathroom")
    t.deco("Sinks", 400, 110, 140, 50, CREAM, "sinks")
    t.add("Stall (breathe)", "stall", 760, 200, 150, 190, GRAY, "stall")
    t.door("Door (hallway)", "hall", 2, 545, 260, 50, 500, 60, 100)

    l = _room("lunchroom", "Lunchroom", ((140, 107, 208), (132, 99, 200)), (91, 68, 154), 3, decor="lunch")
    l.add("Lunch line", "lunch", 300, 200, 200, 70, WOOD, "counter")
    l.add("Friends' table", "friends", 540, 330, 200, 100, CORAL, "table", npcs=[("anika", 60, 8), ("estella", 140, 8)])
    l.deco("Table", 280, 430, 170, 70, CORAL, "table")
    l.deco("Table", 800, 230, 160, 80, CORAL, "table")
    l.deco("Table", 800, 440, 160, 80, CORAL, "table")
    l.door("Door (hallway)", "hall", 2, 525, 480, 450, 100, 140, 90)

    g = _room("guidance", "Guidance room", ((145, 112, 214), (137, 104, 206)), (96, 72, 160), 0, decor="guidance")
    g.deco("Couch", 300, 230, 160, 80, PINK, "sofa")
    g.add("Counselor", "counselor", 550, 235, 80, 60, GREEN, "npcs", npcs=[("counselor", 40, 60)])
    g.deco("Desk", 510, 305, 160, 45, WOOD, "desk")
    g.door("Door (hallway)", "hall", 2, 745, 260, 50, 500, 60, 100)

    k = _room("coffee", "Coffee shop", ((106, 74, 140), (95, 65, 128)), (61, 42, 95), 1, decor="coffee")
    k.add("Counter", "coffee", 380, 210, 260, 70, WOOD, "counter", npcs=[("barista", 130, 18)])
    k.deco("Table", 150, 380, 120, 60, CORAL, "table")
    k.deco("Table", 750, 380, 120, 60, CORAL, "table")
    k.door("Door (bus stop)", "bus_stop", 3, 500, 470, 430, 545, 160, 70)


_build()