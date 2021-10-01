import numpy as np
import plotly.graph_objects as go

def get_the_slice(x,y,z, surfacecolor):
    return go.Surface(x=x,
                      y=y,
                      z=z,
                      surfacecolor=surfacecolor,
                      coloraxis='coloraxis')


def get_lims_colors(surfacecolor):# color limits for a slice
    return np.min(surfacecolor), np.max(surfacecolor)

scalar_f = lambda x,y,z: x*np.exp(-x**2-y**2-z**2)


x = np.linspace(-2,2, 50)
y = np.linspace(-2,2, 50)
x, y = np.meshgrid(x,y)
z = np.zeros(x.shape)
surfcolor_z = scalar_f(x,y,z)
sminz, smaxz = get_lims_colors(surfcolor_z)

slice_z = get_the_slice(x, y, z, surfcolor_z)

x = np.linspace(-2,2, 50)
z = np.linspace(-2,2, 50)
x, z = np.meshgrid(x,y)
y = -0.5 * np.ones(x.shape)
surfcolor_y = scalar_f(x,y,z)
sminy, smaxy = get_lims_colors(surfcolor_y)
vmin = min([sminz, sminy])
vmax = max([smaxz, smaxy])
slice_y = get_the_slice(x, y, z, surfcolor_y)

def colorax(vmin, vmax):
    return dict(cmin=vmin,
                cmax=vmax)

fig1 = go.Figure(data=[slice_z, slice_y])
fig1.update_layout(
         title_text='Slices in volumetric data', 
         title_x=0.5,
         width=700,
         height=700,
         scene_zaxis_range=[-2,2], 
         coloraxis=dict(colorscale='BrBG',
                        colorbar_thickness=25,
                        colorbar_len=0.75,
                        **colorax(vmin, vmax)))            
      
fig1.show()