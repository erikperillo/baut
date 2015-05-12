import tools.oarg as oarg
import core.app as app
import subprocess as sp

TOOLS_DIR_NAME = "tools"
DEF_TESTS_DIR_NAME = "tests" + "/" + "".join(sp.Popen([TOOLS_DIR_NAME + "/date/" + "get_date_footprint.sh"],stdout=sp.PIPE).communicate()[0].splitlines())
BENCHMARK_APPS_DIR_NAME = "apps"

def info(msg,quiet=False):
    if not quiet:
        print "[baut] " + msg

def error(msg,errn=1):
    info("error: " + msg)
    exit(errn)

def numaBalStateString(script="tools/numa/numa_bal_state_string.sh"):
    return sp.Popen([script],stdout=sp.PIPE).communicate()[0]

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

#parsing and checking for wrong options
if oarg.parse() != 0:
     error("Invalid options passed: " + "".join(["'" + word + "'," for word in oarg.Oarg.invalid_options]))

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

#setting up work dir
info("creating results directory '" + work_dir.getVal() + "' ...")
sp.Popen(["mkdir","-p",work_dir.getVal()]).wait()
info("will start tests ...\n")

#dictionary for numa balancing parameters
nb_options = dict([(key,val) for key,val in zip(["--md","--sc","--ss","--spmin","--sd","--spmax"],[nb_migrate_def,nb_settle_count,nb_scan_size,nb_sp_min,nb_scan_delay,nb_sp_max])])
args = sum( [[key,val.getVal()] for key,val in nb_options.iteritems()], [] )

#setting up numa balancing parameters list
if sliding.getVal():
    #checking if sliding args are correct
    if len(set([len(arg.vals) for _,arg in nb_options.iteritems()])) != 1:
        error("Invalid arguments passed")
    nb_params = zip(*[arg.vals for _,arg in nb_options.iteritems()])
else:
    nb_params = [ (md,sc,ss,spmin,sd,spmax) for md in nb_migrate_def.vals for sc in nb_settle_count.vals for sd in nb_scan_delay.vals for ss in nb_scan_size.vals for spmin in nb_sp_min.vals for spmax in nb_sp_max.vals if spmin <= sd <= spmax]

#main loop
for il,nb,md,sc,ss,spmin,sd,spmax in [ (il,nb,md,sc,ss,spmin,sd,spmax) for il in interleave.vals for nb in numa_bal.vals for md,sc,ss,spmin,sd,spmax in nb_params ]:
    info("setting autonuma params...",quiet=True)
    #sp.Popen(["sudo","setters/numa_balancing_config.py"] + sum([[i,str(j)] for i,j in zip(["-a","-s","-d","-m","-M"],[nb,ss,sd,spmin,spmax])],[])).wait()
    info("running with il = " + str(il) + ", nb = " + str(nb) + ", (md,sc,ss,spmin,sd,spmax) = " + str((md,sc,ss,spmin,sd,spmax)) + " ...",quiet.getVal())

    for target in targets:
        if target.run_dir == "":
            info("creating application test structure ...")
            target.createRunDir(base_dir=work_dir.getVal())
            info("created '" + target.run_dir + "'")
        #creating dir
        tgt_curr_dir = target.run_dir + "/" + app.APP_CONFIGS_DIRNAME + "/" + "il" + str(il) + "_" + numaBalStateString()
        sp.Popen(["mkdir","-p",tgt_curr_dir])

        info("running application '" + target.name + "' ...")
        target.run()

        info("'" + target.key + "' output:")
        target.dump()
 
        #creating files
        last_run_file = open(tgt_curr_dir + "/last_run.txt","w")
        hist_run_file = open(tgt_curr_dir + "/hist_run.txt","a")

        for fl in last_run_file,hist_run_file:
            target.dump(out=fl,err=None)
            fl.close()
    print ""
