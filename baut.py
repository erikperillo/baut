#!/usr/bin/python2.7

import oarg
import core.app as app
import core.state as st
import subprocess as sp
import os

#definitions
TOOLS_DIR_NAME          = "tools"
DEF_TESTS_DIR_NAME      = "tests" + "/" + "".join(sp.Popen([TOOLS_DIR_NAME + "/date/" + "get_date_footprint.sh"],stdout=sp.PIPE).communicate()[0].splitlines())
STATES_DIR_NAME         = "states"
APPS_DIR_NAME           = "apps"
STATE_DESCR_FILE        = "state.csv"
BENCHMARK_APPS_DIR_NAME = "apps"
NUMABAL_COMMOM_PATH     = "/proc/sys/kernel"
NUMABAL_CONFIG_FILE     = "tools/numa/numa_bal_config.py"
TIMES_FILE              = "times"
VALS_FILE               = "vals.csv"
VALS_FILE_TRANSPOSED    = "vals_transposed.csv"
DEF_SYSSTATES_FILE      = "confs/sys_states.csv"
DEF_CMDSTATES_FILE      = "confs/cmd_states.csv"

#avaliable actions
actions = ["run","extract"]

#key for info method
baut_key = "[baut]"

#command line arguments
action          = oarg.Oarg(str,"-a --action","","Action to execute",1)
quiet           = oarg.Oarg(bool,"-q --quiet",False,"Does not run so verbose")
sys_states_file = oarg.Oarg(str,"--sf --sys-states-file",DEF_SYSSTATES_FILE,"System states file (run mode)")
cmd_states_file = oarg.Oarg(str,"--cf --cmd-states-file",DEF_CMDSTATES_FILE,"Command line states file (run mode)")
hlp             = oarg.Oarg(bool,"-h --help",False,"This help message")

#options
opts            = ["--cf","--cmd-states-file","--sf","--sys-states-file","-q","--quiet","-a","--action"]

def info(msg,quiet=False):
    if not quiet:
        print baut_key + " " + msg

def error(msg,errn=1):
    info("error: " + msg)
    exit(errn)

def transposeCSV(file_in,file_out):
    import csv

    f,ft = open(file_in,"r"),open(file_out,"w")

    rows = list(csv.reader(f))
    writer = csv.writer(ft)
    for col in xrange(0, len(rows[0])):
        writer.writerow([row[col] for row in rows]) 

    f.close()
    ft.close()

def setSysStates(filename,n_toks=8):
    oargs = {}
    sys_states_descr = {}
    counter = 1
    
    f = open(filename,"r")
    for line in f:
        line = line.replace("\n","").strip()

        if line == "" or line[0] == "#":
            continue

        toks = line.split(",")
        if len(toks) != n_toks:
            error("wrong format in configuration file '" + filename + "' at line " + str(counter))
        
        name,getter,setter,typename = toks[:4]
        tp,keys,defval,descr = toks[4:]

        if not tp in ["str","bool","int","float"]:
            error("'" + tp + "' is not a supported type")
        
        oargs.update({ name: oarg.Oarg(eval(tp),str(keys),eval(tp)(defval),str(descr)) })
        sys_states_descr.update({ name: st.SysState(getter,setter,type(typename)) })

        counter += 1
    f.close()

    return oargs,sys_states_descr

def setCmdStates(filename,n_toks=5):
    oargs = {}
    cmdline_states_descr = {}
    counter = 1

    f = open(filename,"r")
    for line in f:
        line = line.replace("\n","").strip()
    
        if line == "" or line[0] == "#":
            continue

        toks = line.split(",")
        if len(toks) != n_toks:
            error("wrong format in configuration file '" + filename + "' at line " + str(counter))

        name,cmd,priority = toks[:3]
        keys,descr = toks[3:]
        
        oargs.update({ name: oarg.Oarg(bool,str(keys),True,str(descr)) })
        cmdline_states_descr.update({ name: st.CmdState(cmd.split(),int(priority)) })

        counter += 1

    f.close()
    return oargs,cmdline_states_descr

