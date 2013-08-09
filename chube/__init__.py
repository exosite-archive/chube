import os
import sys
import yaml

from .api import api_handler as chube_api_handler
from .plan import Plan
from .datacenter import Datacenter
from .kernel import Kernel
from .distribution import Distribution
from .stackscript import Stackscript, StackscriptInput
from .linode_obj import Linode, Disk, Config, IPAddress
from .nodebalancer import Nodebalancer, NodebalancerConfig
from .dns import Domain
CHUBE_VERSION = "0.1.18"

def load_chube_config():
    """Loads the Chube config from ~/.chube."""
    config_path = os.path.join(os.environ["HOME"], ".chube")
    if os.path.exists(config_path):
        contents = yaml.load(open(config_path, "r"))
        if not hasattr(contents, "__getitem__"):
            raise ValueError("Config file at '%s' must be a valid YAML document; see README.md" % (config_path,))
        chube_api_handler.api_key = contents["api_key"]
        return
    raise OSError("No config file found at '%s'" % (config_path))
