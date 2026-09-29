# from tvam_aid.callbacks import RecordMetrics
from tvam_aid.target import Target
import numpy as np

def calcIPDR(x: np.ndarray, target: Target):
    """Calculate the in-part dose range."""
    inPart = x[target.regions.inPart]
    return np.amax(inPart) - np.amin(inPart)

def calcPW(x: np.ndarray, target: Target):
    """Calculate the process window."""
    inPart = x[target.regions.inPart]
    outPart = x[target.regions.outPart]
    return np.amin(inPart) - np.amax(outPart)

def calcVER(x: np.ndarray, target: Target):
    """Calculate the voxel error rate."""
    inPart = x[target.regions.inPart]
    outPart = x[target.regions.outPart]
    nVoxels = np.count_nonzero(target.regions.inPart | target.regions.outPart)
    return np.sum(outPart>=np.amin(inPart)) / nVoxels

def printMetrics(metrics):
    """Print the metrics of the final iteration recorded by the metrics callback."""
    print('\n=== METRICS ===')
    if 'IPDR' in metrics.names:
        print('{:6}¦ {:.5f}'.format('IPDR', metrics.IPDR[-1]))
    if 'PW' in metrics.names:
        print('{:6}¦ {:.5f}'.format('PW', metrics.PW[-1]))
    if 'VER' in metrics.names:
        print('{:6}¦ {:.5f}'.format('VER', metrics.VER[-1]))

def calcTrimmedMetrics(
        achievedDose: np.ndarray,
        target: Target,
        alphas: np.ndarray):
    """Calculate PW and IPDR for a range of trimming percentages."""
    trimmedIPDR = np.array([
        calcTrimmedIPDR(achievedDose, target, percentage)
        for percentage in alphas
    ])

    trimmedPW = np.array([
        calcTrimmedPW(achievedDose, target, percentage)
        for percentage in alphas
    ])
    return trimmedIPDR, trimmedPW

def calcTrimmedIPDR(
        achievedDose: np.ndarray,
        target: Target,
        alpha: float):
    """Calculate IPDR after removing an equal percentage from both tails."""
    if not 0 <= alpha < 100:
        raise ValueError("percentRemoved must be in the range [0, 50).")

    inPart = achievedDose[target.regions.inPart]

    lower = np.percentile(inPart, alpha/2)
    upper = np.percentile(inPart, 100 - alpha/2)
    return upper - lower


def calcTrimmedPW(
        achievedDose: np.ndarray,
        target: Target,
        alpha: float):
    """Calculate PW after removing an equal percentage from both tails."""
    if not 0 <= alpha < 100:
        raise ValueError("alpha must be in the range [0, 50).")

    inPart = achievedDose[target.regions.inPart]
    outPart = achievedDose[target.regions.outPart]

    inPartLower = np.percentile(inPart, alpha/2)
    outPartUpper = np.percentile(outPart, 100 - alpha/2)
    return inPartLower - outPartUpper
