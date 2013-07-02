#!/usr/bin/python

import os
import sys
import code
import logging
import yaml

from chube import *
load_chube_config()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If you run `chube test Plan`, for example, we will import `plan.PlanTest`
        # and execute its `run()` method.
        class_under_test = sys.argv[-1]
        mod = {"Plan": "plan",
               "Datacenter": "datacenter",
               "Kernel": "kernel",
               "Distribution": "distribution",
               "Linode": "linode_obj",
               "Domain": "dns",
               "Stackscript": "stackscript"}[class_under_test]
        test_suite = getattr(__import__("chube." + mod,
                                        fromlist=[True]),
                             class_under_test + "Test")
        test_suite.run()
        sys.exit(0)

    # If we're not running tests, then just start the interpreter.
    code.interact(local=locals())
