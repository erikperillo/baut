import core.state as state
import core.command_line as cl
import csv

def loadSystemStates(file_path, header=True):
   with open(file_path, "r") as sys_states_file:
        states_table = csv.reader(sys_states_file) 

        system_states = {}
        for col in [c for c in states_table][1 if header else 0:]:
            name, getter, setter, type_name = col
            system_states[name] = state.SystemState(getter, setter, type_name)

        return system_states

def hue():
    import shlex
    with open("oi.csv") as oi:
        reader = csv.reader(oi)
        for col in reader:
            print "in col",col
            for c in col:
                print shlex.split(c)
            print
def main():
    import oarg

    sys_states_path = oarg.Oarg(str, "-s --sys-states-path", "", "system states path")
    hlp = oarg.Oarg(bool, "-h --help", False, "this help message")

    oarg.parse()

    if hlp.found:
        oarg.describeArgs("options:")
        exit()

    if not sys_states_path.found:
        print "error"
        exit(1)

    system_states = loadSystemStates(sys_states_path.val)
    autonuma = system_states["autonuma"]

    print autonuma.getter
    print autonuma.setter
    autonuma.val = 34

if __name__ == "__main__":
    hue()
    exit()
    main()
