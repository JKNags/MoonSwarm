import matplotlib.image as mpimg 
import matplotlib.pyplot as plt 
import matplotlib.markers as mmarkers
from matplotlib.animation import FuncAnimation
import numpy as np
import math

# Global Variables
min_blob_size = 8   # Distance for particle to reflect within blob
search_color = (255, 0, 0)
color_threshold_r = 200  # Min
color_threshold_g = 100   # Max
color_threshold_b = 100   # Max

def is_in_color(color):
	return color[0] > color_threshold_r and color[1] < color_threshold_g and color[2] < color_threshold_b

# Read Image
#img = mpimg.imread('grail_gravity_map_moon_sm.jpg')[::-1,:]
img = mpimg.imread('test/test4.jpg')[::-1,:]#[:,:,:3]

# Figure
fig, ax = plt.subplots()

img_x = img.shape[1]   # get x size
img_y = img.shape[0]   # get y size
plt.xlim(0,img_x)   # set x limits of plot
plt.ylim(0,img_y)   # set y limits of plot

#print ("X=", img.shape[1])
#print ("Y=", img.shape[0])

# Output Images 
ax.imshow(img, origin='lower')    # show gravity map on plot

states = {0:"Travelling", 1:"Measuring blob"}   # states a particle can be in

# return random int
# n - item count, d - dimentions per item
velocity_min = -3
velocity_max = 3
def get_rand_velocity(n, d):
	a = [x for x in range(velocity_min, velocity_max+1)]
	return np.random.choice(a, (n, d))

# Create Swarm
num_groups = 1
swarm_size = 1
swarm = np.zeros(swarm_size, dtype=[('position',       int, 2),    # Position (x,y)
                                   ('velocity',        int, 2),    # Velocity (dx,dy)
                                   ('color',           float, 3),  # Color (r,g,b)
                                   ('group_num',	   int, 1),    # Group
                                   ('state',   		   int, 1),    # Is currently tracing edge
                                   ('blob_num',        int, 1),    # Number of blob it is tracking. 0=none
								   ('in_color_count',  int, 1)])   # Num iter in color

scale = 10
particle_size = 25 * scale  # Set particle size
edge_color = (0, 0, 0, 1)   # Set global outline color
swarm['position'][:, 0] = np.random.randint(0, img_x, swarm_size)   # Set random Y position in px
swarm['position'][:, 1] = np.random.randint(0, img_y, swarm_size)   # Set random X position in px
swarm['velocity'] = get_rand_velocity(swarm_size, 2)   # Set velocity components in px
#particle['color'] = (1, 0.0784, 0.576)   # pink color
swarm['color'] = [tuple(img[particle['position'][1]][particle['position'][0]]) for particle in swarm]
swarm['blob_num'] = -1

step = int(float(swarm_size)/num_groups)
for group_num in range(0, num_groups):
	swarm[group_num * step : group_num * step + step]['group_num'] = group_num

#print swarm

# Blob data
next_blob_num = 0   # for use when a new blob is discovered
blobs = np.empty(0, dtype=[('max_sqr_found',    int, 1),
						   ('num_reflections',  int, 1),
						   ('position',			int, 2)])

"""
THIS IS FOR TESTING, REMOVE LATER
"""
swarm['position'][:,0] = 1 #180 #182
swarm['position'][:,1] = 1 #88 #386
#swarm['velocity'] = (1,1)
"""
THIS IS FOR TESTING, REMOVE LATER
"""


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

# Return true if inside, false if outside
def is_inside_img_bounds(_x, _y):
	return not ((_x < 0) or (_x > img_x-1) or (_y < 0) or (_y > img_y-1))

# Check for position bounds and adjust velocity
def adjust_for_img_bounds(_x, _y, _vx, _vy, particle):
	if (_x + _vx < 0):   # check min bounds x
		_x = 0
		_vx *= -1
		particle['in_color_count'] = 0   # reset counter
	elif (_x + _vx > (img_x - 1)):   # check max bounds x, sub 1 bc img_x is size not index
		_x = (img_x - 1)
		_vx *= -1
		particle['in_color_count'] = 0   # reset counter
	else:
		_x += _vx   # normal movement

	if (_y + _vy < 0):   # check min bounds y
		_y = 0
		_vy *= -1
		particle['in_color_count'] = 0   # reset counter
	elif (_y + _vy > (img_y - 1)):   # check max bounds y
		_y = (img_y - 1)
		_vy *= -1
		particle['in_color_count'] = 0   # reset counter
	else:
		_y += _vy   # normal movement
	return _x, _y, _vx, _vy

# Calculate estimated area of a circle given squared radius
def calculate_A_circle_sqr(r2):
	return 3.1415927 * r2

