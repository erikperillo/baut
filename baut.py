import core.state as state
import core.command_line as cl
import core.table as table
import csv
import os
import oarg

ACTIONS = ("run",)
MAIN_OPTS = ("A", "action", "h", "help")
info_key = "[baut] "

def error(msg, code=1):
    print info_key + "error: " + msg
    exit(code) 

def info(msg):
    print info_key + msg

def loadSystemStates(file_path, delim=","):
    states_table = table.Table(file_path, delim=delim)    
    values = [states_table[col] for col in ("name", "getter", "setter", "type")]
    system_states = dict((name, state.SystemState(getter, setter, type_name)) \
                         for name, getter, setter, type_name in zip(*values))
    return system_states

def run():
    global info_key
    info_key = "[baut::run] "
    special_names = ("cmd", "before_cmd", "after_cmd")

    oarg.reset()

    sys_states_path = oarg.Oarg(str, "-s --sys-states-path", "", "system states path")
    rounds_states_path = oarg.Oarg(str,"-r --rounds", "", "rounds states list")
    apps = oarg.Oarg(str,"-a --apps", "", "applications list (will override possible list in file)")
    hlp = oarg.Oarg(bool, "-h --help", False, "this help message")
    
    try:
        oarg.parse()
    except oarg.UnknownKeyword:
        for key in oarg.unknown_keys:
            if not key in MAIN_OPTS:
                error("unknown key '-%s' passed" % key)    

    if hlp.val:
        info("options:")
        oarg.describeArgs()
        exit()

    for oa in sys_states_path, rounds_states_path:
        if not oa.found:
            error("argument of keyword '-%s' must be passed" % oa.keywords[0])

    #loading tables
    sys_states = loadSystemStates(sys_states_path.val)    
    rounds_states = table.Table(rounds_states_path.val).transposed()

    if apps.found:
        commands = apps.vals
    else:
        try:
            commands = rounds_states["cmd"]
        except KeyError:
            error("invalid format for rounds file, must contain apps specifier")

    rounds_states_names = rounds_states[0]
    for name in rounds_states_names:
        if not name in special_names and not name in sys_states:
            error("unknown system state '%s' in file '%s'" % (name, rounds_states_path.val))

    for i, round_state in enumerate(rounds_states[1:]):
        info("round %d:" % i)
        states = dict((key, val) for key, val in zip(rounds_states_names, round_state))

        for state_name in [key for key, val in states.iteritems() \
                           if not key in special_names and val]:
            info("\tsetting %s = %s ..." % (state_name, states[state_name]))
            sys_states[state_name] = states[state_name]

        for cmd in commands:
            cmd_line = cl.CommandLine(cmd, states["before_cmd"], states["after_cmd"])
            info("running command '%s'" % cmd_line)
            #cmd_line.run()

def main():
    action = oarg.Oarg(str, "-A --action", "", "action to take", 0)
    hlp = oarg.Oarg(bool, "-h --help", False, "this help message")

    unknown_key = ""
    try:
        oarg.parse()
    except oarg.UnknownKeyword as e:
        unknown_key = e.key

    if not action.found:
        if hlp.val:
            info("options:")
            oarg.describeArgs()
            exit()
        else:
            error("must specify an action (%s). use '--help' for more info" % ", ".join(ACTIONS))

    if not action.val.lower() in ACTIONS:
        error("invalid action '%s'" % action.val)

    if action.val.lower() == "run":
        run()
    elif unknown_key:
        raise oarg.UnknownKeyword("invalid option '%s' passed" % unknown_key, unknown_key)

if __name__ == "__main__":
    main()
