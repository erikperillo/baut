import tools.oarg as oarg
import core.app as app
import core.state as st
import subprocess as sp
import os

TOOLS_DIR_NAME = "tools"
DEF_TESTS_DIR_NAME = "tests" + "/" + "".join(sp.Popen([TOOLS_DIR_NAME + "/date/" + "get_date_footprint.sh"],stdout=sp.PIPE).communicate()[0].splitlines())
STATES_DIR_NAME = "states"
APPS_DIR_NAME = "apps"
STATE_DESCR_FILE = "state.csv"
BENCHMARK_APPS_DIR_NAME = "apps"
NUMABAL_COMMOM_PATH = "/proc/sys/kernel"
NUMABAL_CONFIG_FILE = "tools/numa/numa_bal_config.py"
TIMES_FILE = "times"

def info(msg,quiet=False):
    if not quiet:
        print "[baut] " + msg

def error(msg,errn=1):
    info("error: " + msg)
    exit(errn)

#command line states
timer_cmd = st.CmdState(["/usr/bin/time","-f","timer_real: %e"],active=True)
#time extractor
timer = app.Extractor("testext")

#application specific
#numabal_keys = ("numa_balancing","numa_balancing_migrate_deferred","numa_balancing_settle_count","numa_balancing_scan_size_mb","numa_balancing_scan_period_min_ms","numa_balancing_scan_delay_ms","numa_balancing_scan_period_max_ms")
numabal_keys = ("numa_balancing","numa_balancing_scan_size_mb","numa_balancing_scan_period_min_ms","numa_balancing_scan_delay_ms","numa_balancing_scan_period_max_ms")
#numabal_config_flags = ("-a","--md","--sc","--ss","--spmin","--sd","--spmax")
numabal_config_flags = ("-a","--ss","--spmin","--sd","--spmax")

#states
sys_states_descr = dict([ (key, st.SysState(getter=["tools/rmv_newline.sh",NUMABAL_COMMOM_PATH + "/" + key],\
                          setter=["sudo",NUMABAL_CONFIG_FILE,flag])) for key,flag in zip(numabal_keys,numabal_config_flags) ])
cmdline_states_descr = {"interleave": st.CmdState("--interleave=all")}

#arguments
apps            = oarg.Oarg(str,"-a --apps","","Apps directories list")
benchmark       = oarg.Oarg(str,"-b --benchmark","","Benchmark directory")
sliding         = oarg.Oarg(bool,"-s --sliding",False,"Sliding arguments mode")
interleave      = oarg.Oarg(str,"-i --interleave",False,"Activates Interleaving policy")
work_dir        = oarg.Oarg(str,"-w --work-dir",DEF_TESTS_DIR_NAME,"Directory to save results")
quiet           = oarg.Oarg(bool,"-q --quiet",False,"Does not run so verbose")
numa_bal        = oarg.Oarg(bool,"-n --numa-balancing",False,"Activates automatic NUMA balancing")
#nb_migrate_def	= oarg.Oarg(int,"--md --migrate-deferred",16,"Automatic NUMA balancing migrate deferred")
#nb_settle_count	= oarg.Oarg(int,"--sc --settle-count",4,"Automatic NUMA balancing settle count")
nb_scan_size    = oarg.Oarg(int,"--ss --scan-size",256,"Automatic NUMA balancing scan size")
nb_sp_min       = oarg.Oarg(int,"--spmin --scan-period-min",1000,"Automatic NUMA balancing scan period min")
nb_scan_delay   = oarg.Oarg(int,"--sd --scan-delay",1000,"Automatic NUMA balancing scan delay")
nb_sp_max       = oarg.Oarg(int,"--spmax --scan-period-max",60000,"Automatic NUMA balancing scan period max")
n_reps          = oarg.Oarg(int,"--reps --repetitions",1,"Number of repetitions for each iteration")
hlp             = oarg.Oarg(bool,"-h --help",False,"This help message")

#dictionary for numa balancing parameters
#nb_options = [nb_migrate_def,nb_settle_count,nb_scan_size,nb_sp_min,nb_scan_delay,nb_sp_max]
nb_options = [nb_scan_size,nb_sp_min,nb_scan_delay,nb_sp_max]
interleave_options = [interleave]

#parsing and checking for wrong options
if oarg.parse() != 0:
     error("Invalid options passed: " + ",".join(["'" + word + "'" for word in oarg.Oarg.invalid_options]))

#help message
if hlp.getVal():
    info("Available options:")
    oarg.describeArgs()
    exit()

#setting up apps
if apps.wasFound():
    targets = [app.App(benchmark.getVal() + path) for path in apps.vals if path != ""]
