import matplotlib.image as mpimg 
import matplotlib.pyplot as plt 
import matplotlib.markers as mmarkers
from matplotlib.animation import FuncAnimation
import numpy as np
import math

# Global Variables
min_blob_size = 20   # Distance for particle to reflect within blob
search_color = (255, 0, 0)
color_threshold_r = 225  # Min
color_threshold_g = 80   # Max
color_threshold_b = 80   # Max

def is_in_color(color):
	return color[0] > color_threshold_r and color[1] < color_threshold_g and color[2] < color_threshold_b

# Read Image
img = mpimg.imread('grail_gravity_map_moon.jpg') 
#img = mpimg.imread('test1.jpg')[:,:,:3]

# Figure
fig, ax = plt.subplots()

img_x = img.shape[1]   # get x size
img_y = img.shape[0]   # get y size
plt.xlim(0,img_x)   # set x limits of plot
plt.ylim(0,img_y)   # set y limits of plot

#print ("X=", img.shape[1])
#print ("Y=", img.shape[0])

# Output Images 
ax.imshow(img)   # show gravity map on plot

# Create Swarm
swarm_size = 1
swarm = np.zeros(swarm_size, dtype=[('position',  int, 2),   # Position (x,y)
                                   ('velocity',  int, 2),    # Velocity (dx,dy)
                                   ('color',     float, 3),  # Color (r,g,b)
                                   ('in_color_count', int, 1)])  

# return random int, not 0
def get_rand_velocity(n, d):
	return np.random.choice([-5,-4,-3,-2,-1,1,2,4,5], (n, d))

scale = 10
particle_size = 25 * scale  # Set particle size
#radius = particle_size * 0.08
edge_color = (0, 0, 0, 1)   # Set global outline color
swarm['position'][:, 0] = np.random.randint(0, img_x, swarm_size)   # Set random Y position in px
swarm['position'][:, 1] = np.random.randint(0, img_y, swarm_size)   # Set random X position in px
swarm['velocity'] = get_rand_velocity(swarm_size, 2)   # Set velocity components in px
#particle['color'] = (1, 0.0784, 0.576)   # pink color
swarm['color'] = [tuple(img[particle['position'][1]][particle['position'][0]]) for particle in swarm]



swarm['position'][:, 0] = 147
swarm['position'][:, 1] = 344



# Create initial scatter plot
scatter_plot = ax.scatter(swarm['position'][:, 0], swarm['position'][:, 1],
            c=(swarm['color'] / 255.0), s=particle_size, lw=0.5, 
            edgecolors=edge_color, facecolors='none')

# Update plot for markers to show velocity
#   ( num_sides=3, style=0=regular_polygon, angle=atan2(y/x) )
markers = [(3, 0, math.degrees(math.atan2(particle['velocity'][1], particle['velocity'][0]))-90) for particle in swarm]

def set_markers():
	paths = []
	for marker in markers:
		marker_obj = mmarkers.MarkerStyle(marker)
		path = marker_obj.get_path().transformed(marker_obj.get_transform())
		paths.append(path)
	scatter_plot.set_paths(paths)

set_markers() # set plot markers as triangles with rotation wrt velocity


