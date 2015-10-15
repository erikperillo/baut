#!/usr/bin/python2.7

import oarg2 as oarg
import core.app as app
import core.state as st
import subprocess as sp
import os

#definitions
FILE_DIR                  = os.path.dirname(os.path.realpath(__file__))
TOOLS_DIR                 = FILE_DIR + "/" + "tools"
DEF_TESTS_DIR             = FILE_DIR + "/" + "tests" + "/" + "".join(sp.Popen([TOOLS_DIR + "/date/" + "get_date_footprint.sh"],stdout=sp.PIPE).communicate()[0].splitlines())
STATES_DIR_NAME           = "states"
APPS_DIR_NAME             = "apps"
STATE_DESCR_FILE_NAME     = "state.csv"
NUMABAL_COMMOM_PATH       = "/proc/sys/kernel"
NUMABAL_CONFIG_FILE       = FILE_DIR + "/" + "tools/numa/numa_bal_config.py"
VALS_FILE_NAME            = "raw_vals.csv"
VALS_RESUME_FILE          = "vals_resume.csv"
VALS_FILE_NAME_TRANSPOSED = "raw_vals_transposed.csv"
DEF_SYSSTATES_FILE        = FILE_DIR + "/" + "confs/sys_states.csv"
DEF_CMDSTATES_FILE        = FILE_DIR + "/" + "confs/cmd_states.csv"
ELAPSED_TIME_FILE_NAME    = "elapsed_s"
APP_STATS_DIR_NAME        = "stats"
STATES_STATS_DIR_NAME     = "stats"
PLOTS_DIR_NAME            = "plots"
PLOTS_FILES_EXT           = ".pdf"
ALL_FIGS_PLOT_FILE_NAME   = "all" 

#available actions
actions = ["run","extract","stats","plot"]

#key for info method
baut_key = "[baut]"

#command line arguments
action          = oarg.Oarg(str,"-action","","Action to execute",0)
quiet           = oarg.Oarg(bool,"-q -quiet",False,"Does not run so verbose")
sys_states_file = oarg.Oarg(str,"-sf -sys-states-file",DEF_SYSSTATES_FILE,"System states file (run mode)")
cmd_states_file = oarg.Oarg(str,"-cf -cmd-states-file",DEF_CMDSTATES_FILE,"Command line states file (run mode)")
hlp             = oarg.Oarg(bool,"-h -help",False,"This help message")

#options
opts            = ["-cf","-cmd-states-file","-sf","-sys-states-file","-q","-quiet","-action"]

def info(msg, quiet=False):
    if not quiet:
        print baut_key + " " + msg

def error(msg, errn=1):
    info("error: " + msg)
    exit(errn)

def strTrue(string, falses=["0","no","n","false"]):
    return not string.lower() in falses

def transposeCSV(file_in, file_out):
    import csv

    f,ft = open(file_in,"r"),open(file_out,"w")

    rows = list(csv.reader(f))
    writer = csv.writer(ft)
    for col in xrange(0, len(rows[0])):
        writer.writerow([row[col] for row in rows]) 

    f.close()
    ft.close()

def setSysStates(filename, n_toks=8):
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

def setCmdStates(filename, n_toks=6):
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
        estim_success = tgt.struct_dir != None
        if tgt.struct_dir != None:
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
                estim_success = False
        if not estim_success:
            info("warning: could not get time estimation for app '" + tgt.name + "'")

    return total_time

def formatTime(seconds):
    seconds = int(seconds) 
    hours = seconds / 3600
    minutes = (seconds % 3600) / 60
    seconds = seconds % 60 
    return hours,minutes,seconds

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
                with open(fn,"r") as src:
                    ext.extract(source=src)

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

                if tgt.struct_dir != None:
                    info("creating file '" + tgt_dir + "/" + app.PATH_FILENAME + "' for later reference...")
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

