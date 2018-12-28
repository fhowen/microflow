import sys

MAXTIME = sys.maxsize
MACHINENUM = 150
JOBNUM = 3
ZERO = 0.001
RACK_BITS_PER_SEC = 1.0 * 1024 * 1048576 # 1Gbps
RACK_COMP_PER_SEC = 100.0


# dag tye strings
DNNDAG = "DNN"
WEBDAG = "WEB"
RANDOMDAG = "RANDOM"

# task status used for isActive
UNSUBMITTED = 0
SUBMITTED = 1
STARTED = 2
FINISHED = 3