def extractRoutine():
    states_dirs = [work_dir.getVal() + "/" + STATES_DIR_NAME + "/" + d for d in os.listdir(work_dir.getVal() + "/" + STATES_DIR_NAME)]
    apps_dirs = [sd + "/" + APPS_DIR_NAME + "/" + d for sd in states_dirs for d in os.listdir(sd + "/" + APPS_DIR_NAME)]

    for d in apps_dirs:
        info("in dir '" + d + "' ...")
        for ext in extractors:
            info("using extractor '" + ext.name + "' ...")
            line = []
            line.append(ext.name)

            info("filtering files to use ...")
            filenames = [d + "/" + app.LOGS_DIR + "/" + f for f in os.listdir(d + "/" + app.LOGS_DIR) if f.find(ext.filter_key) >= 0]
            for fn in filenames:
                info("extracting information from '" + fn + "' ...")
                src = open(fn,"r")
                ext.extract(source=src)
                src.close()
                line.append(ext.out.replace("\n",""))

            info("writing in file '" + d + "/" + VALS_FILE_TRANSPOSED + "' ...")
            f = open(d + "/" + VALS_FILE_TRANSPOSED,"a" if extractors.index(ext) > 0 else "w")
            f.write(",".join(line) + "\n")
            f.close()

        info("transposing '" + d + "/" + VALS_FILE_TRANSPOSED + "' ...")
        transposeCSV(d + "/" + VALS_FILE_TRANSPOSED,d + "/" + VALS_FILE)
        print ""

def runRoutine():
    counter = 1
    for ssv in sys_states_vals:
        for csv in cmdline_states_vals:
            info("ITERATION " + str(counter) + ":")

            info("setting system states...")
            for s,v in zip(sys_states,ssv):
                s.val = v 

            info("setting command line states...")
            for s,v in zip(cmdline_states,csv):
                s.val = v

            info("state values:")
            for k,s in sys_states_descr.iteritems():
                print "\t\t" + k,":",s.val
            for k,s in cmdline_states_descr.iteritems():
                print "\t\t" + k,":",s.val

            curr_state_dir = work_dir.getVal() + "/" + STATES_DIR_NAME + "/" + str(counter)
            info("creating directory '" + curr_state_dir + "' ...")
            if not os.path.isdir(curr_state_dir):
                os.makedirs(curr_state_dir)
            
            info("creating state info file '" + curr_state_dir + "/" + STATE_DESCR_FILE + "' ...")
            f = open(curr_state_dir + "/" + STATE_DESCR_FILE, "w")
            f.write(",".join(sys_states_keys + cmdline_states_keys) + "\n")
            f.write(",".join([str(s.val) for s in sys_states] + [str(s.val) for s in cmdline_states]) + "\n")
            f.close()

            for tgt in targets:
                tgt_dir = curr_state_dir + "/" + APPS_DIR_NAME + "/" + tgt.name
                info("creating app dir '" + tgt_dir + "' ...")
                if not os.path.isdir(tgt_dir):
                    os.makedirs(tgt_dir) 

                info("creating logs dir '" + tgt_dir + "/" + app.LOGS_DIR + "' ...")
                if not os.path.isdir(tgt_dir + "/" + app.LOGS_DIR):
                    os.makedirs(tgt_dir + "/" + app.LOGS_DIR)

                for i in range(1,n_reps.getVal()+1):
                    info("running app '" + tgt.name + "' (" + str(i) + " of " + str(n_reps.getVal()) + ") ...")
                    tgt.run(cmdstate=True)

                    tgt_out_log = "/".join([tgt_dir,app.LOGS_DIR,str(i) + "_" + app.STDOUT_LOG])
                    tgt_err_log = "/".join([tgt_dir,app.LOGS_DIR,str(i) + "_" + app.STDERR_LOG])

                    info("dumping result stdout to '" + tgt_out_log + "' ...")
                    info("dumping result stderr to '" + tgt_err_log + "' ...")
                    of,ef = open(tgt_out_log,"w"),open(tgt_err_log,"w")
                    tgt.dump(out=of,err=ef)
                    of.close()
                    ef.close() 

            counter += 1
            print ""

