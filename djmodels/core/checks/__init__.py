# Import these to force registration of checks
from .registry import Tags, register, run_checks, tag_exists
import djmodels.core.checks.database  # NOQA isort:skip
import djmodels.core.checks.model_checks  # NOQA isort:skip

