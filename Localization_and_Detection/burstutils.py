
import numpy as np
import matplotlib.pyplot as plt
import math as mth
import random as rand
import statistics as s
import healpy as hp


def length(v):
    """
    Finds the length of a vector
    
    Parameters
    ----------
    
    v : array
        numpy array representative of the vector you want to find the magnitude of. 
    
    Returns
    -------
    
    magv : float
        magnitude of v.
    """
    magv = mth.sqrt(np.dot(v, v))
    return magv

def angle(v1, v2):
    """"
    Finds the angle between 2 vectors
    
    Parameters
    ----------
    
    v1 : array
    v2 : array
        The arrays representing the vectors who's angle is to be calculated.
        
    Returns
    -------
    
    ang : float
        Angle between the 2 vectors. 
        
    """

    ang = np.arccos(np.dot(v1, v2) / (length(v1) * length(v2)))
    return ang

def findAngles(v1s, v2s):
    dot = np.einsum('ijk,ijk->ij',[v1s,v1s,v2s],[v2s,v1s,v2s])
    return np.arccos(dot[0,:]/(np.sqrt(dot[1,:])*np.sqrt(dot[2,:])))


def chiresponse(A):
    """
    The response function used in the chi squared fitting portion of the simulation. 
    Meant to imitate the actual response of a scintillator.
    Inputs 2 vectors, and responds with a cos^x dependence.
    
    Parameters
    ----------
    A : float
        The angle between the two vectors who's response is meant to be imitated. 

    Returns
    -------

    A : float
        The cosine dependence based on the angle, includes a mask so that terms corresponding to angular separations beyond pi/2 are 0, imitating what would happen if a GRB didn't strike the face of a detector. Further simulations of this effect are neccessary in a different software package to confirm this assumption, but its okay for now. 

    """
    #meant to imitate the response of the detectors for effective area vs. angle, found to be around .77
 #   print(length(A),length(B))
#if cosine is negative, 

    mask = A > np.pi/2.

    A[mask] = 0
    A[~mask] = pow(abs(np.cos(A[~mask])),0.76)
    
    
    return A

def response(A):
    """
    Meant to imitate the actual response of a scintillator.
    Inputs 2 vectors, and responds with a cos^x dependence.
    
    Parameters
    -----------
    A : float
        The angular separation in radians between the normal vector of the detector, and the position in the sky of the simulated GRB. 

    Returns
    -------
    R : float
        The response function of how the scintillator will respond to a source at angle A. 

    """
    #meant to imitate the response of the detectors for effective area vs. angle, found to be around .77
 #   print(length(A),length(B))
#if cosine is negative, 

    R = pow(abs(np.cos(A)),0.76)
    
    
    return R         


