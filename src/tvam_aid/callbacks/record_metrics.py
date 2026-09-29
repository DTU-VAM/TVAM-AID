from dataclasses import dataclass
from cil.optimisation.utilities import callbacks
from tvam_aid.target import Target
from tvam_aid.configuration import Thresholds
from tvam_aid.operators import TVAMOperator, AdjointOperator
from tvam_aid import calcIPDR, calcPW, calcVER
import numpy as np

@dataclass(frozen=True)
class RecordMetrics:
    """Specify which optimisation metrics should be recorded."""

    names: tuple[str, ...] = (
        "IPDR",
        "PW",
        "VER",
        "MCC",
        "SM",
    )

    def build(
            self,
            target: Target,
            thresholds: Thresholds,
            tvamOperator: TVAMOperator):
        """Create the CIL callback used to record the selected metrics."""
        return _MetricsCallback(
            target = target,
            thresholds = thresholds,
            AT = tvamOperator.AT,
            names = self.names,
        )


class _MetricsCallback(callbacks.Callback):
    """CIL callback for recording TVAM optimisation metrics."""

    def __init__(
            self,
            target: Target,
            thresholds: Thresholds,
            AT: AdjointOperator,
            names: tuple):
        self.target = target
        self.thresholds = thresholds
        self.AT = AT
        self.names = names

        self.IPDR = []
        self.PW = []
        self.VER = []

    def __call__(self, algorithm):
        """Calculate and store the selected metrics for the current solution."""
        currentSinogram = algorithm.solution
        currentRecon = self.AT.direct(currentSinogram)

        if "IPDR" in self.names:
            self.IPDR.append(calcIPDR(currentRecon.array, self.target))

        if "PW" in self.names:
            self.PW.append(calcPW(currentRecon.array, self.target))

        if "VER" in self.names:
            self.VER.append(calcVER(currentRecon.array, self.target))
