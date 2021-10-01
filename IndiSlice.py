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


def GraphCreator(args):
    filereader = open("./Multifield/ExtractedCompleteData/" + args[0], "r")
    timestep = args[0].split(".")[1]
    prop_name = args[1]
    planeEq = args[2]
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

    #TO perform Axis Aligned slicing -> Extract plane Y=Slicenum. 
    #For arbitrary plane, identify the z values that fall on this plane
    #Plane: Ax + By + Cz = D
    #For a given (A,B,C,D),(x,y) we can calculate the y value as:
    # y = (D - Ax - Cz)/B
    # We will colormap according to the values present at (x,y,z)

    X_len = 600
    Z_len = 248
    Y_coords = [[0 for i in range(Z_len)] for i in range(X_len)] #shape = (X_len, Z_len)
    X_coords, Z_coords = np.mgrid[0:X_len, 0:Z_len]

    val_dict = dict()

    frames = []

    k_change = planeEq[3]/2
    for kc in range(-5,5):
        temp_planeEq = planeEq.copy()
        temp_planeEq[3] += kc*k_change

        temp_Y_coords = Y_coords.copy()

        for i in range(X_len):
            for j in range(Z_len):
                if(temp_planeEq[1] == 0): 
                    temp_Y_coords[i][j] = j # Handles parallel to Yaxis condition
                else: 
                    temp_Y_coords[i][j] = (int)((temp_planeEq[3] - temp_planeEq[0]*i -temp_planeEq[2]*j)/temp_planeEq[1])
        
        #Will store the property values and be used for colormapping
        prop_values = [[0 for i in range(Z_len)] for i in range(X_len)] 
        for i in range(X_len):
            for j in range(Z_len):
                if(temp_Y_coords[i][j] < 0 or temp_Y_coords[i][j] >=248):
                    prop_values[i][j] = properties[prop_name]["vmin"]
                else:
                    prop_values[i][j] = selected_property[X_len*Z_len*j + 600*temp_Y_coords[i][j] + i]
        
        val_dict[kc] = dict(coord = temp_Y_coords, value = prop_values)
    
        frame = go.Frame(data = go.Surface(
                        x = X_coords,
                        y = Z_coords,
                        z = val_dict[kc]["coord"],
                        surfacecolor = val_dict[kc]["value"],
                        coloraxis='coloraxis',
                        cmin = properties[prop_name]["vmin"],
                        cmax = properties[prop_name]["vmax"]
                ),
                name = str(kc))
        frames.append(frame)
    
    fig = go.Figure(frames=frames) 
    fig.add_trace(
        go.Surface(
            x = X_coords,
            y = Z_coords,
            z = val_dict[0]["coord"],
            surfacecolor = val_dict[0]["value"],
            coloraxis='coloraxis',
            cmin = properties[prop_name]["vmin"],
            cmax = properties[prop_name]["vmax"]
        )
    )
    fig.update_layout(
        title_text = "Arbitrary Volume Slicing " + str(kc) ,
        coloraxis=dict(
            colorscale=properties[prop_name]["cmap"],
        )
    )
    
    def frame_args(duration):
        return {
                "frame": {"duration": duration},
                "mode": "immediate",
                "fromcurrent": True,
                "transition": {"duration": duration, "easing": "linear"},
            }

    sliders = [
                {
                    "pad": {"b": 10, "t": 60},
                    "len": 0.9,
                    "x": 0.1,
                    "y": 0,
                    "steps": [
                        {
                            "args": [[f.name], frame_args(0)],
                            "label": str(k),
                            "method": "animate",
                        }
                        for k, f in enumerate(fig.frames)
                    ],
                }
            ]
    fig.update_layout(
        scene=dict(
            xaxis = dict(range=[0,600]),
            yaxis = dict(range=[0,248]),
            zaxis = dict(range=[0,248])),
        width = 900,
        height = 900,
         updatemenus = [
            {
                "buttons": [
                    {
                        "args": [None, frame_args(50)],
                        "label": "&#9654;", # play symbol
                        "method": "animate",
                    },
                    {
                        "args": [[None], frame_args(0)],
                        "label": "&#9724;", # pause symbol
                        "method": "animate",
                    },
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 70},
                "type": "buttons",
                "x": 0.1,
                "y": 0,
            }
         ],
         sliders=sliders
    )
    fig.show()

def SliceExtractor(timestep, prop_name, planeEq):   
    arguments = []
    tsep = ""
    if(timestep < 100): tstep = "0" + str(timestep)
    else: tstep = str(timestep) 
    filename = "multifield.0" + tstep + ".txt"
    
    temp_list = []
    temp_list.append(filename)
    temp_list.append(prop_name)
    temp_list.append(planeEq)

    arguments.append(temp_list)

    for args in arguments:
        GraphCreator(args)

def crossproduct(A, B):
    x = A[1]*B[2] - A[2]*B[1]
    y = - A[0]*B[2] + A[2]*B[0]
    z = A[0]*B[1] - A[1]*B[0]
    return [x,y,z]

def sub(A,B):
    return [A[0]-B[0], A[1]-B[1], A[2]-B[2]]

def GetPlaneEq(Point1, Point2, Point3):
    B_A = sub(Point2, Point1)
    C_A = sub(Point3, Point1)

    CP = crossproduct(B_A, C_A)

    k = lambda a : a[0]*Point1[0] + a[1]*Point1[1] + a[2]*Point1[2]
    D = k(CP)
    CP.append(D)
    return CP

# Example 1 : Plane Parallel to Y axis
Point1 = [0,0,247]
Point2 = [0,247,247]
Point3 = [600,247,0]
planeEq_1 = GetPlaneEq(Point1, Point2, Point3)

# print(planeEq_1)

# Example 2 : Completely Arbitrary Plane
Point1 = [0,50,0]
Point2 = [0,150,247]
Point3 = [590,50,0]
planeEq_2 = GetPlaneEq(Point1, Point2, Point3)

print(planeEq_2)

# This Works -> Just changing the K value gives us a parallel plane
pp_planeEq_2 = planeEq_2.copy()
pp_planeEq_2[3] += 7225000 

# Example 3: Plane Parallel to XZ plane
Point1 = [0,100,0]
Point2 = [0,100,247]
Point3 = [600,100,247]
planeEq_3 = GetPlaneEq(Point1, Point2, Point3)

# print(planeEq_3)

SliceExtractor(60, "density", planeEq_2)
# SliceExtractor(60, "density", pp_planeEq_2)