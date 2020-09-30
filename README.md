# Risk Parity Weighting

This repository builds a docker container to backcalculate risk parity weights for an arbitrary set of assets. The total of the weights produced will sum to 1. It is possible to run the script itself outside of a container, or you can run the container directly from the public repository. For example: `docker run dnase/riskparity:latest python /app/weights.py SPY,TLT`