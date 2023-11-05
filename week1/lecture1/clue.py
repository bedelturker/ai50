import termcolor

from logic import *

mustard = Symbol("ColMustard")
plum = Symbol("ProfPlum")
scarlet = Symbol("MsScarlet")
characters = [mustard, plum, scarlet]

ballroom = Symbol("ballroom")
kitchen = Symbol("kitchen")
library = Symbol("library")
rooms = [ballroom, kitchen, library]

knife = Symbol("knife")
revolver = Symbol("revolver")
wrench = Symbol("wrench")
weapons = [knife, revolver, wrench]

symbols = characters + rooms + weapons


def check_knowledge(knowledge):
    for symbol in symbols:
        if model_check(knowledge, symbol):
            termcolor.cprint(f"{symbol}: YES", "green")
        # Checking whether the opposite is actually true and if not
        # saying maybe
        elif not model_check(knowledge, Not(symbol)):
            print(f"{symbol}: MAYBE")


# There must be a person, room, and weapon.
knowledge = And(
    # Encoding that one of the people is a murderer and others are not
    Or(mustard, plum, scarlet),
    # It took place in one of the rooms and not others
    Or(ballroom, kitchen, library),
    # One of the weapons was used in the crime and not others
    Or(knife, revolver, wrench)
)

# Initial cards
# All the cards that I had that I got.
knowledge.add(And(
    Not(mustard), Not(kitchen), Not(revolver)
))

# Unknown card
# Someone making a guess and being wrong in their guess
# Note that we know that one of these must at least be false
knowledge.add(Or(
    Not(scarlet), Not(library), Not(wrench)
))

# Known cards
knowledge.add(Not(plum))
knowledge.add(Not(ballroom))

check_knowledge(knowledge)
