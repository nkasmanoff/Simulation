from BurstCube.NoahSim import burstutils

import numpy as np


def test_length():
	x = [0,1,0]

	testmag = burstutils.length(x)

	assert (np.abs(testmag - 1) < 1e-7)


def test_angle():
	#used to find one separation
	x = [1,0,0]
	y = [0,1,0]
	testang = burstutils.angle(x,y)

	assert (np.abs(testang - np.pi/2) < 1e-7)

def test_findAngles():
	#used to find an array of separations
	xs = [[1,0,0],[1,0,0]]
	ys = [[0,1,0],[0,1,0]]

	testangs = burstutils.findAngles(xs,ys)

	np.testing.assert_allclose(testangs, (np.pi/2, np.pi/2), 1e-3)


def test_chiresponse():
	testAs = burstutils.chiresponse(np.array([np.pi/4,7*np.pi/4]))
	
	np.testing.assert_allclose(testAs,(0.768438,0),1e-3)

def test_response():
	testR = burstutils.response(np.pi/4)

	assert (np.abs(testR- 0.768438) < 1e-3)


def test_quadsolver():

	fakenorm = [0,0,1]
	fakeval = 1600

	fakechi = burstutils.quad_solver(fakeval,fakenorm,0,5,0,360,0,500,1,1,2,1000)

	np.testing.assert_allclose(fakechi, (225, 6.25), 1e-3)

def test_indexer():
	fakechisquareds = [10,100,4,60,66,1002,99,93]
	fakeindex = burstutils.indexer(fakechisquareds,1,8,27,99,23,45,2,2,2)

	np.testing.assert_allclose(fakeindex, (1.0, 99.0, 23.0), 1e-3)