def statsRoutine():
    states_dirs = [os.path.abspath(work_dir.val) + "/" + STATES_DIR_NAME + "/" + d for d in os.listdir(os.path.abspath(work_dir.val) + "/" + STATES_DIR_NAME)]

    for sd in states_dirs: 
        state_stats_dir = sd + "/" + STATES_STATS_DIR_NAME
        if not os.path.isdir(state_stats_dir):
            info("creating directory '" + state_stats_dir + "' ...")
            os.makedirs(state_stats_dir)

        apps_dirs = [sd + "/" + APPS_DIR_NAME + "/" + d for d in os.listdir(sd + "/" + APPS_DIR_NAME)]

        for ad in apps_dirs:
            app_stats_dir = ad + "/" + APP_STATS_DIR_NAME

            if not os.path.isdir(app_stats_dir):
                info("creating directory '" + app_stats_dir + "' ...")
                os.makedirs(app_stats_dir)

            info("reading data in '" + app_stats_dir + "' ...")
            with open(ad + "/" + VALS_FILE_NAME_TRANSPOSED,"r") as csv_file:
                for line in csv_file:
                    toks = line.replace("\n","").split(",")
                    name = toks[0]
                    vals = [float(t) for t in toks[1:] if t != ""]
                    measures = dict( (key,stats.ops[key](vals)) for key in stat_measures.vals ) 
                    
                    info("writing stats to '" + app_stats_dir + "/" + name + ".csv" + "' ...")
                    with open(app_stats_dir + "/" + name + ".csv","w") as f:
                        f.write(",".join([ key for key in measures ]) + "\n")
                        f.write(",".join([ str(measures[key]) for key in measures ]) + "\n") 
                    
                    if not os.path.isfile(state_stats_dir + "/" + name + ".csv"):
                        info("creating file '" + state_stats_dir + "/" + name + ".csv" + "' ...")
                        with open(state_stats_dir + "/" + name + ".csv","w") as f:
                            f.write(",".join(["app"] + [key for key in measures]) + "\n")

                    info("writing stats to '" + state_stats_dir + "/" + name + ".csv" + "' ...")
                    with open(state_stats_dir + "/" + name + ".csv","a") as sf:
                        sf.write(",".join([os.path.basename(ad)] + [str(measures[key]) for key in measures ]) + "\n")
                 