# Called every animation frame
def update(frame_number):
	#print "Frame %d" % frame_number
	global next_blob_num

	for p_idx,particle in enumerate(swarm):
		x = particle['position'][0]   # position x coordinate
		y = particle['position'][1]   # position y coordinate
		vx = particle['velocity'][0]   # velocity x component
		vy = particle['velocity'][1]   # velocity y component

		# Check if current position is in color
		position_color = tuple(img[y][x])
		#print "P%d color = %s" % (idx, position_color)

		# Check that state is travelling
		if (particle['state'] == 0):
			# Check if current position is in color
			if (is_in_color(position_color)):
				print "X(%d, %d), V(%d, %d), RED, CC=%d : in red" % (x,y,vx,vy, particle['in_color_count'])

				# Check if travelled far enough into blob
				d = (abs(vx) + abs(vy)) * particle['in_color_count']   # distance travelled
				if (d >= min_blob_size):
					particle['state'] = 1

					if (particle['blob_num'] < 0):
						# First blob found for group
						print 'assigning new blob num -', next_blob_num
						blobs.resize(next_blob_num + 1)   # add new blob to list
						swarm[particle['group_num'] * step : particle['group_num'] * step + step]['blob_num'] = next_blob_num
						blobs[next_blob_num]['position'] = (x, y)   # set approximate position of blob
						next_blob_num += 1

					print "\tEntered in blob state"
				else:
					particle['in_color_count'] += 1    # increment counter
			else:
				print "X(%d, %d), V(%d, %d) : not in color" % (x,y,vx,vy)
				
				particle['in_color_count'] = 0   # reset counter

				# Randomly mutate velocity, ensure both not 0
				while(True):
					vx = vx if (np.random.rand() > 0.05) else get_rand_velocity(1, 1) 
					vy = vy if (np.random.rand() > 0.05) else get_rand_velocity(1, 1)
					if (vx != 0 or vy != 0):   # loop while both == 0
						break

			x, y, vx, vy = adjust_for_img_bounds(x, y, vx, vy, particle)

		# Check that state is searching blob
		if (particle['state'] == 1):
			print "X(%d, %d), V(%d, %d), %s : State == 1" % (x,y,vx,vy,"RED" if is_in_color(position_color) else "",)

			# Check if next position will be out of bounds or outside blob
			if (is_inside_img_bounds(x + vx, y + vy) and not is_in_color(tuple(img[y + vy][x + vx]))):
				# need to reduce velocity to just hit in color edge next update

				a = particle['in_color_count'] * vx   # calc distance using iterations and velocity
				b = particle['in_color_count'] * vy

				next_vx = vx * -1   # store reversed velocity
				next_vy = vy * -1   # store reversed velocity

				# Slightly change velocity
				#pos_range = [v for v in range(0, velocity_max+1)]
				#neg_range = [v for v in range(velocity_min, 1)]
				#all_range = np.union1d(pos_range,neg_range)
				all_range = [v for v in range(velocity_min, velocity_max+1)]
				pos_range = all_range[len(all_range)/2:]
				neg_range = all_range[0:len(all_range)/2+1]

				while (True):   # loop to ensure both components != 0
					if (next_vx > 0):
						next_vx = np.random.choice(pos_range)
					elif (next_vx == 0):
						next_vx = np.random.choice(all_range)
					else:
						next_vx = np.random.choice(neg_range)
					if (next_vy > 0):
						next_vy = np.random.choice(pos_range)
					elif (next_vy == 0):
						next_vy = np.random.choice(all_range)
					else:
						next_vy = np.random.choice(neg_range)

					if (next_vx != 0 or next_vy != 0):  # redraw if both == 0
						break

				while (True):   # loop to find nearest position that's in color
					if (vx != 0):
						vx += -1 if vx > 0 else 1
					if (is_in_color(tuple(img[y + vy][x + vx]))):
						break
					if (vy != 0):
						vy += -1 if vy > 0 else 1
					if (is_in_color(tuple(img[y + vy][x + vx]))):
						break

				a += vx   # add last movements to distance
				b += vy

				x = x + vx   # set position as just on the edge
				y = y + vy
				vx = next_vx   # set velocity as reverse of previous
				vy = next_vy

				c2 = a**2 + b**2   # calculate Euclidean c^2,  where c^2 / 4 = r^2 
				r2 = c2 / 4
				approx_blob_area = calculate_A_circle_sqr(r2)

				print "\tflipped V, setting x=%d,y=%d, COUNT=%d, A=%.2f" % \
						(x,y, particle['in_color_count'], approx_blob_area)

				particle['in_color_count'] = 0   # reset counter
				
				blob_num = particle['blob_num']    # get particle's blob num
				blobs[blob_num]['num_reflections'] += 1   # increment reflections in blob
				if (blobs[blob_num]['max_sqr_found'] < r2):   # set max squared radius if found is greater
					print '\tsetting max area of blob'
					blobs[blob_num]['max_sqr_found'] = r2
			else:
				print "\tnormal update"
				particle['in_color_count'] += 1    # increment counter
				x, y, vx, vy = adjust_for_img_bounds(x, y, vx, vy, particle)

		# set particle data
		particle['position'][0] = x
		particle['position'][1] = y
		particle['velocity'][0] = vx
		particle['velocity'][1] = vy
		particle['color'] = position_color
		markers[p_idx] = (3, 0, math.degrees(math.atan2(vy, vx))-90)
	
	set_markers()   # update rotation of plot markers

    # Update the scatter collection
	scatter_plot.set_facecolor(swarm['color'] / 255.0)
	scatter_plot.set_offsets(swarm['position'])
	

	#if (frame_number == 20):
	#	animation.event_source.stop()

# Mouse click event
def onclick(event):
	try:
		# Print image data at click location
		if (event.ydata is not None and event.xdata is not None):
			x = int(round(event.xdata))
			y = int(round(event.ydata))
			color = tuple(img[y][x])
			print "click at (%d, %d) : %s : %s" \
				% (x,y, color, "IN_COLOR" if is_in_color(color) else "NOT_IN_COLOR")
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
interval = 300
min_interval = 25
max_interval = 500
iterations = 180
click_cid = fig.canvas.mpl_connect('button_press_event', onclick)
btn_cid = fig.canvas.mpl_connect('key_press_event', onpress)

plt.grid(True)   # Show grid on axes
animation = FuncAnimation(fig, update, interval=interval)#, frames=iterations)
plt.show()   # Show plot
#animation.save("path1.mp4", fps=20)