def quad_solver(detval,detnorm,bottheta,toptheta,botphi,topphi,botA,topA,ntheta,nphi,nA,background):
    """Generates an array of all possible chi terms for a given detector and the number of counts induced in it by some source. Named quad since BurstCube is composed of 4 detectors, and this generates 1/4 of the terms. 
    
    Parameters
    ----------
    detsvals : array
        Numpy array containing the relative counts in a BurstCube detector.
    detnorms : array
        Numpy array containing the normal vector of a BurstCube detector. 
    bottheta : float
        Minimum polar angle to be tested. 
    toptheta : float
        Maximum polar angle to be tested. 
    botphi : float
        Minimum azimuthal angle to be tested. 
    topphi : float
        Maximum azimuthal angle to be tested. 
    botA : float
        Minimum signal strength to be tested. 
    topA : float
        Maximum signal strength to be tested.  
    ntheta : int
        Number of sample points between bottheta and toptheta.
    nphi : int
        Number of sample points between botphi and topphi.
    bgrd : float
        # of background counts inherent to each detector. 
    nA : int
        Number of sample points between botA and topA. 

    Returns
    ------- 
    chiterm : array
        Numpy array containing all the chisquared terms for one BurstCube detector. 
    """
    #Need a fix for fine opt,  can't handle subtractions from 0..
    theta = np.deg2rad(np.linspace(bottheta,toptheta,ntheta))
    phi = np.deg2rad(np.linspace(botphi,topphi,nphi))
    #theta = [0 if o<0 else o for o in theta]
    #theta = [np.pi if o>np.pi else o for o in theta]
   # phi = [0 if p<0 else p for p in phi]
   # phi = [2*np.pi if p>2*np.pi else p for p in phi]
    mphi,mtheta = np.meshgrid(phi,theta)
    allthetas = np.concatenate(mtheta)
    allphis = np.concatenate(mphi)
    allvecs = hp.ang2vec(allthetas,allphis)
    As= np.linspace(botA,topA,nA)
  #alternate approach to the one below, doesn't really make a difference?   
  #  normarrs = np.zeros(int(len(theta)*len(phi)))
   # normarrs = [[detnorm[0],detnorm[1],detnorm[2]] if o==0 else o for o in normarrs]
    normarr = detnorm
    
    normarrs = []
    for garc in range((len(theta)*len(phi))):
        normarrs.append([normarr[0],normarr[1],normarr[2]])
        
    seps = findAngles(allvecs,normarrs)
    AA,SS = np.meshgrid(As,seps)
    Aofit = np.concatenate(AA)
    chiseps = np.concatenate(SS)
    
    #this is close, but needs to be a way to go one step further and do this in the next chiR
    bg = background * np.ones(len(chiseps))
    #good = chiseps < np.pi/2
    #bad = chiseps > np.pi/2
    
    #probs that, don't want to include bg 
    chiResponse = np.multiply(Aofit,chiresponse(chiseps)) + bg
    #chiResponse = [1e5 if i <= background else i for i in chiResponse]
    if detval > background: 
        chiterm = np.divide(np.power(np.subtract(chiResponse,detval),2),detval)
    else: 
        chiterm = 1e5 * np.ones(len(theta)*len(phi)*len(As))
    
    return chiterm


def indexer(chisquareds,bottheta,toptheta,botphi,topphi,botA,topA,ntheta,nphi,nA):
    """ After obtaining an array of all the possible chi squared values, this uses an equation I tediously discovered which can backtrack to what term in each array corresponds to the minimim chi squared. 
    

    Parameters
    ----------
    chisquareds : array
        numpy array of all possible chi squared values 

    bottheta : float
        Minimum polar angle to be tested. 
    toptheta : float
        Maximum polar angle to be tested. 
    botphi : float
        Minimum azimuthal angle to be tested. 
    topphi : float
        Maximum azimuthal angle to be tested.
    botA : float
        Minimum signal strength to be tested. 
    topA : float
        Maximum signal strength to be tested.  
    ntheta : int
        Number of sample points between bottheta and toptheta.
    nphi : int
        Number of sample points between botphi and topphi.
    nA : int
        Number of sample points between botA and topA. 


    Returns
    -------
    thetaloc : float
        The reconstructed polar angle of the source.
    philoc : float
        The reconstructeed azimuthal angle of the source. 
    Aoguess : float 
        The reconstructed strength of the source. 
    """
    chimin = min(chisquareds)
    chisquareds = list(chisquareds)
    oa = np.deg2rad(np.linspace(bottheta,toptheta,ntheta))
    ob = np.deg2rad(np.linspace(botphi,topphi,nphi))
    Aofit = (np.linspace(botA,topA,nA))
    thetaloc = np.rad2deg(oa[int((chisquareds.index(chimin)-(chisquareds.index(chimin) % (len(ob)*len(Aofit))))/(len(ob)*len(Aofit)))])
    philoc = np.rad2deg(ob[int(((chisquareds.index(chimin) % (len(ob)*len(Aofit)))-(chisquareds.index(chimin) % (len(Aofit))))/len(Aofit))])
    Aoguess=Aofit[int((chisquareds.index(chimin) % (len(ob)*len(Aofit)))  % len(Aofit))]
    
    return thetaloc, philoc, Aoguess



