import math
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import numpy as np

def graph_creator(args):
    file = args[0]
    slicenum = args[1]
    # prop_name = args[2]
    print("Reading "+ file)
    openfile = open("./Velocity/ExtractedCompleteData/" + file,"r")
    timestep = file.split(".")[1]

    indices = []
    for i in range(0,248):
        for j in range(0,600):
            indices.append(600*248*i + 600*slicenum + j)
            indices.append(600*248*i + 600*(slicenum+1) + j)

    datapoint = []
    for i in tqdm(range(0, 600*248*248)):
        dp = openfile.readline()
        datapoint.append(dp)

    print(file + " Read Complete!")

    req_data = {}
    for i in tqdm(indices):
        dp = datapoint[i].split(" ")
        vec3 = {
            "X": float(dp[0]),
            "Y": float(dp[1]),
            "Z": float(dp[2]),
        }
        req_data[i] = vec3
    print("Point Extraction Complete!")

    X_pos = []
    Z_pos = []
    X = 600
    Z = 248
    data_1 = [[0 for i in range(0, 600)] for j in range(0,248)]
    data_2 = [[0 for i in range(0, 600)] for j in range(0,248)]

    # colorval = []

    limiter = 0
    for i in tqdm(range(248)):
        for j in range(600):
            # if(limiter%100 == 0):
            X_pos.append(i)
            Z_pos.append(j)
            
            data_1[i][j] = req_data[X*Z*i + X*slicenum + j]["X"];
            data_2[i][j] = req_data[X*Z*i + X*slicenum + j]["Z"];

            # colorval.append(data_prop[X*Y*j + X*slicenum + i])
            
            # limiter+=1

    for i in range(len(data_1)):
        for j in range(len(data_1[0])):
            data_1[i][j] = math.tanh(data_1[i][j])
            data_2[i][j] = math.tanh(data_2[i][j])
    
    Z_grid, X_grid = np.mgrid[0:Z, 0:X]
    
    fig, ax = plt.subplots(nrows=1, figsize=(10,8))
    ax.set_title("Streamline plot of the Velocity - XZ "+timestep+ " slice125", fontsize=15)
    f = ax.streamplot(X_grid, Z_grid, np.array(data_1), np.array(data_2), density=1)
    ax.set_xlabel('X position($10^{-3}$ parsecs)', fontsize=10)
    ax.set_ylabel('Z position($10^{-3}$ parsecs)', fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.tick_params(axis='both', which='minor', labelsize=10)
    fig.canvas.draw()  
    fig.savefig("./Images/Stream/XZ.stream.slice"+str(slicenum)+"."+ timestep+ ".png", dpi=300)
    # plt.show()
    plt.figure().clear()
    plt.cla()
    plt.clf()
    print(timestep + " complete!")

def YsliceExtractor(slicenum):   
    arguments = []
    for file in sorted(os.listdir("./Velocity/ExtractedCompleteData")):
        temp_list = []
        temp_list.append(file)
        temp_list.append(slicenum)
        # temp_list.append(prop_name)
        arguments.append(temp_list)

    for args in arguments:
        graph_creator(args)

YsliceExtractor(125)
