import subprocess
import sys
from IPython.core.getipython import get_ipython


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# Example usage:

log = get_ipython().getoutput("ls -la")
log
