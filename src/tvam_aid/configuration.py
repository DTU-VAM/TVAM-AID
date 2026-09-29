from dataclasses import dataclass, field
import numpy as np

@dataclass(frozen=True)
class Thresholds:
    """ Dose thresholds."""
    lower: float
    upper: float

@dataclass(frozen=True)
class RunConfig:
    """Configuration options for an optimisation run."""
    device: str = 'gpu'
    numIters: int = 1000
    angles: np.ndarray = field(
        default_factory=lambda: np.linspace(0, 360, 360*4, endpoint=False)
    )
