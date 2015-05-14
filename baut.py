import tools.oarg as oarg
import core.app as app
import core.state as st
import subprocess as sp

TOOLS_DIR_NAME = "tools"
DEF_TESTS_DIR_NAME = "tests" + "/" + "".join(sp.Popen([TOOLS_DIR_NAME + "/date/" + "get_date_footprint.sh"],stdout=sp.PIPE).communicate()[0].splitlines())
STATES_DIR_NAME = "states"
APPS_DIR_NAME = STATES_DIR_NAME + "/" + "apps"
BENCHMARK_APPS_DIR_NAME = "apps"
NUMABAL_COMMOM_PATH = "/proc/sys/kernel/numa_balancing"
NUMABAL_CONFIG_FILE = "tools/numa/numa_bal_config.py"

def info(msg,quiet=False):
    if not quiet:
        print "[baut] " + msg

def error(msg,errn=1):
    info("error: " + msg)
    exit(errn)

#application specific
numabal_keys = ("","migrate_deferred","settle_count","scan_size_mb","scan_period_min_ms","scan_delay_ms","scan_period_max_ms")
numabal_config_flags = ("-a","--md","--sc","--ss","--spmin","--sd","--spmax")

#states
sys_states_descr = dict([ ("numa_balancing" + ("_" if key != "" else "") + key,st.SysState(getter=["head","-c","1",NUMABAL_COMMOM_PATH + ("_" + key) if key != "" else ""],\
                          setter=[NUMABAL_CONFIG_FILE,flag])) for key,flag in zip(numabal_keys,numabal_config_flags) ])
runtime_states_descr = {"interleave": st.RuntimeState("--interleave=all")}

#arguments
apps            = oarg.Oarg(str,"-a --apps","","Apps directories list")
benchmark       = oarg.Oarg(str,"-b --benchmark","","Benchmark directory")
sliding         = oarg.Oarg(bool,"-s --sliding",False,"Sliding arguments mode")
interleave      = oarg.Oarg(str,"-i --interleave",False,"Activates Interleaving policy")
work_dir        = oarg.Oarg(str,"-w --work-dir",DEF_TESTS_DIR_NAME,"Directory to save results")
quiet           = oarg.Oarg(bool,"-q --quiet",False,"Does not run so verbose")
numa_bal        = oarg.Oarg(bool,"-n --numa-balancing",False,"Activates automatic NUMA balancing")
nb_migrate_def	= oarg.Oarg(int,"--md --migrate-deferred",16,"Automatic NUMA balancing migrate deferred")
nb_settle_count	= oarg.Oarg(int,"--sc --settle-count",4,"Automatic NUMA balancing settle count")
nb_scan_size    = oarg.Oarg(int,"--ss --scan-size",256,"Automatic NUMA balancing scan size")
nb_sp_min       = oarg.Oarg(int,"--spmin --scan-period-min",1000,"Automatic NUMA balancing scan period min")
nb_scan_delay   = oarg.Oarg(int,"--sd --scan-delay",1000,"Automatic NUMA balancing scan delay")
nb_sp_max       = oarg.Oarg(int,"--spmax --scan-period-max",60000,"Automatic NUMA balancing scan period max")
hlp             = oarg.Oarg(bool,"-h --help",False,"This help message")

#dictionary for numa balancing parameters
nb_options = [nb_migrate_def,nb_settle_count,nb_scan_size,nb_sp_min,nb_scan_delay,nb_sp_max]
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
    nb_params = zip(len(nb_migrate_def.vals)*(numa_bal.getVal(),),*[arg.vals for arg in nb_options])
else:
    nb_params = [ (nb,md,sc,ss,spmin,sd,spmax) for nb in numa_bal.vals for md in nb_migrate_def.vals for sc in nb_settle_count.vals for sd in nb_scan_delay.vals for ss in nb_scan_size.vals for spmin in nb_sp_min.vals for spmax in nb_sp_max.vals if spmin <= sd <= spmax]
#setting up interleave parameters list
interleave_params = ((interleave.getVal(),),)

#setting up work dir
info("creating results directory '" + work_dir.getVal() + "' ...")
sp.Popen(["mkdir","-p",work_dir.getVal()]).wait()
sp.Popen(["mkdir",work_dir.getVal() + "/" + "states"]).wait()
info("will start tests ...\n")

#setting sys keys
sys_states_keys = tuple("numb_balancing_" + i for i in numabal_keys)
runtime_states_keys = ("interleave",)
#setting sys values
sys_states_vals = nb_params
runtime_states_vals = interleave_params

counter = 0
for ssv in sys_states_vals:
    for rsv in runtime_states_vals:
        #creating dictionaries
        #ss_dict = dict( (k,v) for k,v in zip(sys_states_keys,ss) )
        #rs_dict = dict( (k,v) for k,v in zip(runtime_states_keys,rs) )
        #setting
        for (_,state),value in zip(sys_states_descr.iteritems(),ssv):
            state.val = value

        #creating dir
        state_dir = work_dir.getVal() + "/" + STATES_DIR_NAME + "/" + str(counter)
        info("creating state dir '" + state_dir + "' ...")
        sp.Popen(["mkdir",state_dir]).wait()
        
        #saving state
        info("saving state file '" + state_dir + "/" + "state.csv" + "' ...")
        sf = open(state_dir + "/" + "state.csv","a")
        sf.write("state_name,state_value\n")
        for key,val in zip(sys_states_descr,ssv):
            sf.write(key + "," + str(val) + "\n")
        for key,val in zip(runtime_states_descr,rsv):
            sf.write(key + "," + str(val) + "\n")
        sf.close()

        #creating key for process

        counter += 1

