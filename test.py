import core.app as app
import tools.oarg as oarg
import core.state as st
import subprocess as sp

def info(msg):
    print "[baut::test] " + msg

app_path = "testapp"
ext_path = "testext"

info("adding timer cmdstate to line")
timer_cmdstate = st.CmdState(["/usr/bin/time","-f","timer_real: %e"],1,True)

info("loading app from '" + app_path + "' ...")
dur = app.App(app_path)
info("loaded app '" + dur.name + "'")
info("running app '" + dur.name + "' ...")
dur.run(cmdstate=True)
info("dumping output to stdout ...")
tmp=open("b0ss","w")
dur.dump(err=tmp)
tmp.close()
info("done")

info("loading extractor from '" + ext_path + "'...")
ext = app.Extractor(ext_path,name="le timer")
info("loaded extractor '" + ext.name + "'")
info("running extractor file'" + " ".join(ext.cmd) + "' ...")
ext.extract(source=open("b0ss","r"))
info("dumping ...")
ext.dump()
