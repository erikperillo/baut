import state

a = state.CmdState("lel",True,3)
b = state.CmdState("l0l",False)
c = state.CmdState("hehe")
d = state.CmdState("HUE",False,-1)
e = state.CmdState("rs",False,1)

d.val,e.val = True,False

print state.CmdState.get()

state.CmdState.clear()
f = state.CmdState("rs",True,3)
