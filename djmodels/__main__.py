"""
Invokes djmodels-admin when the djmodels module is run as a script.

Example: python -m djmodels check
"""
from djmodels.core import management

if __name__ == "__main__":
    management.execute_from_command_line()
