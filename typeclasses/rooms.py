"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from evennia import utils


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    def at_object_receive(self, obj, source_location):
        if utils.inherits_from(obj, 'typeclasses.monsters.Monster'): #A Monster has entered
            return
        elif utils.inherits_from(obj, 'typeclasses.characters.Character'):
            # A Player has entered.
            # Sause the player's character to look around.
            obj.execute_cmd('look')
            for item in self.contents:
                if utils.inherits_from(item, 'typeclasses.monsters.Monster'):
                    # A Monster is in the room
                    item.at_char_entered(obj)
                if utils.inherits_from(item, 'typeclasses.npcs.NPC'):
                    # An NPC is in the room
                    item.at_char_entered(obj)

    pass
