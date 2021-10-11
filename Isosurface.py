# Time step 60 Slice 125

from tqdm import tqdm
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
import numpy as np
import plotly.graph_objects as go

properties = {
        "density" : {"cmap": 'Blues_r', "pos": 0, "vmin": 20, "vmax": 18020},
        "temp" : {"cmap": 'hot', "pos": 1, "vmin": 72.16, "vmax": 30350},
        "ab_H2" : {"cmap": 'bone', "pos": 8, "vmin": 1.76e-14, "vmax": 6.911e-05},
        "ab_H-": {"cmap": 'pink', "pos": 7, "vmin": 1e-99, "vmax":1.629e-07},
        "ab_H2+": {"cmap": 'copper', "pos": 9, "vmin": 1e-99, "vmax": 1.691e-08}
    }


def graph_creator(args):
    filereader = open("./Multifield/ExtractedCompleteData/" + args[0], "r")
    timestep = args[0].split(".")[1]
    prop_name = args[1]
    selected_property = []

    vmin = 100000007
    vmax = -11111111
    for lines in tqdm(range(0, 600*248*248)):
        d = filereader.readline()
        props = d.split(" ")
        selected_property.append(float(props[properties[prop_name]["pos"]]))
        if(float(props[properties[prop_name]["pos"]]) < vmin): vmin = float(props[properties[prop_name]["pos"]])
        if(float(props[properties[prop_name]["pos"]]) > vmax): vmax = float(props[properties[prop_name]["pos"]])

    print(vmin, vmax)

    slice = [i for i in range(80, 180)]

    # Trying Volume Rendering - Y slices with X,Z axes
    X, Z, Y = np.mgrid[300:600, 0:248, slice[0]:slice[-1]]

    values = np.copy(Y)
    # So now the shape of each of these is 600*248*60
    # In Y we need to put the property values instead. 
    # So for a given X,Z ->
    for x in tqdm(range(0, 300)):
        for z in range(0,248): 
            for y in range(len(Y[x][z])):
                values[x][z][y] = selected_property[600*248*z + 600*Y[x][z][y] + x+300] # Set the range from 300,600 to get clearer view

    fig = go.Figure(data=go.Isosurface(
        x=X.flatten(),
        y=Z.flatten(),
        z=Y.flatten(),
        value=values.flatten(),
        isomin = vmin + 1000,
        isomax = vmax - 10000,
        opacity=0.10, # needs to be small to see through all surfaces
        colorbar_nticks=5,
        surface_count=5, # needs to be a large number for good volume rendering
        ))
    fig.update_layout(
    scene = dict(
        xaxis = dict(range=[0,600], title="X position"),
        yaxis = dict(range=[0,248], title="Z position"),
        zaxis = dict(range=[slice[0],slice[-1]], title="Y position")),
        width=1000,
        height=1000)
    fig.update_layout(scene_aspectmode='data')
    fig.show()       


def YsliceExtractor(timestep, prop_name):   
    arguments = []
    tsep = ""
    if(timestep < 100): tstep = "0" + str(timestep)
    else: tstep = str(timestep) 
    filename = "multifield.0" + tstep + ".txt"
    
    temp_list = []
    temp_list.append(filename)
    temp_list.append(prop_name)

    arguments.append(temp_list)

    for args in arguments:
        graph_creator(args)

YsliceExtractor(60, "density")