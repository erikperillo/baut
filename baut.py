#!/usr/bin/python2.7

import oarg2 as oarg
import core.app as app
import core.state as st
import subprocess as sp
import os

#definitions
FILE_DIR                    = os.path.dirname(os.path.realpath(__file__))
TOOLS_DIR                   = FILE_DIR + "/" + "tools"
DEF_TESTS_DIR               = FILE_DIR + "/" + "tests" + "/" + "".join(sp.Popen([TOOLS_DIR + "/date/" + "get_date_footprint.sh"],stdout=sp.PIPE).communicate()[0].splitlines())
STATES_DIR_NAME             = "states"
APPS_DIR_NAME               = "apps"
STATE_DESCR_FILE_NAME       = "state.csv"
NUMABAL_COMMOM_PATH         = "/proc/sys/kernel"
NUMABAL_CONFIG_FILE         = FILE_DIR + "/" + "tools/numa/numa_bal_config.py"
VALS_FILE_NAME              = "raw_vals.csv"
VALS_RESUME_FILE            = "vals_resume.csv"
VALS_FILE_NAME_TRANSPOSED   = "raw_vals_transposed.csv"
DEF_SYSSTATES_FILE          = FILE_DIR + "/" + "confs/sys_states.csv"
DEF_CMDSTATES_FILE          = FILE_DIR + "/" + "confs/cmd_states.csv"
COMPD_APP                   = FILE_DIR + "/" + "tools/perftool/compd.py"
ELAPSED_TIME_FILE_NAME      = "elapsed_s"

#available actions
actions = ["run","extract","resume"]

#key for info method
baut_key = "[baut]"

#compd default string
compd_def_str = "(ds-av) (ds-ci)"

#command line arguments
action          = oarg.Oarg(str,"-action","","Action to execute",0)
quiet           = oarg.Oarg(bool,"-q -quiet",False,"Does not run so verbose")
sys_states_file = oarg.Oarg(str,"-sf -sys-states-file",DEF_SYSSTATES_FILE,"System states file (run mode)")
cmd_states_file = oarg.Oarg(str,"-cf -cmd-states-file",DEF_CMDSTATES_FILE,"Command line states file (run mode)")
hlp             = oarg.Oarg(bool,"-h -help",False,"This help message")

#options
opts            = ["-cf","-cmd-states-file","-sf","-sys-states-file","-q","-quiet","-action"]

def info(msg,quiet=False):
    if not quiet:
        print baut_key + " " + msg

def error(msg,errn=1):
    info("error: " + msg)
    exit(errn)

def strTrue(string,falses=["0","no","n","false"]):
    return not string.lower() in falses

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

def setCmdStates(filename,n_toks=6):
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

        name,cmd,def_active,priority = toks[:4]
        keys,descr = toks[4:]
        
        oargs.update({ name: oarg.Oarg(bool,str(keys),strTrue(def_active),str(descr)) })
        cmdline_states_descr.update({ name: st.CmdState(cmd.split(),int(priority)) })

        counter += 1

    f.close()
    return oargs,cmdline_states_descr

def estimatedTime():
    n_its = len(sys_states_vals) * len(cmdline_states_vals) * n_reps.val
    total_time = 0.0

    for tgt in targets:
        times_file = tgt.struct_dir + "/" + app.STATS_DIR_NAME + "/" + ELAPSED_TIME_FILE_NAME
        if os.path.isfile(os.path.abspath(times_file)):
            partial_time = 0.0
            counter = 0
            f = open(times_file,"r")
            for line in f:
                partial_time += float(line) if line != "" else 0.0
                counter += 1
            f.close()
            total_time += n_its * (partial_time / counter)
        else:
            info("warning: could not get time estimation for app '" + tgt.name + "'")

        return total_time

