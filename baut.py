#!/usr/bin/python2.7

import core.state as state
import core.table as table
import os
import sys
try:
    import oarg_exp as oarg
except ImportError:
    import oarg
import time
import subprocess as sp
import shutil
import shlex
import numpy
import glob

ACTIONS = ("run", "extract")
MAIN_OPTS = ("A", "action", "h", "help")
info_key = "[baut] "
file_dir = os.path.dirname(os.path.abspath(__file__))

def gitHash():
    try:
        git_hash = sp.check_output(["git", "rev-parse", "HEAD"]).replace(os.linesep, "")
    except:
        info("warning: could not get git repository commit hash")
        return ""

    return git_hash

def metaInfo(file_path, time_fmt="%A, %d %B %Y %H:%M:%S"):
    with open(file_path, "w") as meta_file:
        meta_file.write("generated by command: %s\n" % " ".join(sys.argv))
        meta_file.write("created on: %s\n" % time.strftime(time_fmt))
        git_hash = gitHash()
        meta_file.write("project commit hash: %s\n" % git_hash)

def error(msg, code=1):
    print info_key + "error: " + msg
    exit(code) 

def info(msg, newline=True):
    if newline:
        print info_key + msg
    else:
        print info_key + msg,

    sys.stdout.flush()

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
    
def loadSystemStates(file_path, delim=",", file_patterns=False):
    states_table = table.Table(file_path, delim=delim)    

    values = [states_table[col] for col in ("name", "getter", "setter")]

    if not file_patterns:
        return dict((name, state.SystemState(os.path.abspath(getter), os.path.abspath(setter)))\
                    for name, getter, setter in zip(*values))
    
    values.append(states_table["file_pattern"])
    return dict((name, (state.SystemState(os.path.abspath(getter), os.path.abspath(setter)), 
                        pattern)) \
                for name, getter, setter, pattern in zip(*values))

def addCmdTimeToFile(file_path, cmd_name, time):
    #file must have the format: cmd,wall_time
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
    global info_key, file_dir
    info_key = "[baut::run] "
    special_names = ("command", "iterations")

    #command line arguments
    oarg.reset()

    vars_path = oarg.Oarg("-v --vars", os.path.join(file_dir, "vars", "vars.csv"), 
                          "vars .csv file path")
    states_path = oarg.Oarg("-s --states", "", "rounds states .csv file path")
    run_dir = oarg.Oarg("-d --run-dir", os.path.join(file_dir, "runs"), 
                        "directory to store results")
    times_file = oarg.Oarg("-t --times-file", os.path.join(file_dir, "times.csv"), 
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

    for oa in (states_path, ):
        if not oa.found:
            error("argument of keyword '-%s' must be passed" % oa.keywords[0])

    #loading system states table
    variables = loadSystemStates(vars_path.val)    

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
        except IOError:
            info("warning: times file '%s' could not be open" % times_file.val)

    for name in states_descr:
        if not name in special_names and not name in variables:
            error("unknown system state '%s' in file '%s'" % (name, states_path.val))

    #creating run directory
    run_dir = os.path.join(run_dir.val, getRunDirName())
    if not os.path.exists(run_dir):
        os.makedirs(run_dir)
    info("storing execution information in '%s'" % run_dir)

    #copying states file
    shutil.copy2(states_path.val, os.path.join(run_dir, "states.csv"))

    #creating meta file
    metaInfo(os.path.join(run_dir, "meta.txt"))

    total_time = 0.
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

        #changing directory to state dir
        os.chdir(state_dir)

        #creating state dict
        state = dict((key, val) for key, val in zip(states_descr, _state))

        #setting system states
        info("vars configuration:")
        for name in [key for key, val in state.iteritems() if not key in special_names and val]:
            info("\tsetting %s = %s ..." % (name, state[name]), newline=False)
            variables[name] = state[name]
            print "done" 

        #creating state file
        with open("state.csv", "w") as state_file:
            state_file.write(",".join(states_descr) + os.linesep)
            state_file.write(",".join(state[key] if key in special_names else variables[key] \
                                      for key in states_descr) + os.linesep)

        #creating command
        command = shlex.split(state["command"])

        info("on command '%s':" % " ".join(command))
        
        wall_times = []
        files = []
        #command loop
        for k in xrange(int(state["iterations"])):
            info("\trunning iteration %d out of %d ..." % (k+1, int(state["iterations"])),
                  newline=False)
            #creating process
            process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)    

            #time statistics
            start_time = time.time()          
            #running command
            stdout, stderr = process.communicate()
            #getting elapsed time
            wall_times.append(time.time() - start_time)
            print "done (%f seconds elapsed)" % wall_times[-1]

            #appending time to times file if specified
            if times_file.val:
                addCmdTimeToFile(times_file.val, " ".join(command), wall_times[-1])

            #writing results to files
            with open("stdout", "w") as out_file, open("stderr", "w") as err_file:
                out_file.write(stdout)
                err_file.write(stderr) 

            files = [f for f in os.listdir(os.getcwd()) if f != "state.csv" and not f in files]

            for f in files:
                os.rename(f, "%s_%d" % (f, k+1))
            files = os.listdir(os.getcwd())

        total_time += sum(wall_times)
        info("end of iterations for command. average elapsed time: %fs" % \
             (sum(wall_times) / len(wall_times)))
                     
        #creating meta file for state dir
        metaInfo("meta.txt")
        
    print
    info("end. total elapsed time: %dh%dm%fs" % formatTime(total_time))

