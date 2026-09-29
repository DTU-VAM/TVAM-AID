from tvam_aid.target import Target
from tvam_aid.configuration import Thresholds

def _getThresholdTarget(target: Target, thresholds: Thresholds):
    thresholdTarget = target.image.geometry.allocate()

    thresholdTarget.array[target.regions.inPart] = thresholds.upper
    thresholdTarget.array[target.regions.outPart] = thresholds.lower
    thresholdTarget.array[target.regions.external] = 0.0

    return thresholdTarget