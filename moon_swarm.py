import matplotlib.image as mpimg 
import matplotlib.pyplot as plt 
import matplotlib.markers as mmarkers
from matplotlib.animation import FuncAnimation
import numpy as np
import math

# Global Variables
min_blob_size = 20   # Distance for particle to reflect within blob
color_threshold_r = 230  # Min
color_threshold_g = 50   # Max
color_threshold_b = 50   # Max

# Read Image
img = mpimg.imread('grail_gravity_map_moon.jpg') 

#		   y  x
#print img[0][3]

# Figure
#fig = plt.figure() #figsize=(7,7))
fig, ax = plt.subplots()

#print(img)
#print("Data type of img > ", type(img))
#print("Shape of img > ", img.shape)
#print("Dimention of img > ",img.ndim)

img_x = img.shape[1]   # get x size
img_y = img.shape[0]   # get y size
plt.xlim(0,img_x)   # set x limits of plot
plt.ylim(0,img_y)   # set y limits of plot

#ax = fig.add_axes([0, 0, 1, 1], frameon=False)
#ax.set_xlim(0,1), ax.set_xticks([])
#ax.set_ylim(0,1), ax.set_yticks([])

print ("X=", img.shape[1])
print ("Y=", img.shape[0])

# Output Images 
ax.imshow(img)   # show gravity map on plot
#ax.figure.figimage(img,0,0)

# Create Swarm
swarm_size = 50
swarm = np.zeros(swarm_size, dtype=[('position',  int, 2),   # Position (x,y)
                                    ('velocity',  int, 2),   # Velocity (dx,dy)
                                    ('color',     int, 3)])  # Color (r,g,b,a)

def get_rand_velocity(n, d):
	return np.random.choice([-5,-4,-3,-2,-1,1,2,4,5], (n, d))

scale = 5
particle_size = 25 * scale  # Set particle size
radius = particle_size * 0.08
arrow_width = particle_size * 0.05
arrow_head_width = particle_size * 0.12
arrow_head_length = particle_size * 0.12
edge_color = (0, 0, 0, 1)   # Set global outline color
swarm['position'][:, 0] = np.random.randint(0, img_x, swarm_size)   # Set random Y position in px
swarm['position'][:, 1] = np.random.randint(0, img_y, swarm_size)   # Set random X position in px
swarm['velocity'] = get_rand_velocity(swarm_size, 2)   # Set velocity components in px
for particle in swarm:
	particle['color'] = img[particle['position'][1]][particle['position'][0]] #(1, 0.0784, 0.576)   # Set initial RGBA color to pink, can change on location?

# Create initial scatter plot
scatter_plot = ax.scatter(swarm['position'][:, 0], swarm['position'][:, 1],
            c=swarm['color'], s=particle_size, lw=0.5, 
            edgecolors=edge_color, facecolors='none')

# Update plot for markers to show velocity
markers = [(3, 0, math.degrees(math.atan2(particle['velocity'][1], particle['velocity'][0]))-90) for particle in swarm]

def set_markers():
	paths = []
	for marker in markers:
		marker_obj = mmarkers.MarkerStyle(marker)
		path = marker_obj.get_path().transformed(marker_obj.get_transform())
		paths.append(path)
	scatter_plot.set_paths(paths)

# Create arrows for scatter plot
#ax = plt.axes()
"""
arrows = [swarm_size]

def set_arrow(idx):
	particle = swarm[idx]
	x = particle['position'][0]   # position x coordinate
	y = particle['position'][1]   # position y coordinate
	vx = particle['velocity'][0]   # velocity x component
	vy = particle['velocity'][1]   # velocity y component
	rad = math.atan2(vy, vx)   # rotation in rad of velocity
	arrow_x = math.cos(rad) * radius   # base of velocity arrow x
	arrow_y = math.sin(rad) * radius   # base of belocity arrow y
	arrow_dx = arrow_x * abs(vx) * 0.3   # tip of velocity arrow x
	arrow_dy = arrow_y * abs(vy) * 0.3   # tip of velocity arrow y
	arrows.append(ax.arrow(x + arrow_x, y + arrow_y, 
			arrow_dx, arrow_dy,
			fc=particle['color'], ec=edge_color, width=arrow_width,
			head_width=arrow_head_width, head_length=arrow_head_length))

for idx,particle in enumerate(swarm):
	set_arrow(idx)
"""

def update(frame_number):
	for idx,particle in enumerate(swarm):
		x = particle['position'][0]   # position x coordinate
		y = particle['position'][1]   # position y coordinate
		vx = particle['velocity'][0]   # velocity x component
		vy = particle['velocity'][1]   # velocity y component
		
		if (x + vx < 0):   # check min bounds x
			x = 0
			vx *= -1
		elif (x + vx > img_x):   # check max bounds x
			x = img_x
			vx *= -1
		else:
			x += vx   # normal movement

		if (y + vy < 0):   # check min bounds y
			y = 0
			vy *= -1
		elif (y + vy > img_y):   # check max bounds y
			y = img_y
			vy *= -1
		else:
			y += vy   # normal movement

		# set particle data
		particle['position'][0] = x
		particle['position'][1] = y
		particle['velocity'][0] = vx if (np.random.rand() > 0.05) else get_rand_velocity(1, 1) 
		particle['velocity'][1] = vy if (np.random.rand() > 0.05) else get_rand_velocity(1, 1) 
		markers[idx] = (3, 0, math.degrees(math.atan2(vy, vx))-90)
	
	set_markers()

    # Update the scatter collection
	scatter_plot.set_offsets(swarm['position'])
	#TODO: set color


#plt.grid(True)   # Show grid on axes
#animation = FuncAnimation(fig, update, interval=100)
plt.show()   # Show plot
