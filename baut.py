#!/usr/bin/python2.7

import core.state as state
import core.table as table
import os
import oarg_exp as oarg
import time
import subprocess as sp
import shutil
import shlex
import numpy

ACTIONS = ("run",)
MAIN_OPTS = ("A", "action", "h", "help")
info_key = "[baut] "

def error(msg, code=1):
    print info_key + "error: " + msg
    exit(code) 

def info(msg, newline=True):
    if newline:
        print info_key + msg
    else:
        print info_key + msg,

def getCmdTimes(command, file_path):
    times = []

    for row in table.getRawTable(file_path):
        cmd, time = row[0], float(row[1])
        if cmd == command:
            times.append(time)

    return times

def getCmdTimesList(states, states_descr, file_path):
    times = {}

    for state in states[1:]:
        cmd = state[states_descr.index("command")]
        its = int(state[states_descr.index("iterations")])

        _cmds_times = getCmdTimes(cmd, file_path)

        if _cmds_times:
            cmds_times = numpy.array(_cmds_times, dtype=float)
            time_mean = cmds_times.mean() * its
            time_std = cmds_times.std() * its
            times[cmd] = (time_mean, time_std)
        else:
            times[cmd] = None

    return times
    
def loadSystemStates(file_path, delim=","):
    states_table = table.Table(file_path, delim=delim)    
    values = [states_table[col] for col in ("name", "getter", "setter")]
    system_states = dict((name, state.SystemState(getter, setter)) \
                         for name, getter, setter in zip(*values))
    return system_states

def addCmdTimeToFile(file_path, cmd_name, time):
    #file must have the format: cmd,avg_wall_time
    with open(file_path, "a") as times_file:
        times_file.write(",".join((cmd_name.replace(",","\,"), str(time))) + os.linesep)

def getRunDirName(fmt="baut_run_%d-%m-%Y_%H:%M:%S"):
    return time.strftime(fmt, time.gmtime())

def getCmdUniqueName(cmd_name, hash_size=8):
    hash_obj = hashlib.md5(cmd_name)
    return "%s_%s" % (os.path.basename(cmd_name), hash_obj.hexdigest()[0:hash_size])

def formatTime(seconds):
    hours = int(seconds) / 3600
    minutes = (int(seconds)%3600) / 60
    seconds = seconds % 60 
    return hours, minutes, seconds

def run():
    #routine's variables
    global info_key
    info_key = "[baut::run] "
    special_names = ("command", "iterations")

    #command line arguments
    oarg.reset()

    sys_vars_path = oarg.Oarg("-s --sys-vars-path", "", "system vars .csv file path")
    states_path = oarg.Oarg("-S --states", "", "rounds states .csv file path")
    run_dir = oarg.Oarg("-d --run-dir", os.getcwd(), "directory to store results")
    times_file = oarg.Oarg("-t --times-file", os.path.abspath("times.csv"), 
                           "file to store times statistics")
    hlp = oarg.Oarg("-h --help", False, "this help message")
    
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

    for oa in sys_vars_path, states_path:
        if not oa.found:
            error("argument of keyword '-%s' must be passed" % oa.keywords[0])

    #loading system states table
    sys_states = loadSystemStates(sys_vars_path.val)    

    #loading rounds states table
    states = table.Table(states_path.val).transposed()
    #names of state variables
    states_descr = states[0]

    #checking validity of names 
    for special_name in special_names:
        if not special_name in states_descr:
            error("mandatory variable '%s' not defined in file '%s'" % (special_name, 
                                                                        states_path.val))

    if times_file.val:
        try:
            times_list = getCmdTimesList(states, states_descr, times_file.val)
            for cmd, elapsed_time in times_list.iteritems():
                if elapsed_time:
                    time_mean, time_std = elapsed_time 
                    info("time estimation for command '%s': %dh%dm%fs (+- %fs)" % \
                         ((cmd,) + formatTime(time_mean) + (time_std,)))
                else:
                    info("warning: could not get time estimation for command '%s'" % cmd)

            valid_times_list = [val for __, val in times_list.iteritems() if val]
            if valid_times_list:
                print "estimated total time: %dh%dm%fs (+- %fs)" % \
                      (formatTime(sum(mean for mean, __ in valid_times_list)) + 
                       (sum(std for __, std in valid_times_list),))
        except OSError:
            info("warning: times file '%s' could not be open")

    for name in states_descr:
        if not name in special_names and not name in sys_states:
            error("unknown system state '%s' in file '%s'" % (name, states_path.val))

    #creating run directory
    run_dir = os.path.join(run_dir.val, getRunDirName())
    if not os.path.exists(run_dir):
        os.makedirs(run_dir)
    #copying states file
    shutil.copy2(states_path.val, os.path.join(run_dir, "states.csv"))

    #main running loop
    for i, _state in enumerate(states[1:]):
        print
        info("in state %d" % (i+1))
        #creating state structure
        state_dir = os.path.join(run_dir, "state_%d" % i)
        if not os.path.exists(state_dir):
            os.makedirs(state_dir)
        else:
            info("warning: directory '%s' already exists" % state_dir)

        #creating state dict
        state = dict((key, val) for key, val in zip(states_descr, _state))

        #setting system states
        info("system vars configuration:")
        for name in [key for key, val in state.iteritems() if not key in special_names and val]:
            info("\tsetting %s = %s ..." % (name, state[name]), newline=False)
            sys_states[name] = state[name]
            print "done" 

        #creating state file
        with open(os.path.join(state_dir, "state.csv"), "w") as state_file:
            state_file.write(",".join(states_descr) + os.linesep)
            state_file.write(",".join(state[key] if key in special_names else sys_states[key] \
                                      for key in states_descr) + os.linesep)

        #creating command
        command = shlex.split(state["command"])

        info("on command '%s':" % " ".join(command))
        #command loop
        for k in xrange(int(state["iterations"])):
            info("\trunning iteration %d out of %d ..." % (k+1, int(state["iterations"])),
                  newline=False)
            #creating process
            process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)    

            if times_file.val:
                start_time = time.time()          
            #running command
            stdout, stderr = process.communicate()
            #appending time to times file if specified
            if times_file.val:
                wall_time = time.time() - start_time
                addCmdTimeToFile(times_file.val, " ".join(command), wall_time)
                print "done (%f seconds elapsed)" % wall_time
            else:
                print "done"

            #writing results to files
            with open(os.path.join(state_dir, "stdout_%d" % (k+1)), "w") as out_file, \
                 open(os.path.join(state_dir, "stderr_%d" % (k+1)), "w") as err_file:
                out_file.write(stdout)
                err_file.write(stderr) 
                     

def main():
    #command line args
    action = oarg.Oarg("-A --action", "", "action to take", 0)
    hlp = oarg.Oarg("-h --help", False, "this help message")

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
