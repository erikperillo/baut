import core.state as state
import core.command_line as cl
import core.table as table
import csv
import os
import oarg
import time
import hashlib

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
    values = [states_table[col] for col in ("name", "getter", "setter")]
    system_states = dict((name, state.SystemState(getter, setter)) \
                         for name, getter, setter in zip(*values))
    return system_states

def addCmdTimeToFile(file_path, cmd_name, time):
    #file must have the format: cmd,avg_wall_time
    with open(file_path, "a") as times_file:
        times_file.write(",".join((cmd_name, str(time))) + os.linesep)

def getRunDirName(fmt="baut_run_%d-%m-%Y_%H:%M:%S"):
    return time.strftime(fmt, time.gmtime())

def getCmdUniqueName(cmd_name, hash_size=8):
    hash_obj = hashlib.md5(cmd_name)
    return "%s_%s" % (os.path.basename(cmd_name), hash_obj.hexdigest()[0:hash_size])

def formatTime(seconds):
    seconds = int(seconds) 
    hours = seconds / 3600
    minutes = (seconds%3600) / 60
    seconds = seconds % 60 
    return hours, minutes, seconds

def getStateFileLines(header, values, commands):
    header, values = list(header), list(values)

    if not "cmd" in header:
        header.append("cmd")
        values.append("")

    values[header.index("cmd")] = " ".join(commands)

    return header, values

def run():
    #routine's variables
    global info_key
    info_key = "[baut::run] "
    special_names = ("cmd", "before_cmd", "after_cmd", "iterations")

    #command line arguments
    oarg.reset()

    sys_states_path = oarg.Oarg(str, "-s --sys-states-path", "", "system states path")
    rounds_states_path = oarg.Oarg(str,"-r --rounds", "", "rounds states list")
    cmds_list = oarg.Oarg(str,"-c --commands", "",
                          "commands list (will override possible list in file)", single=False)
    run_dir = oarg.Oarg(str, "-d --run-dir", os.getcwd(), "directory to store results")
    times_file = oarg.Oarg(str, "-t --times-file", "", "file to store times statistics")
    hlp = oarg.Oarg(bool, "-h --help", False, "this help message")
    
    #ckecking for wrong command line options
    try:
        oarg.parse()
    except oarg.UnknownKeyword:
        for key in oarg.unknown_keys:
            if not key in MAIN_OPTS:
                error("unknown key '-%s' passed" % key)    

    if hlp.val:
        info("options:")
        oarg.describeArgs(def_val=True)
        exit()

    for oa in sys_states_path, rounds_states_path:
        if not oa.found:
            error("argument of keyword '-%s' must be passed" % oa.keywords[0])

    #loading system states table
    sys_states = loadSystemStates(sys_states_path.val)    

    #loading rounds states table
    rounds_states = table.Table(rounds_states_path.val).transposed()

    #determining list of commands to run
    if cmds_list.found:
        commands = cmds_list.vals
    else:
        try:
            commands = rounds_states["cmd"]
        except KeyError:
            error("invalid format for rounds file, must contain apps specifier")

    #names of state variables
    rounds_states_names = rounds_states[0]

    #checking validity of names 
    for special_name in special_names:
        if not special_name in rounds_states_names:
            error("no variable '%s' defined in file '%s'" % (special_name, rounds_states_path.val))

    for name in rounds_states_names:
        if not name in special_names and not name in sys_states:
            error("unknown system state '%s' in file '%s'" % (name, rounds_states_path.val))

    #creating run directory
    run_dir = os.path.join(run_dir.val, getRunDirName())

    #main running loop
    for i, round_state in enumerate(rounds_states[1:]):
        info("creating round structure")
        round_dir = os.path.join(run_dir, "round_%d" % i)
        try:
            os.makedirs(round_dir)
        except OSError:
            info("warning: directory '%s' already existed" % round_dir)
        #creating state file
        header, values = getStateFileLines(rounds_states_names, round_state, commands)
        with open(os.path.join(round_dir, "state.csv"), "w") as state_file:
            state_file.write(",".join(header) + os.linesep)
            state_file.write(",".join(values) + os.linesep)

        info("starting new round\n")
        states = dict((key, val) for key, val in zip(rounds_states_names, round_state))

        for state_name in [key for key, val in states.iteritems() \
                           if not key in special_names and val]:
            info("setting %s = %s ..." % (state_name, states[state_name]))
            sys_states[state_name] = states[state_name]

        for k in xrange(int(states["iterations"])):
            info("on iteration %d out of %d" % (k + 1, int(states["iterations"])))
            print "H",commands 
            for cmd in commands:
                #creating cmd dir
                cmd_dir = os.path.join(round_dir, getCmdUniqueName(cmd))
                try:
                    os.makedirs(cmd_dir)
                except OSError:
                    pass

                #building command line
                cmd_line = cl.CommandLine(cmd, states["before_cmd"], states["after_cmd"])

                info("\trunning command %s ..." % cmd_line)
                if times_file.val:
                    start_time = time.time()          
                #running command 
                stdout, stderr = cmd_line.run()
                #adding time to file if specified 
                if times_file.val:
                    wall_time = time.time() - start_time
                    addCmdTimeToFile(times_file.val, cmd, wall_time)
                    msg = "\tdone | %f seconds elapsed" % wall_time
                    info(msg)

                #writing results to files
                with open(os.path.join(cmd_dir, "stdout_%d" % (k+1)), "w") as out_file, \
                     open(os.path.join(cmd_dir, "stderr_%d" % (k+1)), "w") as err_file:
                    out_file.write(stdout)
                    err_file.write(stderr) 
                     

def main():
    #command line args
    action = oarg.Oarg(str, "-A --action", "", "action to take", 0)
    hlp = oarg.Oarg(bool, "-h --help", False, "this help message")

    #checking for wrongs options passed, it may be intended for other parts besides main
    unknown_key = ""
    try:
        oarg.parse()
    except oarg.UnknownKeyword as e:
        unknown_key = e.key

    #checking for errors
    if not action.found:
        if hlp.val:
            info("options:")
            oarg.describeArgs()
            exit()
        else:
            error("must specify an action (%s). use '--help' for more info" % ", ".join(ACTIONS))

    if not action.val.lower() in ACTIONS:
        error("invalid action '%s'" % action.val)

    #determining subroutine to use
    if action.val.lower() == "run":
        run()
    elif unknown_key:
        raise oarg.UnknownKeyword("invalid option '%s' passed" % unknown_key, unknown_key)

if __name__ == "__main__":
    main()
