import benchmark as bm
import app

cg = app.App("cg","cg.C")
mg = app.App("mg","mg,C")

NPB = bm.Benchmark([cg,mg],["nas-par-bm run "," -n 64"])

NPB.run("cg")