def extract():
    global info_key, file_dir
    info_key = "[baut::extract] "

    oarg.reset()

    run_dir = oarg.Oarg("-d --run-dir", "", "directory of application run")
    baut_run_struct = oarg.Oarg("-D --baut-struct", False, "indicates a baut run directory")
    vars_path = oarg.Oarg("-v --vars", os.path.join(file_dir, "vars", "vars.csv"), 
                          "vars .csv file path")
    vars_names = oarg.Oarg("-n --vars-names", "", "names of vars to filter", single=False)
    hlp = oarg.Oarg("-h --help", False, "this help message")
    
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

    for oa in vars_names, run_dir:
        if not oa.found:
            error("argument of keyword '-%s' must be passed" % oa.keywords[0])

    #loading variables to look for in run dir
    info("loading vars in file '%s' ..." % vars_path.val)
    _variables = loadSystemStates(vars_path.val, file_patterns=True)
    variables = {name: val for (name, val) in _variables.iteritems() if name in vars_names.vals}

    #checking for errors
    not_found_vars = [name for name in vars_names.vals if not name in variables]
    if not_found_vars:
        error("var name '%s' not found in vars file '%s'" % (not_found_vars[-1], vars_path.val))

    if any(not pattern for __, (var, pattern) in variables.iteritems()):
        error("some vars in file '%s' do not have a file pattern" % vars_path.val)

    if baut_run_struct.val:
        #runs were generated by baut and thus dir has a known structure
        base_dir = os.path.abspath(run_dir.val)
        #getting states dirs
        states_dirs = [d for d in os.listdir(base_dir) \
                       if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("state_")]
    else:
        base_dir = os.path.abspath(run_dir.val)
        states_dirs = [""]
        print base_dir, states_dirs

    #main loop
    for state_dir in states_dirs:
        print
        #going to base directory
        info("in directory '%s' ..." % os.path.join(base_dir, state_dir))
        os.chdir(os.path.join(base_dir, state_dir)) 

        #creating necessary directories 
        results_dir = "results"
        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)

        metaInfo(os.path.join(results_dir, "meta.txt"))

        for name, value in variables.iteritems():
            info("getting values for var '%s' ..." % name)
            var, pattern = value 

            input_files = glob.glob(os.path.join(os.getcwd(), pattern))            
            with open(os.path.join(results_dir, name), "w") as res_file:
                for input_file in input_files: 
                    output = var[input_file]
                    if not output.endswith(os.linesep):
                        output += os.linesep
                    res_file.write(output)

        info("results stored in '%s'" % os.path.abspath(results_dir))

    info("done.")

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
    elif action.val.lower() == "extract":
        extract()
    elif unknown_key:
        raise oarg.UnknownKeyword("invalid option '%s' passed" % unknown_key, unknown_key)

if __name__ == "__main__":
    main()
