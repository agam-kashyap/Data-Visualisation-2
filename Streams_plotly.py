import plotly.graph_objects as go
import math
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os
from tqdm import tqdm

def graph_creator(args):
    file = args[0]
    slicenum = args[1]
    # prop_name = args[2]
    print("Reading "+ file)
    openfile = open("./Velocity/ExtractedCompleteData/" + file,"r")
    timestep = file.split(".")[1]

    # colorfile = open("../Multifield/ExtractedCompleteData/multifield."+timestep+".txt")

    indices = []
    for i in range(0,248):
        for j in range(0,600):
            indices.append(600*248*i + 600*slicenum + j)
            indices.append(600*248*i + 600*(slicenum+1) + j)

    datapoint = []
    # data_prop = []
    for i in tqdm(range(0, 600*248*248)):
        dp = openfile.readline()
        datapoint.append(dp)

        # cf = colorfile.readline()
        # props = cf.split(" ")
        # data_prop.append(float(props[properties[prop_name]["pos"]]))

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

    # curl(x,y) 
    # curl(y,z)
    # index iteration will be from [0, 599) for X, [0, 248) for Z, since the i+1, k+1 indices are required for calculation
    # So, we should have data of 599*248

    # For a given (i,j,k) it's linear index can be given as: 
    # X*Y*k + X*j + i

    curl_xy = []
    curl_yz = []
    X_pos = []
    Z_pos = []
    X = 600
    Y = 248

    # colorval = []

    max_c_xy = -1
    min_c_xy = 10e9
    max_c_yz = -1
    min_c_yz = 10e9

    limiter = 0
    for i in tqdm(range(599)):
        for j in range(247):
            if(limiter%100 == 0):
                vy_i1jk = req_data[X*Y*j + X*(slicenum+1) + i]["Y"]
                vy_ijk  = req_data[X*Y*j + X*slicenum + i]["Y"]
                vx_ij1k = req_data[X*Y*(j+1) + X*slicenum + i]["X"]
                vx_ijk  = req_data[X*Y*j + X*slicenum + i]["X"]

                vz_ij1k = req_data[X*Y*j + X*(slicenum+1) + i]["Z"]
                vz_ijk  = req_data[X*Y*j + X*slicenum + i]["Z"]
                vy_ijk1 = req_data[X*Y*(j+1) + X*slicenum + i]["Y"]

                X_pos.append(i)
                Z_pos.append(j)
                
                calc_curl_xy = (vy_i1jk - vy_ijk - vx_ij1k + vx_ijk)/0.001
                calc_curl_yz = (vz_ij1k - vz_ijk - vy_ijk1 + vy_ijk)/0.001
                curl_xy.append(calc_curl_xy)
                curl_yz.append(calc_curl_yz)

                if(calc_curl_xy < min_c_xy): min_c_xy = calc_curl_xy
                if(calc_curl_xy > max_c_xy): max_c_xy = calc_curl_xy
                if(calc_curl_yz < min_c_yz): min_c_yz = calc_curl_yz
                if(calc_curl_yz > max_c_yz): max_c_yz = calc_curl_yz

                # colorval.append(data_prop[X*Y*j + X*slicenum + i])
            
            limiter+=1

    for i in range(len(curl_xy)):
        curl_xy[i] = math.tanh(curl_xy[i])
        curl_yz[i] = math.tanh(curl_yz[i])

    fig, (ax, cax) = plt.subplots(nrows=2, figsize=(10,8), gridspec_kw={"height_ratios":[1, 0.05]})
    ax.set_title("Velocity Quiver with Temp Colormap XZ "+timestep+ " slice125", fontsize=15)
    f = ax.quiver(X_pos, Z_pos, curl_yz, curl_xy, scale=50)
    cb = fig.colorbar(f, cax=cax, orientation="horizontal")
    ax.set_xlabel('X position($10^{-3}$ parsecs)', fontsize=10)
    ax.set_ylabel('Z position($10^{-3}$ parsecs)', fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.tick_params(axis='both', which='minor', labelsize=10)
    fig.canvas.draw()  
    fig.savefig("./Images/XZ.velocity.slice"+str(slicenum)+"."+ timestep+ ".png", dpi=300)
    plt.figure().clear()
    plt.cla()
    plt.clf()
    print(timestep + " complete!")

def YsliceExtractor(slicenum):   
    arguments = []
    for file in sorted(os.listdir("./ExtractedCompleteData")):
        temp_list = []
        temp_list.append(file)
        temp_list.append(slicenum)
        # temp_list.append(prop_name)
        arguments.append(temp_list)

    for args in arguments:
        graph_creator(args)

YsliceExtractor(125)

def AnimCreator():
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    fig_dict["layout"]["xaxis"] = {"range": [0, 600], "title": "X coordinate"}
    fig_dict["layout"]["yaxis"] = {"range": [0, 248], "title": "Z coordinate"}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": False},
                                    "fromcurrent": True, "transition": {"duration": 300,"easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]
    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size":20},
            "prefix": "Timestep: ",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": [] 
    }