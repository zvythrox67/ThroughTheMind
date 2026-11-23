import random

TOTAL_LEVELS = 5
WAKE = 6 * 60 + 30
CLASS_START = 8 * 60 + 30
LATE_CUTOFF = 9 * 60 + 30
LUNCH_OPENS = 11 * 60 + 30
AFTERNOON = 13 * 60
BEDTIME_OPENS = 19 * 60
FORCED = 24 * 60 - 1
ENERGY_DRAIN = 0.05

TASKS = {
    "on_time": "Get to class by 8:30",
    "morning_class": "Do your morning classwork",
    "lunch": "Eat lunch",
    "afternoon_class": "Do your afternoon classwork",
    "family": "Spend time with family",
    "homework": "Do your homework",
}

LEVELS = [
    {"name": "A Normal Day", "sev": 0.7,
     "blurb": "Worry hums in the background all day. Your body can't quite relax.",
     "new": ["Muscle tension: shoulders up, jaw clenched", "Constant low worry that drains your energy"]},
    {"name": "The What-Ifs", "sev": 0.95,
     "blurb": "Small choices start to feel risky. Your mind runs every worst case.",
     "new": ["Racing 'what if' thoughts", "Decision paralysis: choices cost time", "Reassurance seeking"]},
    {"name": "Under Pressure", "sev": 1.2,
     "blurb": "A presentation today. Your heart races and your hands shake.",
     "new": ["Shaky hands and a pounding heart", "Irritability: you snap at people you love", "Restless, light sleep"]},
    {"name": "Tunnel Vision", "sev": 1.5,
     "blurb": "The world narrows. Crowds feel unbearable and panic can hit with no warning.",
     "new": ["Panic attacks", "Dizziness and tunnel vision", "Avoidance: you want to stay away from crowds"]},
    {"name": "The Big Test", "sev": 1.8,
     "blurb": "Exam day. Everything at once. Use everything you've learned.",
     "new": ["Constant dread", "Frequent panic attacks", "Exhaustion"]},
]

WIN = {"grades": 75, "attendance": 75, "happiness": 75, "stress_max": 35,
       "attentiveness": 70, "energy": 70, "health": 70, "relationships": 60}

THOUGHTS = ["What if I failed that?", "What if everyone is mad at me?", "Did I lock the door?",
            "What if something goes wrong?", "Everyone can tell I'm nervous."]

INTRO = [
    "Miku is a high school student living with generalized anxiety disorder (GAD): constant, "
    "hard-to-control worry about everyday things, even when nothing is wrong.",
    "Your body can't relax. Your shoulders creep up toward your ears, your jaw clenches, your neck "
    "locks. Simple decisions feel impossible because you calculate every risk. You keep seeking "
    "reassurance, and worrying burns through your energy.\n\nAnd it gets harder. Each level, the symptoms get stronger.",
]

COUNSELOR = [
    "\"Thank you for telling me. What you describe sounds like generalized anxiety. It's very common "
    "and very treatable. Your brain is sounding an alarm that doesn't need to go off.\"",
    "\"Slow breathing tells your body it's safe. And try a 'worry time': write worries down and give "
    "them 10 minutes later in the day.\"",
    "\"Therapy, especially CBT, helps a lot with anxiety, and sometimes medication can too. Let's talk "
    "with your parents about finding a specialist.\"",
    "\"You're learning to notice worry without obeying it. That's real progress.\"",
]


def clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


