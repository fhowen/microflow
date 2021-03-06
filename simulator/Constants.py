import sys

# this section do not need to change
# =====================================
MAXTIME = sys.maxsize
MACHINENUM = 150
JOBNUM = 256
ZERO = 0.001/(1048576*8)
# ======================================


RACK_BITS_PER_SEC = 1.0 * 1024 * 1048576 # 1Gbps
RACK_COMP_PER_SEC = 300.0


# dag tye strings
DNNDAG = "DNN"
WEBDAG = "WEB"
RANDOMDAG = "RANDOM"
MIXEDDAG = "MIXED"

# task status used for isActive
UNSUBMITTED = 0
SUBMITTED = 1
STARTED = 2
FINISHED = 3

# log file path
LOGDIR = "logfile"