def extractRoutine():
    states_dirs = [work_dir.val + "/" + STATES_DIR_NAME + "/" + d for d in os.listdir(work_dir.val + "/" + STATES_DIR_NAME)]
    apps_dirs = [sd + "/" + APPS_DIR_NAME + "/" + d for sd in states_dirs for d in os.listdir(sd + "/" + APPS_DIR_NAME)]

    for d in apps_dirs:
        info("in dir '" + d + "' ...")

        if app_dir_save.val:
            f = open(d + "/" + app.PATH_FILENAME,"r")
            app_run_dir = f.read()
            f.close()
            if not os.path.isdir(app_run_dir + "/" + app.STATS_DIR_NAME):
                info("creating stats dir '" + app_run_dir + "/" + app.STATS_DIR_NAME + "' ...")
                os.makedirs(app_run_dir + "/" + app.STATS_DIR_NAME)
            
        for ext in extractors:
            info("using extractor '" + ext.name + "' ...")
            line = []
            line.append(ext.name)

            if app_dir_save.val:
                if os.path.isfile(app_run_dir + "/" + app.STATS_DIR_NAME + "/" + ext.name) and app_stats_clear.val:
                    os.remove(app_run_dir + "/" + app.STATS_DIR_NAME + "/" + ext.name)

                sf = open(app_run_dir + "/" + app.STATS_DIR_NAME + "/" + ext.name,"a")
                info("will write info to '" + app_run_dir + "/" + app.STATS_DIR_NAME + "/" + ext.name + "' ...")

            info("filtering files to use ...")
            filenames = [d + "/" + app.LOGS_DIR + "/" + f for f in os.listdir(d + "/" + app.LOGS_DIR) if f.find(ext.filter_key) >= 0]
            for fn in filenames:
                info("extracting information from '" + fn + "' ...")
                src = open(fn,"r")
                ext.extract(source=src)
                src.close()
                line.append(ext.out.replace("\n",""))
                
                if app_dir_save.val:
                    sf.write(line[-1] + "\n")
            
            if app_dir_save.val:
                sf.close()

            info("writing in file '" + d + "/" + VALS_FILE_NAME_TRANSPOSED + "' ...")
            f = open(d + "/" + VALS_FILE_NAME_TRANSPOSED,"a" if extractors.index(ext) > 0 else "w")
            f.write(",".join(line) + "\n")
            f.close()

        info("transposing '" + d + "/" + VALS_FILE_NAME_TRANSPOSED + "' ...")
        transposeCSV(d + "/" + VALS_FILE_NAME_TRANSPOSED,d + "/" + VALS_FILE_NAME)
        print ""

def runRoutine():
    counter = 1
    for ssv in sys_states_vals:
        for csv in cmdline_states_vals:
            info("STATE " + str(counter) + ":")

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

            curr_state_dir = work_dir.val + "/" + STATES_DIR_NAME + "/" + str(counter)
            info("creating directory '" + curr_state_dir + "' ...")
            if not os.path.isdir(curr_state_dir):
                os.makedirs(curr_state_dir)
            
            info("creating state info file '" + curr_state_dir + "/" + STATE_DESCR_FILE_NAME + "' ...")
            f = open(curr_state_dir + "/" + STATE_DESCR_FILE_NAME, "w")
            f.write(",".join(sys_states_keys + cmdline_states_keys) + "\n")
            f.write(",".join([str(s.val) for s in sys_states] + [str(s.val) for s in cmdline_states]) + "\n")
            f.close()

            for tgt in targets:
                tgt_dir = curr_state_dir + "/" + APPS_DIR_NAME + "/" + tgt.name
                info("creating app dir '" + tgt_dir + "' ...")
                if not os.path.isdir(tgt_dir):
                    os.makedirs(tgt_dir) 

                info("creating file '" + tgt_dir + "/" + app.PATH_FILENAME + "' dir for later reference...")
                f = open(tgt_dir + "/" + app.PATH_FILENAME,"w")
                f.write(os.path.abspath(tgt.struct_dir))
                f.close()

                info("creating logs dir '" + tgt_dir + "/" + app.LOGS_DIR + "' ...")
                if not os.path.isdir(tgt_dir + "/" + app.LOGS_DIR):
                    os.makedirs(tgt_dir + "/" + app.LOGS_DIR)

                for i in range(1,n_reps.val+1):
                    info("running app '" + tgt.name + "' (" + str(i) + " out of " + str(n_reps.val) + ") ...")
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

def resumeRoutine():
    states_dirs = [work_dir.val + "/" + STATES_DIR_NAME + "/" + d for d in os.listdir(work_dir.val + "/" + STATES_DIR_NAME)]
    apps_dirs = [sd + "/" + APPS_DIR_NAME + "/" + d for sd in states_dirs for d in os.listdir(sd + "/" + APPS_DIR_NAME)]
    
    compd_fmt_str = compd_arg_str.val.replace(","," ") if compd_arg_str.found else compd_def_str

    for d in apps_dirs:
        info("reading data...")
        fd = open(d + "/" + VALS_FILE_NAME,"r")
        header = fd.read().replace("\n","").split(",")
        fd.close()

        info("creating file '" + d + "/" + VALS_RESUME_FILE + "' ...")
        fr = open(d + "/" + VALS_RESUME_FILE,"a")

        for elem in header:
            try:
                proc = sp.Popen([COMPD_APP,"--ds",d + "/" + VALS_FILE_NAME,"--cf","elapsed_s","--of"] + ([compd_arg_str.val.replace(","," ")] if compd_arg_str.found else ["(ds-av) (ds-ci)"]),stdout=sp.PIPE,stderr=sp.PIPE)
                proc.wait()
                info("result for '" + elem + "' in '" + d + "':")
                ret = proc.communicate()[0]
            except ZeroDivisionError:
                ret = ["0"] * len(compd_fmt_str) 
                pass 

            line = elem + "," + ",".join(ret.split())
            fr.write(line)

        fr.close()

