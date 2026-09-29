from importlib.metadata import version

CIL_VERSION = '24.2.0'
installedCILVersion = version('cil')
if installedCILVersion != CIL_VERSION:
    try:
        installedCILVersion = version('cil')
    except PackageNotFoundError:
        raise ImportError(
            'TVAM AID requires CIL 24.2.0, but CIL is not installed.'
        ) from None
    raise ImportError(
        f'TVAM AID requires CIL {CIL_VERSION}, '
        f'but CIL {installedCILVersion} is installed. '
        'Install the required version with:\n'
        'conda install -c conda-forge -c ccpi cil=24.2.0'
    )


from .configuration import RunConfig, Thresholds
from .target import loadTargetGeometry
from .plotting import showTarget, plotAchievedDose2D, plotHistogram, plotMetricSensitivity, plotPWSweep, plotIPDRSweep, plotVERSweep, plotSliceMetrics, showAchievedDose3D
from .optimisation import nonNegativityConstraint, runOptimisation
from .metrics import calcIPDR, calcPW, calcVER, printMetrics, calcTrimmedMetrics, calcTrimmedIPDR, calcTrimmedPW

__all__ = [
    'RunConfig', 'Thresholds',
    'loadTargetGeometry',
    'showTarget', 'plotAchievedDose2D', 'plotHistogram', 'plotMetricSensitivity', 'plotPWSweep', 'plotIPDRSweep', 'plotVERSweep', 'plotSliceMetrics', 'showAchievedDose3D',
    'nonNegativityConstraint', 'runOptimisation',
    'calcIPDR', 'calcPW', 'calcVER', 'printMetrics', 'calcTrimmedMetrics', 'calcTrimmedIPDR', 'calcTrimmedPW'
]