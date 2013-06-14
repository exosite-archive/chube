#!/usr/bin/python

import os
import sys
import code
import logging
import yaml

from chube import *


class ScriptConfig:
    """Describes the configuration parsed from files by ConfigBuilder."""
    def __init__(self, search_path):
        """Initializes the ScriptConfig instance.

           `search_path`: The list of files that ConfigBuilder attempted to parse."""
        self._params = {}
        self._search_path = search_path

    def __getitem__(self, param_name):
        """Returns the value for the given configuration parameter.

           Returns None if the parameter is not defined."""
        if self._params.has_key(param_name):
            return self._params[param_name]
        return None

    def set_param(self, k, v):
        """Sets the given configuration parameter."""
        self._params[k] = v


class ConfigBuilder:
    """Builds a ScriptConfig instance from config files found the search path.

       The attribute `path` is an array of the files that will be parsed, in order,
       to generate the config. You may modify it before calling build()."""
    def __init__(self):
        self.path = []
        self.path.append(os.path.join("etc", "chube.conf"))
        self.path.append(os.path.join(os.environ["HOME"], ".chube"))

    def build(self):
        """Builds a ScriptConfig from the files it finds in `self.path`.

           Options found later will replace options found earlier."""
        conf = ScriptConfig(self.path)
        for f in self.path:
            if not os.access(f, os.R_OK): continue
            logging.info("Reading configuration parameters from '%s'" % (f))
            contents = yaml.load(open(f))
            if not hasattr(contents, "__getitem__"):
                raise ValueError("Config file at '%s' must be a valid YAML document; see README.md" % (f,))
            for k, v in contents.items():
                conf.set_param(k, v)
        return conf


if __name__ == "__main__":
    conf_builder = ConfigBuilder()
    conf = conf_builder.build()
    chube_api_handler.api_key = conf["api_key"]

    if len(sys.argv) > 1:
        # If you run `chube test Plan`, for example, we will import `plan.PlanTest`
        # and execute its `run()` method.
        class_under_test = sys.argv[-1]
        mod = {"Plan": "plan",
               "Datacenter": "datacenter",
               "Kernel": "kernel",
               "Distribution": "distribution",
               "Linode": "linode_obj",
               "Stackscript": "stackscript"}[class_under_test]
        test_suite = getattr(__import__("chube." + mod,
                                        fromlist=[True]),
                             class_under_test + "Test")
        test_suite.run()
        sys.exit(0)

    # If we're not running tests, then just start the interpreter.
    code.interact(local=locals())
