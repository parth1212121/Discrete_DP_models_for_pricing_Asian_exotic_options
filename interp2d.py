import numpy as np

def bilinear(V, Sg, Ag, S, A):
    NS, NA = V.shape
    i1 = np.searchsorted(Sg, S, side='left')
    if i1 <= 0: i0, i1, alpha = 0, 0, 0.0
    elif i1 >= NS: i0, i1, alpha = NS-1, NS-1, 0.0
    else:
        i0 = i1 - 1
        d = (Sg[i1] - Sg[i0]); alpha = 0.0 if d==0 else (S - Sg[i0]) / d
    j1 = np.searchsorted(Ag, A, side='left')
    if j1 <= 0: j0, j1, beta = 0, 0, 0.0
    elif j1 >= NA: j0, j1, beta = NA-1, NA-1, 0.0
    else:
        j0 = j1 - 1
        d = (Ag[j1] - Ag[j0]); beta = 0.0 if d==0 else (A - Ag[j0]) / d
    v00 = V[i0, j0]; v10 = V[i1, j0]
    v01 = V[i0, j1]; v11 = V[i1, j1]
    return (1-alpha)*(1-beta)*v00 + alpha*(1-beta)*v10 + (1-alpha)*beta*v01 + alpha*beta*v11