def update(frame_number):
	for p_idx,particle in enumerate(swarm):
		x = particle['position'][0]   # position x coordinate
		y = particle['position'][1]   # position y coordinate
		vx = particle['velocity'][0]   # velocity x component
		vy = particle['velocity'][1]   # velocity y component
		
		# Check for position bounds and adjust velocity
		if (x + vx < 0):   # check min bounds x
			x = 0
			vx *= -1
		elif (x + vx > (img_x - 1)):   # check max bounds x, sub 1 bc img_x is size not index
			x = (img_x - 1)
			vx *= -1
		else:
			x += vx   # normal movement

		if (y + vy < 0):   # check min bounds y
			y = 0
			vy *= -1
		elif (y + vy > (img_y - 1)):   # check max bounds y
			y = (img_y - 1)
			vy *= -1
		else:
			y += vy   # normal movement

		# Check position and surrounding color data
		position_color = tuple(img[y][x])
		#print "P%d color = %s" % (idx, position_color)
		surrounding_colors = [None,None,None,None,None,None,None,None]
		try:
			# check bounds for using [y|x][minus|plus]
			xm = x != 0   # can use x-1
			ym = y != 0   # can use y-1
			xp = x != img_x-1   # can use x+1
			yp = y != img_y-1   # can use y+1

			# 0 1 2
			# 3 X 4
			# 5 6 7

			if (yp):
				surrounding_colors[1] = tuple(img[y+1][x])
				if (xm):
					surrounding_colors[0] = tuple(img[y+1][x-1])
				if (xp):
					surrounding_colors[2] = tuple(img[y+1][x+1])
			if (xm):
				surrounding_colors[3] = tuple(img[y][x-1])
			if (xp):
				surrounding_colors[4] = tuple(img[y][x+1])
			if (ym):
				surrounding_colors[6] = tuple(img[y-1][x])
				if (xm):
					surrounding_colors[5] = tuple(img[y-1][x-1])
				if (xp):
					surrounding_colors[7] = tuple(img[y-1][x+1])
		except:
			print "error"

		# Check if position color in color threshold
		if (is_in_color(position_color)):
			print position_color,"IS RED!"

			# Find direction of best red
			best_node_idx = -1
			best_dist = 1000
			for c_idx,surrounding_color in enumerate(surrounding_colors):
				dist = abs(search_color[0] - surrounding_color[0]) + \
					abs(search_color[1] - surrounding_color[1]) + abs(search_color[2] - surrounding_color[2])
				if (dist < best_dist):
					best_dist = dist
					best_node_idx = c_idx

			print "\tMoving to idx:",best_node_idx

			if (particle['in_color_count'] == 0):
				# Change velocity wrt current velocity
				if (best_node_idx <= 2):
					vy = 1
				elif (best_node_idx <= 4):
					vy = 0
				else:
					vy = -1

				if (best_node_idx in (2,4,7)):
					vx = 1
				elif (best_node_idx in (1,6)):
					vx = 0
				else:
					vx = -1

			particle['in_color_count'] += 1
		else:
			print position_color

			if (particle['in_color_count'] > 0):
				# particle was just in color, reverse
				vx *= -1
				vy *= -1
			else:
				particle['in_color_count'] = 0
				# Randomly change velocity
				vx = vx if (np.random.rand() > 0.02) else get_rand_velocity(1, 1) 
				vy = vy if (np.random.rand() > 0.02) else get_rand_velocity(1, 1)
			


		# set particle data
		particle['position'][0] = x
		particle['position'][1] = y
		particle['velocity'][0] = vx
		particle['velocity'][1] = vy
		particle['color'] = position_color
		markers[p_idx] = (3, 0, math.degrees(math.atan2(vy, vx))-90)
	
	set_markers()   # update rotation of plot markers

    # Update the scatter collection
	scatter_plot.set_offsets(swarm['position'])
	scatter_plot.set_facecolor(swarm['color'] / 255.0)

	#if (frame_number == 20):
	#	animation.event_source.stop()

# Mouse click event
def onclick(event):
	try:
		# Print image data at click location
		print "click at (%.2f, %.2f) : %s" % (event.xdata, event.ydata, tuple(img[int(event.ydata)][int(event.xdata)]))
	except Exception as e:
		print e
		pass

# Keyboard click event
def onpress(event):
	global run_anim
	global interval, min_interval, max_interval

	# Start/Stop animation on any key press
	if (event.key == "x"):
		if (run_anim):
			run_anim = False
			animation.event_source.stop()
		else:
			run_anim = True
			animation.event_source.start()

	# Change animation interval
	# NOT WORKING
	if (event.key == "-" and interval > min_interval):
		interval -= 25
		animation.event_source.interval = interval
	if (event.key == "=" and interval < max_interval):
		interval += 25
		animation.event_source.interval = interval

run_anim = True
interval = 200
min_interval = 25
max_interval = 500
click_cid = fig.canvas.mpl_connect('button_press_event', onclick)
btn_cid = fig.canvas.mpl_connect('key_press_event', onpress)

plt.grid(True)   # Show grid on axes
animation = FuncAnimation(fig, update, interval=interval)
plt.show()   # Show plot


