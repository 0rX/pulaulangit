"""
Commands

Commands describe the input the account can do to the game.

"""
import re

from evennia.commands.command import Command as BaseCommand
from evennia import InterruptCommand
from evennia.utils import inherits_from
from evennia.utils.evmenu import EvMenu
from evennia import search_object

# from evennia import default_cmds


class Command(BaseCommand):
    """
    Inherit from this if you want to create your own command styles
    from scratch.  Note that Evennia's default commands inherits from
    MuxCommand instead.

    Note that the class's `__doc__` string (this text) is
    used by Evennia to create the automatic help entry for
    the command, so make sure to document consistently here.

    Each Command implements the following methods, called
    in this order (only func() is actually required):
        - at_pre_cmd(): If this returns anything truthy, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_cmd(): Extra actions, often things done after
            every command, like prompts.

    """
    pass

class CmdInventory(Command):
    """
    Shows your inventory.

    """
    key     = "inventory"
    aliases = ["inv", "i"]
    locks   = "cmd:all()"
    def parse(self):
        self.args       = self.args.lstrip()
        args            = self.args

        self.arg_type   = get_inventory_arg_type(args)
    def func(self):
        self.caller.inv.get_inventory(self.arg_type)

class CmdPut(Command):
    """
    Usage:
        put <item> di <container>

    Finds an item around you and put it in a container.
    """
    key     = "put"
    aliases = ["taro", "taruh"]
    locks   = "cmd:all()"

    def parse(self):
        try:
            if not self.args:
                raise InterruptCommand
            for i in ["di", "in", "on", "at", "ke"]:
                if i in self.args.split(" "):
                    self.splitter = i
            self.obj_arg, self.container_arg   = self.args.split(" "+self.splitter+" ")
            self.obj_arg       = self.obj_arg.strip()
            self.container_arg  = self.container_arg.strip()
        except:
            self.caller.msg("Usage: put <object> di <container>")
            raise InterruptCommand

    def func(self):
        caller          = self.caller
        obj_arg         = self.obj_arg
        container_arg   = self.container_arg
        splitter        = self.splitter

        # Find the item.
        # Location unset, search conducted within the character and its location.

        obj   = caller.search(obj_arg, quiet=True)[0]
        if not obj.access(caller, 'get'):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("You can't move that thing.")
            raise InterruptCommand

        if obj:
            container = caller.search(container_arg, quiet=True)
            if container:
                if len(container):
                    container = container[0]
                if obj.location == caller:
                    caller.msg(f"you place {obj.name} {splitter} {container.name}.")
                    caller.msg_contents(f"{caller.name} places {obj.name} {splitter} {container.name}.")
                if obj.location == caller.location:
                    caller.msg(f"You pick up {obj.name} and place it {splitter} {container.name}.")
                    caller.msg_contents(f"{caller.name} picks up {obj.name} and places it {splitter} {container.name}.", exclude=caller)
                obj.move_to(container, quiet=True)
            else:
                caller.msg(f"Could not find {container_arg}!")
        else:
            caller.msg(f"Could not find {obj_arg}!")