def plotRoutine():
    plot_colors = [tuple([k*i for i in (a,b,c)]) for k in (1,0.5) for (a,b,c) in [(0,0,1),(0,1,0),(1,0,0),(0,1,1),(1,1,0),(0,1,0)]]
    plots_dir = os.path.abspath(work_dir.val + "/" + PLOTS_DIR_NAME)

    if not os.path.isdir(plots_dir):
        info("creating directory '" + plots_dir + "' ...")
        os.makedirs(plots_dir)

    states_dirs = [os.path.abspath(work_dir.val) + "/" + STATES_DIR_NAME + "/" + d for d in os.listdir(os.path.abspath(work_dir.val) + "/" + STATES_DIR_NAME)]

    x_vals = []
    y_vals = {}
    
    for sd in states_dirs:
        info("working in '" + sd + "' ...")
        with open(sd + "/" + STATE_DESCR_FILE_NAME,"r") as state_file:
            states_names = state_file.readline().replace("\n","").split(",")
            if not x_axis.val in states_names:
                error("no such state '" + x_axis.val + "' in file '" + sd + "/" + STATE_DESCR_FILE_NAME)
            index = states_names.index(x_axis.val)
            states_vals = state_file.readline().replace("\n","").split(",")
            x_vals.append(float(states_vals[index]))    

        apps_dirs = [sd + "/" + APPS_DIR_NAME + "/" + d for d in os.listdir(sd + "/" + APPS_DIR_NAME)]
        for ad in apps_dirs:
            app_name = os.path.basename(ad)

            info("getting info about app '" + app_name + "' ...")
            if not app_name in y_vals:
                y_vals[app_name] = []

            app_stats_dir = ad + "/" + APP_STATS_DIR_NAME
            with open(app_stats_dir + "/" + y_axis.val + ".csv","r") as yval_file:
                stats_names = yval_file.readline().replace("\n","").split(",")
                if not y_stat.val in stats_names:
                    error("no such statistical measure '" + y_stat.val + "' in file '" + app_stats_dir + "/" + y_axis.val + ".csv")
                index = stats_names.index(y_stat.val)
                stats_vals = yval_file.readline().replace("\n","").split(",")
                stat_value = float(stats_vals[index])

                if y_err.found:
                    if not y_err.val in stats_names:
                        error("no such statistical measure '" + y_err.val + "' in file '" + app_stats_dir + "/" + y_axis.val + ".csv")
                    index = stats_names.index(y_err.val)
                    y_vals[app_name].append((stat_value,float(stats_vals[index])))
                else:
                    y_vals[app_name].append((stat_value,0))

    info("sorting values...")
    for key in y_vals:
        y_vals[key] = [ y for (x,y) in sorted(zip(x_vals,y_vals[key])) ]
    x_vals.sort()

    to_plot = [(key,) for key in y_vals]
    to_plot += [sum(to_plot,())] if len(y_vals) > 1 else []

    info("plotting...")
    for ylabels in to_plot:
        for key,color in zip(ylabels,plot_colors):
            Y = [ i for i,_ in y_vals[key] ]
            Y_errs = [ i for _,i in y_vals[key] ]
            pylab.errorbar(x_vals,Y,yerr=Y_errs,color=color,ecolor="r",label=key)

        pylab.xlabel(x_axis.val)
        pylab.ylabel(y_axis.val + " " + y_stat.val)
        pylab.xticks(x_vals)
        pylab.legend() 
        pylab.grid()

        filename = (ylabels[0] if len(ylabels) == 1 else ALL_FIGS_PLOT_FILE_NAME) + "_" + x_axis.val + "_vs_" + y_axis.val + PLOTS_FILES_EXT
        info("saving plot to '" + work_dir.val + "/" + PLOTS_DIR_NAME + "/" + filename + "' ...")
        pylab.savefig(work_dir.val + "/" + PLOTS_DIR_NAME + "/" + filename, bbox_inches="tight")

        if (len(ylabels) > 1 or len(y_vals) == 1) and show_plot.val:
            info("displaying resume of results:")
            pylab.show()    

    info("all results saved to '" + work_dir.val + "/" + PLOTS_DIR_NAME + "'")

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
        targets = [app.App(path) if os.path.isdir(path) else app.App(cmd=path.split()) for path in apps.vals]

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
        hours,minutes,seconds = [str(t) for t in formatTime(estimatedTime())]
        info("estimated time is " + hours + "h" + minutes + "m" + seconds + "s")
        
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

    elif action.val == "stats":
        import core.stats as stats

        baut_key = "[baut::stats]"

        hlp             = oarg.Oarg(bool,"-h -help",False,"This help message")
        work_dir        = oarg.Oarg(str,"-w -work-dir","","Directory to extract results")
        stat_measures   = oarg.Oarg(str,"-m -measures","mean","Statistical measures to use")

        try:
            oarg.parse()
        except oarg.UnknownOptionsError as e:
            if not all(opt in opts for opt in e.opts):
                raise e

        if hlp.val:
            info("available command line options:")
            oarg.describeArgs()
            print "\navailable measures:\n" + "\n".join([ "\t" + k for k in stats.ops ]) 
            exit()

        if not work_dir.found:
            error("no target directory specified")

        if stat_measures.val == "all":
            stat_measures.vals = tuple(k for k in stats.ops)
        elif not all(m in stats.ops for m in stat_measures.vals):
            error("invalid statistical measure\nuse '-help' for more information")

        info("will resume in directory '" + work_dir.val + "' ...")
        statsRoutine()
        exit()

    elif action.val == "plot":
        import pylab 

        baut_key = "[baut::plot]"

        hlp             = oarg.Oarg(bool,"-h -help",False,"This help message")
        work_dir        = oarg.Oarg(str,"-w -work-dir","","Directory to extract results")
        x_axis          = oarg.Oarg(str,"-x","","x axis field name to be used")
        y_axis          = oarg.Oarg(str,"-y","","y axis field name to be used")
        y_stat          = oarg.Oarg(str,"-ystat","mean","y axis statistical value to be used")
        y_err           = oarg.Oarg(str,"-yerr","","y axis error field name to be used")
        show_plot       = oarg.Oarg(bool,"-show",False,"Show all plots on screen when finished")

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
        if not x_axis.found:
            error("no axis x name specified")
        if not y_axis.found:
            error("no axis y name specified")

        info("will plot fields in directory '" + work_dir.val + "' ...")
        plotRoutine()
        exit()

    else:
        error("invalid action '" + action.val + "' specified.\nuse '-help' for more information")