if __name__ == "__main__":
    #parsing
    oarg.parse()

    if not action.wasFound():
        if hlp.getVal():
            info("usage: baut [ACTION] {OPTIONS}\navaliable actions:\n\t" + "\n\t".join(actions))
            oarg.describeArgs("avaliable options:")
            exit()
        else:
            error("no action specified\nuse '--help' for more information")

    #reloading oarg
    oarg = reload(oarg)

    if action.getVal() == "run":
        from itertools import product
        from time import sleep

        baut_key = "[baut::run]"

        hlp             = oarg.Oarg(bool,"-h --help",False,"This help message")
        work_dir        = oarg.Oarg(str,"-w --work-dir",DEF_TESTS_DIR_NAME,"Directory to save results")
        n_reps          = oarg.Oarg(int,"-r --reps --repetitions",1,"Number of repetitions for each iteration")
        sliding         = oarg.Oarg(bool,"-s --sliding",False,"Activates sliding system states mode")
        apps            = oarg.Oarg(str,"-a --apps","","Apps directories list")

        #keys sys states
        sys_states_oargs,sys_states_descr = setSysStates(sys_states_file.getVal())
        #keys cmd states
        cmdline_states_oargs,cmdline_states_descr = setCmdStates(cmd_states_file.getVal())

        if oarg.parse() != 0 and not all( i in opts for i in oarg.Oarg.invalid_options ):
             error("invalid options passed: " + ",".join(["'" + word + "'" for word in oarg.Oarg.invalid_options if not word in opts]))

        if hlp.getVal():
            info("available options:")
            oarg.describeArgs()
            exit()

        if not apps.wasFound():
            error("no apps specified") 

        #setting up apps
        targets = [app.App(path) for path in apps.vals if path != ""]

        #setting sys states
        sys_states_keys = [key for key in sys_states_oargs]
        _sys_states_vals = [sys_states_oargs[k].vals for k in sys_states_keys]
        sys_states = [sys_states_descr[k] for k in sys_states_keys]

        if sliding.getVal():
            if len(set([len(i) for i in _sys_states_vals])) != 1:
                error("Invalid arguments passed")
            sys_states_vals = zip(_sys_states_vals)
        else:
            sys_states_vals = list(product(*_sys_states_vals))

        #setting cmd states
        cmdline_states_keys = [key for key in cmdline_states_oargs]
        _cmdline_states_vals = [cmdline_states_oargs[k].vals for k in cmdline_states_keys]
        cmdline_states_vals = list(product(*_cmdline_states_vals))
        cmdline_states = [cmdline_states_descr[k] for k in cmdline_states_keys]
    
        #number of iterations
        n_its = len(sys_states_vals) * len(cmdline_states_vals) * n_reps.getVal()
        
        #running apps
        info("will run " + str(n_its) + " iterations ...\n")
        sleep(3)
        runRoutine()
        exit()

    elif action.getVal() == "extract":
        baut_key = "[baut::extract]"

        #args
        hlp      = oarg.Oarg(bool,"-h --help",False,"This help message")
        work_dir = oarg.Oarg(str,"-w --work-dir",DEF_TESTS_DIR_NAME,"Directory to extract results")
        exts     = oarg.Oarg(str,"--exts","","Extractors paths")

        if oarg.parse() != 0 and not all( i in opts for i in oarg.Oarg.invalid_options ):
             error("invalid options passed: " + ",".join(["'" + word + "'" for word in oarg.Oarg.invalid_options if not word in opts]))

        if hlp.getVal():
            info("available options:")
            oarg.describeArgs()
            exit()

        if not exts.wasFound():
            error("no extractors specified")
        if not work_dir.wasFound():
            error("no target directory specified")

        extractors = [app.Extractor(path) for path in exts.vals if path != ""]

        extractRoutine()
        exit()

    else:
        error("invalid action specified.\nuse '--help' for more information")