class CmdGet(Command):
    """
    Picks up something.

    Usage:
        get <object>
        get <object> dari <container>

    Gets an object from your inventory or location and places it in your inventory.
    """
    key     = "get"
    aliases = ["take", "ambil"]
    locks   = "cmd:all()"

    def parse(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: get <object> | get <object> dari <container>")
            raise InterruptCommand
        self.splitter = None
        args = self.args
        for i in ["dari","from","in","on","di","at"]:
            if i in args.split(" "):
                self.splitter = i
        if self.splitter != None:
            splitter = self.splitter
            obj_arg = args.split(" "+splitter+" ", 1)[0].strip()
            container_arg = args.split(" "+splitter+" ", 1)[1].strip()

            container = caller.search(container_arg, quiet=True)
            if not container:
                caller.msg(f"Could not find {container_arg}.")
                raise InterruptCommand
            else:
                container = container[0]
                if not container.tags.get('container'):
                    caller.msg(f"You can't get {obj_arg} from {container.name}.")
                    raise InterruptCommand
                self.container = container
                obj = caller.search(obj_arg, location=container, quiet=True)
                if not obj:
                    caller.msg(f"Could not find {obj_arg} {splitter} {container}.")
                    raise InterruptCommand
                else:
                    obj = obj[0]
                    self.caller_possess = True if obj.location == caller else False
                    self.obj = obj
        else:
            obj_arg = args.strip()
            try:
                obj = caller.search(obj_arg, quiet=True)[0]
                if not obj:
                    caller.msg(f"Could not find {obj_arg}.")
                    raise InterruptCommand
                else:
                    self.caller_possess = True if obj.location == caller else False
                    self.container = None
                    self.obj = obj
            except:
                caller.msg("You don't see that thing here.")
                raise InterruptCommand

        if caller == obj:
            caller.msg("You can't get yourself.")
            raise InterruptCommand

        if not obj.access(caller, 'get'):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("You can't get that.")
                raise InterruptCommand

    def func(self):
        success = self.obj.move_to(self.caller, quiet=True)
        self.caller.msg(f"You pick up {self.obj.name}")
        self.caller.location.msg_contents(
                f"{self.caller.name} picks up {self.obj.name}", exclude=self.caller
            )
        #(self.obj, self.container, self.caller_possess)

class CmdPulangin(Command):
    """
    used for Developers to return objects to their home location.

    Usage:
        pulangin <target>
    """
    key             = 'pulangin'
    help_category   = 'developer'
    locks           = 'cmd:all()'
    def func(self):
        if not self.args:
            self.caller.msg("Usage: pulangin <target>")
            return
        else:
            args = self.args.strip()
            num = None
            if "-" in args:
                num, args = args.split("-", 1)
                num = int(num)-1
            if "#" in args:
                target = search_object(args)[0]
            else:
                target = search_object(args)
                if len(target) > 1 and num == None:
                    listobjname = []
                    output = "Pulangin yang mana ?|/"
                    index = 1
                    for i in target:
                        string = str(index)+"-"+i.name+f" (|b#{i.dbid}|n)"
                        listobjname.append(string)
                        index += 1
                    for name in listobjname:
                        output = output+name+"|/"
                    self.caller.msg(f"{output}")
                    return
                if num == None:
                    num = 0
                target = target[num]
            if not target.access(self.caller, 'monster') or not target.access(self.caller, 'pulangin'):
                if target.db.get_err_msg:
                    self.caller.msg(target.db.get_err_msg)
                else:
                    self.caller.msg("Kamu ngga bisa pulangin objek ini.")
                    raise InterruptCommand
            if target:
                target.move_to(target.home, quiet=True)
                self.caller.msg(f"{target.name} sudah kembali ke home location")
            else:
                self.caller.msg(f"You don't see {self.args} here")


class CmdFlee(Command):
    """
    Used for monsters/NPCs when they digetok.
    """
    key             = 'flee'
    help_category   = 'your nightmare'

    def func(self):
        exit = search_object("Black Hole").get()
        self.caller.move_to(exit)
        yield 180
        self.caller.move_to(self.caller.home)
        for obj in self.caller.homes_set.select_related():
            obj.move_to(obj.home)

class CmdGetok(Command):
    """
    Getok seseorang atau sesuatu dengan palu, jika kamu punya palu.

    Usage:
        getok <target>
    """
    key             = 'getok'
    help_category   = 'action'
    weapon_req      = 'palu kayu'

    def parse(self):
        if not self.args:
            self.caller.msg('Usage: getok <target>')
            raise InterruptCommand
        self.args = self.args.strip()

    def func(self):
        caller  = self.caller

        target = caller.search(self.args, quiet=True)
        inven = []
        if not target:
            caller.msg(f'Ngga ada {self.args} di sini')
            raise InterruptCommand
        weakness = target[0].db.weakness
        if weakness:
            weakness = weakness.lower()
        if caller.contents == None:
            caller.msg(f'Kamu ngga punya {self.weapon_req} buat getok getok.')
            raise InterruptCommand
        for i in caller.contents:
            i = i.name.lower()
            inven.append(i)
        if weakness not in inven:
            caller.msg(f'Kamu ngga punya {self.weapon_req} buat getok getok.')
            raise InterruptCommand
        else:
            target = target[0]
            if inherits_from(target, 'typeclasses.monsters.Monster'):
                # Getok monster
                target.at_cmd_getok(caller, self.weapon_req)

class CmdTembak(Command):
    """
    Tembak seseorang atau sesuatu dengan Pistol, jika kamu punya Pistol.

    Usage:
        tembak <target>
    """
    key             = 'tembak'
    help_category   = 'action'
    weapon_req      = 'pistol'

    def parse(self):
        if not self.args:
            self.caller.msg('Usage: tembak <target>')
            raise InterruptCommand
        self.args = self.args.strip()

    def func(self):
        caller  = self.caller

        target = caller.search(self.args, quiet=True)
        inven = []
        if not target:
            caller.msg(f'Ngga ada {self.args} di sini')
            raise InterruptCommand
        weakness = target[0].db.weakness
        if weakness:
            weakness = weakness.lower()
        if caller.contents == None:
            caller.msg(f'Kamu ngga punya {self.weapon_req} buat menembak.')
            raise InterruptCommand
        for i in caller.contents:
            i = i.name.lower()
            inven.append(i)
        if weakness not in inven:
            caller.msg(f'Kamu ngga punya {self.weapon_req} buat menembak.')
            raise InterruptCommand
        else:
            target = target[0]
            if inherits_from(target, 'typeclasses.monsters.Monster'):
                # Tembak monster
                target.at_cmd_tembak(caller, self.weapon_req)


class CmdLook(Command):
    """
    Look at location or object

    Usage:
        look
        look <obj>
        look <obj> in <container>
        look *<account>

    Observes your location or objects in your vicinity.
    """
    key = "look"
    aliases = ["l", "ls", "liat", "lihat"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def parse(self):
        caller = self.caller
        self.splitter = None
        if self.args:
            args = self.args
            for i in ["in","on","di","at"]:
                if i in args.split(" "):
                    self.splitter = i
            if self.splitter != None:
                splitter = self.splitter
                obj_arg = args.split(" "+splitter+" ", 1)[0].strip()
                container_arg = args.split(" "+splitter+" ", 1)[1].strip()

                container = caller.search(container_arg, quiet=True)[0]
                if container.access(caller, 'kunci') == True and container.access(caller, 'look') == False:
                    if container.db.get_err_msg:
                        caller.msg(container.db.get_err_msg)
                        raise InterruptCommand
                    else:
                        caller.msg("Can't see that item.")
                        raise InterruptCommand
                if not container:
                    caller.msg(f"Could not find {container_arg}.")
                    raise InterruptCommand
                else:
                    if not container.tags.get('container'):
                        caller.msg(f"You can't see {obj_arg} from {container.name}.")
                        raise InterruptCommand
                    self.container = container
                    obj = caller.search(obj_arg, location=container, quiet=True)[0]
                    if not obj:
                        caller.msg(f"Could not find {obj_arg}.")
                        raise InterruptCommand
                    else:
                        self.obj = obj
            else:
                obj_arg = args.strip()
                try:
                    obj = caller.search(obj_arg, quiet=True)[0]
                    if obj.access(caller, 'kunci') == True and obj.access(caller, 'look') == False:
                        #caller.msg("done2")
                        if obj.db.get_err_msg:
                            #caller.msg("done3")
                            caller.msg(obj.db.get_err_msg)
                            raise InterruptCommand
                        else:
                            #caller.msg("done4")
                            caller.msg("Can't see that item.")
                            raise InterruptCommand
                    if not obj:
                        #caller.msg("done5")
                        caller.msg(f"Could not find {obj_arg}.")
                        raise InterruptCommand
                    else:
                        #caller.msg("done6")
                        self.container = None
                        self.obj = obj
                except:
                    #caller.msg("You don't see that thing here.")
                    raise InterruptCommand

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("You have no location to look at!")
                return
        else:
            #target = caller.search(self.obj)
            target = self.obj
            if not target:
                return
        self.msg((caller.at_look(target), {"type":"look"}), options=None)

def get_inventory_arg_type(args):
    arg_type = 0 # Default inventory summary.

    all_list = ['all', '1']
    fav_list = ['fav', 'favor', 'favorite', 'favorites', '2']
    weap_list = ['weap', 'weapon', 'weapons', '3']
    arm_list = ['arm', 'armor', '4']
    cloth_list = ['clo', 'cloth', 'clothing', '5']
    contain_list = ['con', 'cont', 'containers', '6']
    jewel_list = ['jew', 'jewel', 'jewelry', '7']
    relic_list = ['rel', 'relic', 'relics', '8']
    consume_list = ['cons', 'consum', 'consumable', 'consumables', '9']
    quest_list = ['que', 'ques', 'quest', '10']
    craft_list = ['cra', 'craf', 'craft', 'crafting', '11']
    misc_list = ['mis', 'misc', '12']

    if args in all_list: # List the entire inventory, separated by category.
        arg_type = 1
    elif args in fav_list:
        arg_type = 2
    elif args in weap_list:
        arg_type = 3
    elif args in arm_list:
        arg_type = 4
    elif args in cloth_list:
        arg_type = 5
    elif args in contain_list:
        arg_type = 6
    elif args in jewel_list:
        arg_type = 7
    elif args in relic_list:
        arg_type = 8
    elif args in consume_list:
        arg_type = 9
    elif args in quest_list:
        arg_type = 10
    elif args in craft_list:
        arg_type = 11
    elif args in misc_list:
        arg_type = 12
    return arg_type


# -------------------------------------------------------------
#
# The default commands inherit from
#
#   evennia.commands.default.muxcommand.MuxCommand.
#
# If you want to make sweeping changes to default commands you can
# uncomment this copy of the MuxCommand parent and add
#
#   COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"
#
# to your settings file. Be warned that the default commands expect
# the functionality implemented in the parse() method, so be
# careful with what you change.
#
# -------------------------------------------------------------

# from evennia.utils import utils
#
#
# class MuxCommand(Command):
#     """
#     This sets up the basis for a MUX command. The idea
#     is that most other Mux-related commands should just
#     inherit from this and don't have to implement much
#     parsing of their own unless they do something particularly
#     advanced.
#
#     Note that the class's __doc__ string (this text) is
#     used by Evennia to create the automatic help entry for
#     the command, so make sure to document consistently here.
#     """
#     def has_perm(self, srcobj):
#         """
#         This is called by the cmdhandler to determine
#         if srcobj is allowed to execute this command.
#         We just show it here for completeness - we
#         are satisfied using the default check in Command.
#         """
#         return super().has_perm(srcobj)
#
#     def at_pre_cmd(self):
#         """
#         This hook is called before self.parse() on all commands
#         """
#         pass
#
#     def at_post_cmd(self):
#         """
#         This hook is called after the command has finished executing
#         (after self.func()).
#         """
#         pass
#
#     def parse(self):
#         """
#         This method is called by the cmdhandler once the command name
#         has been identified. It creates a new set of member variables
#         that can be later accessed from self.func() (see below)
#
#         The following variables are available for our use when entering this
#         method (from the command definition, and assigned on the fly by the
#         cmdhandler):
#            self.key - the name of this command ('look')
#            self.aliases - the aliases of this cmd ('l')
#            self.permissions - permission string for this command
#            self.help_category - overall category of command
#
#            self.caller - the object calling this command
#            self.cmdstring - the actual command name used to call this
#                             (this allows you to know which alias was used,
#                              for example)
#            self.args - the raw input; everything following self.cmdstring.
#            self.cmdset - the cmdset from which this command was picked. Not
#                          often used (useful for commands like 'help' or to
#                          list all available commands etc)
#            self.obj - the object on which this command was defined. It is often
#                          the same as self.caller.
#
#         A MUX command has the following possible syntax:
#
#           name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]
#
#         The 'name[ with several words]' part is already dealt with by the
#         cmdhandler at this point, and stored in self.cmdname (we don't use
#         it here). The rest of the command is stored in self.args, which can
#         start with the switch indicator /.
#
#         This parser breaks self.args into its constituents and stores them in the
#         following variables:
#           self.switches = [list of /switches (without the /)]
#           self.raw = This is the raw argument input, including switches
#           self.args = This is re-defined to be everything *except* the switches
#           self.lhs = Everything to the left of = (lhs:'left-hand side'). If
#                      no = is found, this is identical to self.args.
#           self.rhs: Everything to the right of = (rhs:'right-hand side').
#                     If no '=' is found, this is None.
#           self.lhslist - [self.lhs split into a list by comma]
#           self.rhslist - [list of self.rhs split into a list by comma]
#           self.arglist = [list of space-separated args (stripped, including '=' if it exists)]
#
#           All args and list members are stripped of excess whitespace around the
#           strings, but case is preserved.
#         """
#         raw = self.args
#         args = raw.strip()
#
#         # split out switches
#         switches = []
#         if args and len(args) > 1 and args[0] == "/":
#             # we have a switch, or a set of switches. These end with a space.
#             switches = args[1:].split(None, 1)
#             if len(switches) > 1:
#                 switches, args = switches
#                 switches = switches.split('/')
#             else:
#                 args = ""
#                 switches = switches[0].split('/')
#         arglist = [arg.strip() for arg in args.split()]
#
#         # check for arg1, arg2, ... = argA, argB, ... constructs
#         lhs, rhs = args, None
#         lhslist, rhslist = [arg.strip() for arg in args.split(',')], []
#         if args and '=' in args:
#             lhs, rhs = [arg.strip() for arg in args.split('=', 1)]
#             lhslist = [arg.strip() for arg in lhs.split(',')]
#             rhslist = [arg.strip() for arg in rhs.split(',')]
#
#         # save to object properties:
#         self.raw = raw
#         self.switches = switches
#         self.args = args.strip()
#         self.arglist = arglist
#         self.lhs = lhs
#         self.lhslist = lhslist
#         self.rhs = rhs
#         self.rhslist = rhslist
#
#         # if the class has the account_caller property set on itself, we make
#         # sure that self.caller is always the account if possible. We also create
#         # a special property "character" for the puppeted object, if any. This
#         # is convenient for commands defined on the Account only.
#         if hasattr(self, "account_caller") and self.account_caller:
#             if utils.inherits_from(self.caller, "evennia.objects.objects.DefaultObject"):
#                 # caller is an Object/Character
#                 self.character = self.caller
#                 self.caller = self.caller.account
#             elif utils.inherits_from(self.caller, "evennia.accounts.accounts.DefaultAccount"):
#                 # caller was already an Account
#                 self.character = self.caller.get_puppet(self.session)
#             else:
#                 self.character = None