if __name__ == "__main__":
    #parsing

    try:
        oarg.parse()
    except oarg.UnknownOptionsError:
        pass

    if not action.found:
        if hlp.val:
            info("usage: baut [ACTION] {OPTIONS}\n\navailable actions:\n\t" + "\n\t".join(actions))
            oarg.describeArgs("\navailable options:")
            exit()
        else:
            error("no action specified\nuse '-help' for more information")

    #refreshing oarg
    oarg = reload(oarg)

    if action.val == "run":
        from itertools import product
        from time import sleep

        baut_key = "[baut::run]"

        hlp             = oarg.Oarg(bool,"-h -help",False,"This help message")
        work_dir        = oarg.Oarg(str,"-w -work-dir",DEF_TESTS_DIR,"Directory to save results")
        n_reps          = oarg.Oarg(int,"-r -reps --repetitions",1,"Number of repetitions for each iteration") 
        sliding         = oarg.Oarg(bool,"-s -sliding",False,"Activates sliding system states mode")
        apps            = oarg.Oarg(str,"-a -apps","","Apps directories list")

        #keys sys states
        sys_states_oargs,sys_states_descr = setSysStates(sys_states_file.val)
        #keys cmd states
        cmdline_states_oargs,cmdline_states_descr = setCmdStates(cmd_states_file.val)

        try:
            oarg.parse()
        except oarg.UnknownOptionsError as e:
            if not all(opt in opts for opt in e.opts):
                raise e

        if hlp.val:
            info("available options:")
            oarg.describeArgs()
            exit()

        if not apps.found:
            error("no apps specified") 

        #setting up apps
        targets = [app.App(path) for path in apps.vals if path != ""]

        #setting sys states
        sys_states_keys = [key for key in sys_states_oargs]
        _sys_states_vals = [sys_states_oargs[k].vals for k in sys_states_keys]
        sys_states = [sys_states_descr[k] for k in sys_states_keys]

        if sliding.val:
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
        n_its = len(sys_states_vals) * len(cmdline_states_vals) * n_reps.val
        #estimating time
        info("estimated time is " + str(estimatedTime()) + " seconds")
        
        #running apps
        info("will run " + str(n_its) + " iterations ...\n")
        sleep(3)
        runRoutine()
        exit()

    elif action.val == "extract":
        baut_key = "[baut::extract]"

        #args
        hlp             = oarg.Oarg(bool,"-h -help",False,"This help message")
        work_dir        = oarg.Oarg(str,"-w -work-dir","","Directory to extract results")
        exts            = oarg.Oarg(str,"-exts","","Extractors paths")
        app_dir_save    = oarg.Oarg(bool,"-record",False,"Records results in apps stats directory")
        app_stats_clear = oarg.Oarg(bool,"-clear",False,"Clear app stats dir")

        try:
            oarg.parse()
        except oarg.UnknownOptionsError as e:
            if not all(opt in opts for opt in e.opts):
                raise e

        if hlp.val:
            info("available options:")
            oarg.describeArgs()
            exit()

        if not exts.found:
            error("no extractors specified")
        if not work_dir.found:
            error("no target directory specified")

        extractors = [app.Extractor(path) for path in exts.vals if path != ""]

        extractRoutine()
        exit()

    elif action.val == "resume":
        #import pylab

        baut_key = "[baut::resume]"

        hlp      = oarg.Oarg(bool,"-h -help",False,"This help message")
        work_dir = oarg.Oarg(str,"-w -work-dir","","Directory to extract results")
        compd_arg_str   = oarg.Oarg(str,"-s -compd-str","","Compd string to pass directly to program")

        try:
            oarg.parse()
        except oarg.UnknownOptionsError as e:
            if not all(opt in opts for opt in e.opts):
                raise e

        if hlp.val:
            info("available options:")
            oarg.describeArgs()
            exit()

        if not work_dir.found:
            error("no target directory specified")

        info("not completely implemented yet")
        #info("will resume in directory '" + work_dir.val + "' ...")
        #resumeRoutine()
        exit()

    else:
        error("invalid action '" + action.val + "' specified.\nuse '-help' for more information")
