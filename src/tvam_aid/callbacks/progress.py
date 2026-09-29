from dataclasses import dataclass
from cil.optimisation.utilities import callbacks

@dataclass(frozen=True)
class Progress:
    """Display optimisation progress."""

    def build(self):
        """Create the CIL progress callback."""
        return callbacks.ProgressCallback()