def fmt_time(m):
    h = (m // 60) % 24
    mm = m % 60
    h12 = 12 if h % 12 == 0 else h % 12
    return "%d:%02d %s" % (h12, mm, "AM" if h < 12 else "PM")


class Dialogue:
    """One dialogue box. Dialogue("text") or Dialogue("Speaker", "text")."""

    def __init__(self, a, b=None):
        if b is None:
            self.speaker, self.text = "", a
        else:
            self.speaker, self.text = a, b
        self.choices = []
        self.on_close = None

    def choice(self, label, fn=None):
        self.choices.append((label, fn))
        return self

    def then(self, fn):
        self.on_close = fn
        return self


class Game:
    def __init__(self):
        self.ui = None
        self.rng = random.Random()
        self.st = {"happiness": 55.0, "stress": 45.0, "attentiveness": 65.0, "energy": 70.0, "health": 70.0}
        self.rel = {"family": 50.0, "friends": 45.0, "teachers": 50.0, "classmates": 40.0}
        self.grades = 68.0
        self.attendance_pts = 0.0
        self.levels_done = 0
        self.level = 1
        self.minutes = WAKE
        self.room = "home"
        self.counsel_visits = 0
        self.tasks = {k: False for k in TASKS}
        self.seen = set()
        self.worry = 40.0
        self.skill = 0.0
        self.reassures = 0
        self.thought_timer = 0.0
        self.sleep_mult = 1.0
        self.panics = 0
        self.day_over = False
        self.reset_flags()

    def reset_flags(self):
        self.arrival = "none"
        self.breakfast = self.family_done = self.homework = False
        self.morning_done = self.afternoon_done = self.lunch_done = self.group_done = False
        self.counseled = self.teacher_done = self.left_early = self.forced = False
        self.stall_count = 0
        self.sleep_mult = 1.0
        self.panics = 0

    def sev(self):
        return LEVELS[self.level - 1]["sev"]

    def level_info(self):
        return LEVELS[self.level - 1]

    def get(self, s):
        return self.st[s]

    def modify(self, stat, d):
        if d > 0 and stat == "stress":
            return d * (1 + 0.4 * self.worry / 100) * (0.85 + 0.15 * self.sev())
        return d

    def change(self, s, d):
        self.raw(s, self.modify(s, d))

    def raw(self, s, d):
        b = self.st[s]
        a = clamp(b + d)
        self.st[s] = a
        if self.ui and abs(a - b) >= 2:
            good = (a - b < 0) if s == "stress" else (a - b > 0)
            self.ui.toast("%s %+d" % (s.capitalize(), round(a - b)), good)

    def quiet(self, s, d):
        self.st[s] = clamp(self.st[s] + d)

    def relate(self, who, d):
        b = self.rel[who]
        a = clamp(b + d)
        self.rel[who] = a
        if self.ui and abs(a - b) >= 1:
            self.ui.toast("%s %+d" % (who.capitalize(), round(a - b)), a > b)

    def add_worry(self, d):
        self.worry = clamp(self.worry + d)

    def study(self, q):
        gain = (100 - self.grades) * 0.04 * q
        self.grades = clamp(self.grades + gain)
        if self.ui and abs(gain) >= 0.4:
            self.ui.toast("Grades %+.1f" % gain, gain > 0)

    def mark(self, task):
        self.tasks[task] = True

    def thought(self, t):
        if self.ui:
            self.ui.thought(t)

    def once(self, key):
        k = "%d:%s" % (self.level, key)
        if k in self.seen:
            return False
        self.seen.add(k)
        return True

    def rel_avg(self):
        return sum(self.rel.values()) / len(self.rel)

    def attendance(self):
        return 100.0 if self.levels_done == 0 else 100.0 * self.attendance_pts / self.levels_done

    def time(self):
        return fmt_time(self.minutes)

    def social(self):
        self.raw("energy", -3)
        if self.level >= 3 and self.get("stress") > 55:
            self.relate("friends", -1.5 * (self.sev() - 0.9))

    def study_quality(self):
        return 1 - 0.2 * self.worry / 100

    def crowd(self, room):
        from world import crowd_of
        return crowd_of(room)

    def advance(self, mins):
        mins = int(mins)
        sev = self.sev()
        self.minutes += mins
        crowd = self.crowd(self.room)
        self.add_worry(mins * (0.03 + 0.007 * crowd) * sev)
        self.quiet("stress", mins * 0.03 * self.worry / 100 * sev)
        self.quiet("energy", -mins * 0.02 * self.worry / 100 * sev)
        self.thought_timer += mins
        if self.thought_timer >= 60 / sev:
            self.thought_timer = 0
            self.thought(self.rng.choice(THOUGHTS))
        self.raw("energy", -mins * ENERGY_DRAIN * (0.9 + 0.1 * sev))
        self.quiet("stress", mins * 0.01 * crowd if crowd > 0 else -mins * 0.012)
        self.quiet("happiness", -mins * 0.018)
        self.maybe_panic(mins)
        if self.minutes >= FORCED and not self.forced and not self.day_over:
            self.forced = True
            self.say(Dialogue("You can barely keep your eyes open. You fall asleep before you know it.")
                     .then(lambda: self.end_day(True)))

    def maybe_panic(self, mins):
        if self.level < 4 or self.panics >= self.level - 2 or self.day_over:
            return
        if self.crowd(self.room) < 2 or self.worry < 55:
            return
        rate = 0.30 if self.level == 4 else 0.55
        if self.rng.random() < rate * mins / 60.0:
            self.panic()

    def panic(self):
        self.panics += 1
        self.ui.panic_fx(9.0)

        def breathe():
            self.ui.minigame("breathing", {"panic": True, "sev": self.sev()}, self.done_panic)

        def push():
            self.advance(5)
            self.raw("stress", 12)
            self.raw("energy", -10)
            self.raw("attentiveness", -10)
            self.add_worry(6)
            self.say(Dialogue("You grit your teeth and keep going. The attack fades slowly, but you feel wrung out."))

        def hide():
            self.advance(20)
            self.add_worry(3)
            self.quiet("stress", -4)
            self.relate("teachers", -1)
            self.say(Dialogue("You find somewhere quiet and wait for it to pass. It helps, but avoiding things makes the fear grow."))
        self.say(Dialogue("PANIC", "Without warning, your heart starts pounding. Your chest is tight, you can't get enough air, "
                                   "your hands go numb and shaky, and the room spins. It feels like something terrible is about to happen.")
                 .choice("Ride it out with slow breathing", breathe)
                 .choice("Push through and keep going", push)
                 .choice("Hide until it passes (20 min)", hide))

    def done_panic(self, r):
        s = r["score"]
        self.advance(10)
        self.add_worry(-(10 + 3 * s))
        self.raw("stress", -(6 + 2 * s))
        self.skill = clamp(self.skill + 6 + 2 * s)
        self.ui.panic_fx(0)
        self.say(Dialogue("Slow breath in, slow breath out. The wave peaks and then it starts to fall. Panic always passes, even when it doesn't feel like it will."
                          if s >= 3 else "It's hard to catch your breath, but the wave finally passes. Practicing the breathing makes it easier next time."))

    def start_level(self):
        self.minutes = WAKE
        self.room = "home"
        self.day_over = False
        self.reset_flags()
        self.tasks = {k: False for k in TASKS}
        self.worry = max(22 * self.sev(), self.worry * 0.8)
        self.reassures = 0

    def morning(self):
        t = ("Your alarm goes off at 6:30. You've been rehearsing what could go wrong today since before you woke up. "
             "School starts at 8:30, and getting there takes about 30 minutes (10 to the bus stop, 20 on the bus).")
        if self.level == 3:
            t += "\n\nToday your group presents to the class."
        if self.level == 5:
            t += "\n\nToday is the big exam."
        return Dialogue("Level %d" % self.level, t)

    def end_day(self, was_forced=False):
        if self.day_over:
            return
        self.day_over = True
        pts = {"on_time": 1.0, "late": 0.6}.get(self.arrival, 0.3 if (self.arrival == "missed" and self.afternoon_done) else 0.0)
        if self.arrival in ("on_time", "late") and not self.afternoon_done:
            pts = max(0.0, pts - 0.4)
        self.attendance_pts += pts
        self.levels_done += 1
        if pts == 0:
            self.grades = max(0.0, self.grades - 4)
        bed = self.minutes
        if self.level >= TOTAL_LEVELS:
            self.finish()
            return
        late = was_forced or bed > 22 * 60 + 30
        quality = (1 - 0.25 * self.worry / 100) * self.sleep_mult
        self.quiet("energy", (38 if late else 52) * quality)
        self.quiet("stress", -22)
        self.quiet("attentiveness", 14)
        self.quiet("health", 2)
        self.worry = clamp(self.worry - 8 * (self.sleep_mult - 0.6) / 0.4)
        done = sum(1 for v in self.tasks.values() if v)
        names = {"on_time": "On time", "late": "Late", "missed": "Missed the morning", "none": "Didn't go to school"}
        lines = ["Arrival: " + names[self.arrival], "Bedtime: " + fmt_time(bed), ""]
        for k, label in TASKS.items():
            lines.append(("[x] " if self.tasks[k] else "[ ] ") + label)
        lines.append("")
        lines.append("Tasks %d/%d    Grades %d%%    Attendance %d%%" % (done, len(TASKS), round(self.grades), round(self.attendance())))
        lines.append("Stress %d%%    Worry %d%%    Panic attacks %d" % (round(self.st["stress"]), round(self.worry), self.panics))
        lines.append("")
        nxt_info = LEVELS[self.level]
        lines.append("Next: Level %d, \"%s\". The symptoms get stronger." % (self.level + 1, nxt_info["name"]))

        def nxt():
            self.level += 1
            self.start_level()
            self.ui.new_level()
        self.ui.summary("Level %d complete" % self.level, "\n".join(lines), [("Level %d" % (self.level + 1), nxt)])

    def finish(self):
        rows = [("Grades", self.grades, WIN["grades"], True), ("Attendance", self.attendance(), WIN["attendance"], True),
                ("Happiness", self.st["happiness"], WIN["happiness"], True), ("Stress", self.st["stress"], WIN["stress_max"], False),
                ("Attentiveness", self.st["attentiveness"], WIN["attentiveness"], True), ("Energy", self.st["energy"], WIN["energy"], True),
                ("Health", self.st["health"], WIN["health"], True), ("Relationships", self.rel_avg(), WIN["relationships"], True)]
        won = True
        lines = []
        for name, val, goal, high in rows:
            ok = val >= goal if high else val <= goal
            won = won and ok
            lines.append("%s %s: %d%%  (goal %s %d%%)" % ("[x]" if ok else "[ ]", name, round(val), ">=" if high else "<=", goal))
        lines.append("")
        if won:
            lines.append("You made it through all five levels. Not by being \"fixed\", but by finding support and facing "
                         "worries instead of only avoiding them.")
        else:
            lines.append("These five levels were hard, and that is the point. Generalized anxiety disorder is a real condition, "
                         "not a lack of willpower, and support from a counselor, therapist or doctor makes a big "
                         "difference. Try again and see what changes.")
        lines.append("")
        lines.append("If you or someone you know is struggling, talk to a trusted adult, a school counselor or a "
                     "doctor. In the US, call or text 988 anytime.")
        self.ui.summary("You made it" if won else "End of the line", "\n".join(lines),
                        [("Main menu", self.ui.exit_to_menu)])

    def say(self, d):
        if d.choices:
            self.on_decision(d)
        self.ui.say(d)

    def on_decision(self, d):
        if self.level >= 2 and self.worry > 35 and "weighing every" not in d.text:
            self.advance(int(round(4 * self.sev())))
            self.quiet("stress", 2)
            d.text += "\n\n(You spend a few minutes weighing every way this could go wrong before you can choose.)"

    def act(self, action):
        fn = getattr(self, "a_" + action, None)
        if fn:
            d = fn()
            if d is not None:
                self.say(d)

    def a_breakfast(self):
        if self.breakfast:
            return Dialogue("You've already eaten.")

        def sit():
            self.breakfast = True
            self.advance(15)
            self.raw("energy", 12)
            self.change("happiness", 3)
            self.relate("family", 3)
            self.social()
            self.say(Dialogue("You sit and eat. Your mind keeps running through the day, but the table is warm."))

        def go():
            self.breakfast = True
            self.advance(3)
            self.raw("energy", 6)
            self.say(Dialogue("You grab something and head for the door."))
        return (Dialogue("Kitchen", "Mom and Dad are at the table. You catch yourself rehearsing everything that could go wrong today.")
                .choice("Sit and eat with the family (15 min)", sit).choice("Grab something and go (3 min)", go))

    def a_family(self):
        if self.family_done:
            return Dialogue("You've already spent time with your family today.")
        d = Dialogue("Family", "Your family is gathered in the living room.")

        def join():
            self.family_done = True
            self.advance(25)
            self.mark("family")
            self.relate("family", 6)
            self.change("happiness", 4)
            self.social()
            self.say(Dialogue("You spend some time together. Talking about small things helps your shoulders drop a little."))

        def ask():
            self.family_done = True
            self.advance(25)
            self.mark("family")
            self.reassures += 1
            self.add_worry(-5)
            if self.reassures >= 2:
                self.relate("family", -2)
                self.say(Dialogue("Mom", "\"Sweetheart, we've gone over this. It'll be fine.\" You feel a flash of irritation "
                                         "at yourself, and at the question you can't stop asking."))
            else:
                self.relate("family", 2)
                self.say(Dialogue("Mom", "\"You'll do great.\" It helps for a few minutes, then the doubt creeps back."))

        def avoid():
            self.family_done = True
            self.relate("family", -3)
            self.quiet("stress", -2)
            self.say(Dialogue("Being alone feels easier, but also lonelier. You can hear them laughing in the other room."))
        return (d.choice("Join them (25 min)", join)
                .choice("Ask: \"Are you sure everything will be okay?\" (25 min)", ask)
                .choice("Say you're tired and go to your room", avoid))

    def a_homework(self):
        if self.homework:
            return Dialogue("Your homework is done for tonight.")
        if self.arrival == "none" and self.minutes < CLASS_START + 240:
            return Dialogue("You should head to school first.")

        def start():
            self.ui.minigame("check", {"worry": self.worry, "sev": self.sev()}, self.done_homework)
        return Dialogue("Desk", "Time to get your homework done.").choice("Start", start).choice("Not yet")

    def done_homework(self, r):
        rechecks, trusted, correct = r["rechecks"], r["trusted"], r["correct"]
        self.advance(50 + 6 * rechecks)
        self.homework = True
        self.mark("homework")
        base = max(0.3, min(1.0, (self.get("attentiveness") + self.get("energy")) / 200))
        self.study(base * self.study_quality() * (0.4 + 0.6 * correct / 5.0))
        self.add_worry(0.8 * rechecks - 1.5 * trusted)
        self.raw("stress", rechecks * 1.0)
        self.raw("attentiveness", -3)
        if rechecks >= 4:
            t = "You checked and re-checked until the answers stopped looking like words. It took far longer than it needed to."
        elif trusted >= 3:
            t = "You made yourself move on, even with the 'what if it's wrong?' feeling. And the world didn't end."
        else:
            t = "You got through it, one worry at a time."
        self.say(Dialogue(t))

    def a_bed(self):
        if self.minutes < BEDTIME_OPENS:
            def rest():
                self.advance(60)
                self.raw("energy", 6)
                self.add_worry(3)
                self.say(Dialogue("You lie on top of the covers. You can't really nap, and your mind drifts to tomorrow. But your body gets a little rest."))
            return (Dialogue("Bed", "It's too early to sleep (after 7 PM). You could lie down and rest for a while.")
                    .choice("Rest for an hour (60 min)", rest).choice("Not yet"))

        def sleep():
            if self.level >= TOTAL_LEVELS:
                self.end_day(False)
            else:
                self.ui.minigame("sleep", {"worry": self.worry, "sev": self.sev()}, self.done_sleep)
        return Dialogue("Bed", "Go to sleep? This ends the level.").choice("Yes, sleep", sleep).choice("Not yet")

    def done_sleep(self, r):
        self.sleep_mult = 0.6 + 0.4 * r["score"]
        self.end_day(False)

    def a_classmates(self):
        def hi():
            self.advance(5)
            self.relate("classmates", 3)
            self.change("stress", 4)
            self.social()
            self.say(Dialogue("Asher", "\"Hey.\" Lamar nods at you. It's a little awkward, but it's okay."))

        def phones():
            self.quiet("stress", -1)
            self.say(Dialogue("The music helps. It's quiet inside your head, but you feel apart from everyone."))
        return (Dialogue("Asher & Lamar", "Two kids from your grade are chatting by the bench.")
                .choice("Say hi (5 min)", hi).choice("Put your headphones in", phones))

    def a_bus(self):
        from world import Obj
        self.ui.travel(Obj.travel("hall", 20, 170, 380, "bus"))

    def a_class_desk(self):
        if not self.morning_done:
            self.start_class(True)
        elif not self.afternoon_done:
            if not self.lunch_done and self.minutes < AFTERNOON:
                return Dialogue("Morning class is over. It's time for lunch.")
            if self.minutes < AFTERNOON:
                self.advance(AFTERNOON - self.minutes)
            self.start_class(False)
        else:
            return Dialogue("Class is over for the day. Head home whenever you're ready.")

    def start_class(self, morning):
        if morning and self.minutes < CLASS_START:
            self.advance(CLASS_START - self.minutes)
        self.ui.minigame("focus", {"worry": self.worry, "sev": self.sev(), "exam": self.level == 5 and morning},
                         lambda r: self.done_class(morning, r))

    def done_class(self, morning, r):
        self.advance(90 if morning else 75)
        score, hits = r["score"], r["hits"]
        q = max(0.3, min(1.0, (self.get("attentiveness") + self.get("energy")) / 200))
        q = (0.25 + 0.9 * score) * q * self.study_quality()
        if self.get("stress") > 65:
            q *= 0.8
        self.study(q)
        self.raw("attentiveness", -2 - hits * 0.5)
        self.add_worry(hits * 1.0)
        if morning:
            self.morning_done = True
            self.mark("morning_class")
        else:
            self.afternoon_done = True
            self.mark("afternoon_class")
        if score >= 0.7:
            t = "You kept your focus on the lesson and let the 'what ifs' drift past."
        elif score >= 0.4:
            t = "Your mind kept getting pulled away, but you caught enough to follow along."
        else:
            t = "Worries crowded out the lesson. You hardly took in anything. Your jaw is clenched and your shoulders are up around your ears."
        self.say(Dialogue(t))

    def a_group(self):
        if self.arrival == "none":
            return None
        if not self.morning_done:
            return Dialogue("Group work starts after the morning lesson.")
        if self.group_done:
            return Dialogue("Group work is finished for today.")
        intro = ("Today your group presents to the class. Everyone's attention is pointed at you."
                 if self.level == 3 else "Noah and Estella are waiting for you at the table.")

        def speak():
            self.ui.minigame("voice", {"worry": self.worry, "sev": self.sev(), "presenting": self.level == 3}, self.done_voice)

        def hold():
            self.group_done = True
            self.advance(40)
            self.change("stress", 3)
            self.study(0.4)
            self.relate("classmates", -2)
            self.say(Dialogue("You get through it quietly, but Noah and Estella end up finishing your part for you."))

        def skip():
            self.group_done = True
            self.advance(15)
            self.quiet("stress", -5)
            self.relate("teachers", -2)
            self.relate("classmates", -3)
            self.say(Dialogue("Leaving is a relief right away. But your group notices, and so does your teacher."))
        return (Dialogue("Group work", intro).choice("Speak up and share your part", speak)
                .choice("Hold back and let others lead (40 min)", hold).choice("Say you feel sick and leave", skip))

    def done_voice(self, r):
        s = r["score"]
        self.group_done = True
        self.advance(40)
        self.change("stress", (16 + (4 if self.level == 3 else 0)) * (1 - 0.6 * s))
        self.study(0.3 + 0.7 * s)
        self.relate("classmates", 1 + 4 * s)
        if s >= 0.6:
            self.add_worry(-6)
            t = "Your voice wobbled at first, but you kept going. People were focused on the work, not on you. Facing it made it a little less scary."
        else:
            self.add_worry(2)
            t = "Your voice shook and your hands trembled. You got through it, but it felt like everyone noticed."
        self.say(Dialogue(t))

    def a_teacher(self):
        if self.teacher_done:
            return Dialogue("Ms. Park", "\"Let me know if you need anything else.\"")

        def ask():
            self.teacher_done = True
            self.advance(10)
            self.relate("teachers", 3)
            self.study(0.5)
            self.raw("attentiveness", 2)
            self.say(Dialogue("Ms. Park", "\"Good question. Here's what I'd do...\" Her answer clears up what you were stuck on."))
        return Dialogue("Ms. Park", "\"How's the assignment going?\"").choice("Ask a question (10 min)", ask).choice("\"I'm fine.\"")

    def a_stall(self):
        self.stall_count += 1
        self.ui.minigame("breathing", {"sev": self.sev()}, self.done_breathing)

    def done_breathing(self, r):
        score = r["score"]
        self.advance(10)
        self.skill = clamp(self.skill + 8 + score * 2)
        self.add_worry(-(6 + score * 3))
        self.raw("stress", -(4 + score * 2))
        if score >= 3:
            t = "Your breathing slows and your shoulders drop. Your body starts to believe it's safe."
        else:
            t = "It's hard to settle, but slow breathing gets easier with practice."
        self.say(Dialogue(t))

    def a_lunch(self):
        if self.lunch_done:
            return Dialogue("You've already had lunch.")
        if self.minutes < LUNCH_OPENS:
            self.advance(LUNCH_OPENS - self.minutes)
        self.ui.minigame("decision", {"worry": self.worry, "sev": self.sev()}, self.done_lunch)

    def done_lunch(self, r):
        choice, spiral = r["choice"], r["spiral"]
        self.lunch_done = True
        self.advance(int(12 * spiral))
        self.raw("stress", 6 * spiral)
        self.add_worry(4 * spiral - (3 if spiral < 0.5 else 0))
        if choice == 0:
            self.advance(30)
            self.mark("lunch")
            self.raw("energy", 16)
            self.raw("health", 3)
            self.relate("friends", 4)
            self.change("happiness", 4)
            self.social()
            t = "You sit with Anika. She tells a story that makes you laugh, and for a few minutes you forget about everything else."
        elif choice == 1:
            self.advance(30)
            self.mark("lunch")
            self.raw("energy", 16)
            self.raw("health", 3)
            self.quiet("stress", -2)
            self.relate("friends", -2)
            t = "It's quieter here. Across the room, Anika looks over and wonders where you went."
        else:
            self.advance(10)
            self.raw("health", -3)
            self.raw("energy", -4)
            self.relate("friends", -1)
            t = "You couldn't decide, and the bell rang. Your stomach disagrees with how you spent lunch."
        self.say(Dialogue(t))

    def a_friends(self):
        def chat():
            self.advance(10)
            self.relate("friends", 5)
            self.change("happiness", 3)
            self.change("stress", 1)
            self.social()
            self.say(Dialogue("You talk about a show you both like. It's an easy conversation."))

        def open_up():
            self.advance(20)
            self.relate("friends", 5)
            self.raw("stress", -6)
            self.change("happiness", 4)
            self.add_worry(-6)
            self.social()
            self.say(Dialogue("Anika listens without trying to fix anything. Saying it out loud makes it feel a little lighter."))

        def validate():
            self.advance(5)
            self.reassures += 1
            self.add_worry(-8)
            if self.reassures >= 2:
                self.relate("friends", -3)
                self.say(Dialogue("Anika", "\"I already said it's fine!\" She sounds irritated, and you feel the worry come right back."))
            else:
                self.raw("stress", -4)
                self.say(Dialogue("Anika", "\"Of course not!\" You feel better for about a minute, then the doubt creeps back."))
        return (Dialogue("Anika", "\"Hey! Sit with us.\"")
                .choice("Talk about something else (10 min)", chat)
                .choice("Open up about how anxious you've been (20 min)", open_up)
                .choice("Ask: \"Are you SURE you're not mad at me?\" (5 min)", validate))

    def a_counselor(self):
        if self.counseled:
            return Dialogue("Ms. Rivera", "\"I have another student coming in. Come back tomorrow, okay? I'm glad you came.\"")
        if self.arrival == "none":
            return Dialogue("You should get to class first.")

        def talk():
            self.ui.minigame("sort", {"sev": self.sev()}, self.done_counsel)
        return (Dialogue("Ms. Rivera", "\"Come in, sit anywhere. What's on your mind?\"")
                .choice("Talk about what you've been going through (30 min)", talk).choice("\"I'm fine.\" (leave)"))

    def done_counsel(self, r):
        s = r["score"]
        self.counseled = True
        self.counsel_visits += 1
        self.advance(30)
        self.add_worry(-(8 + 10 * s))
        self.skill = clamp(self.skill + 8 + 12 * s)
        self.raw("stress", -10)
        self.change("happiness", 5)
        self.relate("teachers", 3)
        line = COUNSELOR[min(self.counsel_visits, 4) - 1]
        self.say(Dialogue("Ms. Rivera", line))

    def a_coffee(self):
        def coffee():
            self.advance(10)
            self.add_worry(18)
            self.raw("stress", 8)
            self.raw("energy", 8)
            self.say(Dialogue("A few minutes later your heart is pounding and your hands shake. Caffeine can make anxiety worse."))

        def tea():
            self.advance(10)
            self.add_worry(-8)
            self.raw("stress", -4)
            self.change("happiness", 2)
            self.say(Dialogue("The warm cup in your hands helps your shoulders drop."))
        return (Dialogue("Barista", "\"What can I get you?\" You're exhausted from worrying all night.")
                .choice("Coffee (10 min)", coffee).choice("Herbal tea (10 min)", tea).choice("Nothing, just leave"))

    def on_arrive(self, to, frm):
        if to == "classroom" and self.arrival == "none":
            self.evaluate_arrival()
            return
        if to == "bus_stop" and frm == "hall" and self.maybe_left_early():
            return
        if self.level >= 4 and to in ("hall", "lunchroom") and self.once("avoid_" + to):
            def go_in():
                self.raw("stress", 4)
                self.add_worry(-1)
                self.say(Dialogue("Your legs feel like lead, but you go in anyway. The fear peaks and falls. You did it."))

            def wait():
                self.advance(10)
                self.quiet("stress", -2)
                self.add_worry(2)
                self.say(Dialogue("You wait outside until it feels safer. Avoiding gives relief, but the fear gets stronger next time."))
            self.say(Dialogue("Dread", "The noise and the crowd feel like too much. Everything in you says to turn around.")
                     .choice("Go in anyway", go_in).choice("Wait outside for a bit (10 min)", wait))
            return
        notes = {"bus_stop": "Two kids look up from their phones. Your chest tightens. Did they notice something about you?",
                 "hall": "The hallway is loud. You scan every face, sure someone is judging you.",
                 "lunchroom": "The lunchroom is a wall of noise. Where to sit? What if you pick wrong?"}
        if to in notes and self.once_global("note_" + to):
            self.say(Dialogue(notes[to]))

    def once_global(self, key):
        if key in self.seen:
            return False
        self.seen.add(key)
        return True

    def evaluate_arrival(self):
        if self.minutes <= CLASS_START:
            self.arrival = "on_time"
            self.mark("on_time")
            self.relate("teachers", 2)
            self.say(Dialogue("You slip into your seat before the bell. (On time)"))
        elif self.minutes <= LATE_CUTOFF:
            self.arrival = "late"
            self.relate("teachers", -3)
            self.change("stress", 6)
            self.study(-0.5)
            self.say(Dialogue("Class has already started. Every eye lands on you as you walk in. (Late)"))
        else:
            self.arrival = "missed"
            self.morning_done = True
            self.relate("teachers", -4)
            self.change("stress", 8)
            self.say(Dialogue("The morning lesson is almost over by the time you arrive. You can still make the afternoon. (Missed morning class)"))

    def maybe_left_early(self):
        if self.arrival in ("on_time", "late") and not self.afternoon_done and not self.left_early:
            self.left_early = True
            self.relate("teachers", -3)
            self.say(Dialogue("You leave before afternoon class. Going home feels easier right now, but skipping will cost you."))
            return True
        return False