elif benchmark.wasFound():
	targets = [d for d in os.listdir(benchmark + "/" + BENCHMARK_APPS_DIR_NAME) if d[0] != "."]
else:
    error("No applications specified\nUse '--help' for more information")

#setting up numa balancing parameters list
if sliding.getVal():
    if len(set([len(arg.vals) for arg in nb_options])) != 1:
        error("Invalid arguments passed")
    nb_params = zip(len(nb_scan_size.vals)*(numa_bal.getVal(),),*[arg.vals for arg in nb_options])
else:
    #nb_params = [ (nb,md,sc,ss,spmin,sd,spmax) for nb in numa_bal.vals for md in nb_migrate_def.vals for sc in nb_settle_count.vals for sd in nb_scan_delay.vals for ss in nb_scan_size.vals for spmin in nb_sp_min.vals for spmax in nb_sp_max.vals if spmin <= sd <= spmax]
    nb_params = [ (nb,ss,spmin,sd,spmax) for nb in numa_bal.vals for ss in nb_scan_size.vals for spmin in nb_sp_min.vals for sd in nb_scan_delay.vals for spmax in nb_sp_max.vals if spmin <= sd <= spmax]
#setting up interleave parameters list
interleave_params = ((interleave.getVal(),),)

#setting up work dir
info("creating results directory '" + work_dir.getVal() + "' ...")
if not os.path.isdir(work_dir.getVal()):
    os.makedirs(work_dir.getVal())
#sp.Popen(["mkdir","-p",work_dir.getVal()]).wait()
#sp.Popen(["mkdir",work_dir.getVal() + "/" + "states"]).wait()
info("will start tests ...\n")

#setting sys keys
sys_states_keys = numabal_keys #tuple("numa_balancing" + ("_" if i != "" else "") + i for i in numabal_keys)
cmdline_states_keys = ("interleave",)
#setting sys states setters
sys_states = [sys_states_descr[k] for k in sys_states_keys]
cmdline_states = [i for _,i in cmdline_states_descr.iteritems()]
#setting sys values
sys_states_vals = nb_params
cmdline_states_vals = interleave_params

counter = 0

for ssv in sys_states_vals:
    for csv in cmdline_states_vals:
        info("ITERATION " + str(counter) + ":")

        info("setting system states...")
        for s,v in zip(sys_states,ssv):
            s.val = v 

        info("setting command line states...")
            #st.CmdState.clear()
        for s,v in zip(cmdline_states,csv):
            s.val = v

        info("state values:")
        for k,s in sys_states_descr.iteritems():
            print "\t" + k,":",s.val
        #info("command line states values:")
        for k,s in cmdline_states_descr.iteritems():
            print "\t" + k,":",s.val

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

            info("creating times file '" + tgt_dir + "/" + TIMES_FILE + "'...")
            f = open(tgt_dir + "/" + TIMES_FILE, "w")
            f.write("real_s" + "\n")
            f.close()

            for i in range(n_reps.getVal()):
                info("running app '" + tgt.name + "' (" + str(i+1) + " of " + str(n_reps.getVal()) + ") ...")
                tgt.run(cmdstate=True)

                #info("result of command '" + " ".join(tgt.cmd) + "':") 
                #tgt.dump()

                info("dumping result stdout to '" + tgt_dir + "/" + app.LAST_STDOUT_LOG + "' ...")
                info("dumping result stderr to '" + tgt_dir + "/" + app.LAST_STDERR_LOG + "' ...")
                of,ef = open(tgt_dir + "/" + app.LAST_STDOUT_LOG,"w"),open(tgt_dir + "/" + app.LAST_STDERR_LOG,"w")
                tgt.dump(out=of,err=ef)
                of.close()
                ef.close() 

                info("dumping result stdout to '" + tgt_dir + "/" + app.HIST_STDOUT_LOG + "' ...")
                info("dumping result stderr to '" + tgt_dir + "/" + app.HIST_STDERR_LOG + "' ...")
                of,ef = open(tgt_dir + "/" + app.HIST_STDOUT_LOG,"a"),open(tgt_dir + "/" + app.HIST_STDERR_LOG,"a")
                tgt.dump(out=of,err=ef)
                of.close()
                ef.close()

                info("extracting time information from stderr ...")
                ef = open(tgt_dir + "/" + app.LAST_STDERR_LOG, "r")
                timer.extract(source=ef)
                ef.close()

                info("dumping extracted time to '" + tgt_dir + "/" + TIMES_FILE + "' ...")
                tf = open(tgt_dir + "/" + TIMES_FILE, "a")
                timer.dump(out=tf)
                tf.close()

        counter += 1
        print ""
     
