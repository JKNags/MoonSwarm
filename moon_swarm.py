import matplotlib.image as mpimg 
import matplotlib.pyplot as plt 
import matplotlib.markers as mmarkers
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import numpy as np
import math
import time

# Global Variables
min_blob_size = 25   # Distance for particle to reflect within blob
search_color_above = (255, 100, 100)   # Target color range
search_color_below = (200, 0, 0)
max_num_reflections = 40   # number of times particles reflect inside region for size estimation
swarm_size = 55
num_groups = 11
img_file_name = 'grail_gravity_map_moon.jpg'
velocity_min = -7   # Range of velocities particles can randomly take
velocity_max = 7
max_num_frames = 800   # End animation at this frame
use_position_colors = False   # Change particle color based on position or just white
show_anim = True   # Show animation running or just print results

def is_in_color(color):
	#return color[0] > color_threshold_r and color[1] < color_threshold_g and color[2] < color_threshold_b
	
	is_in = (color[0] >= search_color_below[0] and color[0] <= search_color_above[0]) \
		and (color[1] >= search_color_below[1] and color[1] <= search_color_above[1]) \
		and (color[2] >= search_color_below[2] and color[2] <= search_color_above[2])
	return is_in

# Read Image
img = mpimg.imread(img_file_name)[::-1,:]
#img = mpimg.imread('test/test7.jpg')[::-1,:]#[:,:,:3]

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
velocity_range = velocity_max - velocity_min
def get_rand_velocity(n, d):
	a = [x for x in range(velocity_min, velocity_max+1)]
	return np.random.choice(a, (n, d))

# Create Swarm
swarm = np.zeros(swarm_size, dtype=[('position',       		int,   2),    # Position (x,y)
                                   ('velocity',        		int,   2),    # Velocity (dx,dy)
                                   ('color',           		float, 3),  # Color (r,g,b)
                                   ('group_num',	   		int,   1),    # Group
                                   ('state',   		   		int,   1),    # Is currently tracing edge
                                   ('blob_num',        		int,   1),    # Number of blob it is tracking. 0=none
                                   ('reflection_position',  int,   2),    # Position of last reflection bounce
								   ('in_color_count',  		int,   1)])   # Num iter in color

scale = 10
particle_size = 25 * scale  # Set particle size
edge_color = (0, 0, 0, 1)   # Set global outline color
swarm['position'][:, 0] = np.random.randint(0, img_x, swarm_size)   # Set random Y position in px
swarm['position'][:, 1] = np.random.randint(0, img_y, swarm_size)   # Set random X position in px
swarm['velocity'] = get_rand_velocity(swarm_size, 2)   # Set velocity components in px
#particle['color'] = (1, 0.0784, 0.576)   # pink color
swarm['color'] = [tuple(img[particle['position'][1]][particle['position'][0]]) for particle in swarm]
swarm['blob_num'] = -1   # begin invalid
swarm['reflection_position'] = (-1,-1)   # begin invalid

step = int(float(swarm_size)/num_groups)
for group_num in range(0, num_groups):
	swarm[group_num * step : group_num * step + step]['group_num'] = group_num

#print swarm

# Blob data
next_blob_num = 0   # for use when a new blob is discovered
blobs = np.empty(0, dtype=[('max_r2_found',     int, 1),
						   ('num_reflections',  int, 1),
						   ('position',			int, 2)])

# Manually selected blobs for accuracy testing
actual_blobs = np.empty(12, dtype=[('r2',    int, 1),   # for accuracy in testing
						   ('position',		 int, 2)])

if (img_file_name == 'grail_gravity_map_moon.jpg'):
	actual_blobs[0]['position'] = (69, 482)
	actual_blobs[0]['r2'] = 1180.0
	actual_blobs[1]['position'] = (303, 643)
	actual_blobs[1]['r2'] = 490.0
	actual_blobs[2]['position'] = (215, 455)
	actual_blobs[2]['r2'] = 610.0
	actual_blobs[3]['position'] = (123, 327)
	actual_blobs[3]['r2'] = 400.0
	actual_blobs[4]['position'] = (319, 376)
	actual_blobs[4]['r2'] = 270.0
	actual_blobs[5]['position'] = (540, 485)
	actual_blobs[5]['r2'] = 70.0
	actual_blobs[6]['position'] = (977, 313)
	actual_blobs[6]['r2'] = 235.0
	actual_blobs[7]['position'] = (973, 172)
	actual_blobs[7]['r2'] = 395.0
	actual_blobs[8]['position'] = (1155, 136)
	actual_blobs[8]['r2'] = 125.0
	actual_blobs[9]['position'] = (1177, 293)
	actual_blobs[9]['r2'] = 390.0
	actual_blobs[10]['position'] = (1254, 532)
	actual_blobs[10]['r2'] = 2400.0
	actual_blobs[11]['position'] = (111, 626)
	actual_blobs[11]['r2'] = 265.0

for blob in actual_blobs:
	circle = Circle((blob['position'][0], blob['position'][1]), math.sqrt(blob['r2']), edgecolor=(1,1,1,1), facecolor=(.8, .5, .5, .2))
	ax.add_patch(circle)

# Create initial scatter plot
scatter_plot = ax.scatter(swarm['position'][:, 0], swarm['position'][:, 1],
            c=(swarm['color'] / 255.0 if use_position_colors else (1,1,1)), s=particle_size, lw=0.5, 
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

# Return accuracy of measurement
def accuracy(actual, observed):
	if (observed) == 0:
		return 0.0
	return abs(observed - actual) / float(observed)

# Print particles and blobs
def print_data():
	# Print Frame Number
	print "Frame Number:", global_frame_number

	# Print Particles #######################################################
	print "PARTICLES:"
	for particle in swarm:
		print "\tParticle X(x:%d,y:%d), V(x:%d,y:%d), %s, G%d, State:%d, blob:%d, cnt%d" %\
			(particle['position'][0], particle['position'][1], particle['velocity'][0], particle['velocity'][1], "IN_COLOR" if is_in_color(particle['color']) else "OUT_COLOR",\
				 particle['group_num'], particle['state'], particle['blob_num'], particle['in_color_count'])

	# Print Blobs ###########################################################
	print "BLOBS (%d):" % (len(blobs))
	blobs.sort(order='max_r2_found')   # sort ascending,  #TODO: THIS MESSES UP PARTICLE's blob_num
	
	for blob in blobs:
		blob_area = calculate_A_circle_r2(blob['max_r2_found'])

		min_dist = img_x + img_y   # arbitrary max	
		closest_actual_blob = None

		# find closest actual blob for accuracy
		for actual_blob in actual_blobs:
			dist = math.sqrt((actual_blob['position'][0] - blob['position'][0])**2 + (actual_blob['position'][1] - blob['position'][1])**2)
			if (dist < min_dist):
				min_dist = dist
				closest_actual_blob = actual_blob
		
		# build actual blob string
		closest_actual_blob_info = ""
		if (closest_actual_blob is not None):
			closest_actual_blob_area = calculate_A_circle_r2(closest_actual_blob['r2'])

			position_accuracy_x = accuracy(closest_actual_blob['position'][0], blob['position'][0])
			position_accuracy_y = accuracy(closest_actual_blob['position'][1], blob['position'][1])
			position_accuracy = (1.0 - position_accuracy_x) * (1.0 - position_accuracy_y) * 100   # combine position accuracy
			area_accuracy = 100 - accuracy(closest_actual_blob['r2'], blob['max_r2_found']) #100 - accuracy(closest_actual_blob_area, blob_area)
			closest_actual_blob_info = "ClosestActualBlob: P(%d,%d),A=%.2f,  X_accuracy=%.4f%%, A_accuracy=%.4f%%" % (closest_actual_blob['position'][0],closest_actual_blob['position'][1], \
									closest_actual_blob_area, position_accuracy, area_accuracy)

		# actually print info
		print "\tBlob P(X:%d, Y:%d) max_r2=%.2f,  A=%.2f,  num_refl=%d.  %s" \
			% (blob['position'][0], blob['position'][1], blob['max_r2_found'], blob_area, blob['num_reflections'], closest_actual_blob_info )

	# Print Actual Blobs ####################################################
	print "ACTUAL BLOBS (%d):" % (len(actual_blobs))
	position_accuracy_sum = 0
	area_accuracy_sum = 0
	for actual_blob in actual_blobs:
		actual_blob_area = calculate_A_circle_r2(actual_blob['r2'])

		min_dist = img_x + img_y   # arbitrary max	
		closest_blob = None

		# find closest actual blob for accuracy
		for blob in blobs:
			dist = math.sqrt((actual_blob['position'][0] - blob['position'][0])**2 + (actual_blob['position'][1] - blob['position'][1])**2)
			if (dist < min_dist):
				min_dist = dist
				closest_blob = blob
		
		closest_blob_info = ""
		if (closest_blob is not None):
			closest_blob_area = calculate_A_circle_r2(closest_blob['max_r2_found'])

			position_accuracy_x = accuracy(actual_blob['position'][0], closest_blob['position'][0])
			position_accuracy_y = accuracy(actual_blob['position'][1], closest_blob['position'][1])
			position_accuracy = (1.0 - position_accuracy_x) * (1.0 - position_accuracy_y) * 100   # combine position accuracy
			area_accuracy = 100 - (accuracy(actual_blob_area, closest_blob_area) * 100)
			closest_blob_info = "ClosestBlob: P(%d,%d),A=%.2f,  X_accuracy=%.4f%%, A_accuracy=%.4f%%" % (closest_actual_blob['position'][0],closest_actual_blob['position'][1], \
									closest_blob_area, position_accuracy, area_accuracy)
			
			position_accuracy_sum += position_accuracy
			area_accuracy_sum += area_accuracy

		# actually print info
		print "\tActualBlob P(%d, %d) r2=%.2f, A=%.2f. %s" \
			% (actual_blob['position'][0], actual_blob['position'][1], actual_blob['r2'], blob_area, closest_blob_info )		
	print "\tAvg Accuacy: Position=%.4f,  Area=%.4f" % (position_accuracy_sum / len(actual_blobs), area_accuracy_sum / len(actual_blobs))
	
# Check for position bounds and adjust velocity
def update_x_with_v(_x, _y, _vx, _vy, particle):
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
def calculate_A_circle_r2(r2):
	return 3.1415927 * r2

# Called every animation frame
global_frame_number = 0
def update(frame_number):
	global global_frame_number
	global_frame_number = frame_number
	#print "Frame %d" % frame_number
	global next_blob_num

	for p_idx,particle in enumerate(swarm):
		# extract particle data for easy access
		x = particle['position'][0]   # position x coordinate
		y = particle['position'][1]   # position y coordinate
		vx = particle['velocity'][0]   # velocity x component
		vy = particle['velocity'][1]   # velocity y component

		# Check if current position is in color
		position_color = tuple(img[y][x])
		#print "P%d color = %s" % (idx, position_color)

		#print "particle", p_idx
		
		# Check blob's reflections for max
		blob_num = particle['blob_num']
		if (blob_num >= 0):
			blob = blobs[blob_num]
			if (blob['num_reflections'] > max_num_reflections):
				#print "\nBlob %d reflection count maxed. resetting particles\n" % blob_num
				circle = Circle((blob['position'][0], blob['position'][1]), math.sqrt(blob['max_r2_found']), edgecolor=(.5,.5,.5,1), facecolor=(.8, .8, .8, .6))
				ax.add_patch(circle)

				# reset group's variables
				swarm[particle['group_num'] * step : particle['group_num'] * step + step]['blob_num'] = -1
				swarm[particle['group_num'] * step : particle['group_num'] * step + step]['state'] = 0
				swarm[particle['group_num'] * step : particle['group_num'] * step + step]['reflection_position'] = (-1, -1)
		
		# Check that state is searching for blob
		if (particle['state'] == 0):

			if (particle['blob_num'] < 0):
				# No blob found for group

				def particle_in_other_blob_radius(x, y):
					for blob_idx,blob in enumerate(blobs):
						blob_x = blob['position'][0]
						blob_y = blob['position'][1]
						blob_r2 = blob['max_r2_found']

						d2 = (x - blob_x)**2 + (y - blob_y)**2
						r2 = d2 / 4

						#print "particle_in_other_blob_radius: P(%d,%d),  B%d(%d,%d), blob_r2=%.4f, r2=%.2f" % \
						#	(x, y, blob_idx, blob_x, blob_y, blob_r2, r2)

						if (r2 <= blob_r2):   # true if distance^2 < r^2 of blob
							return True
					return False

				# Check if particle is in another's radius
				if (particle_in_other_blob_radius(x, y) or not is_in_color(position_color)):
					# particle is in another blob's radius or is not in color

					#print "X(%d, %d), V(%d, %d) : not in color" % (x,y,vx,vy)
					
					particle['in_color_count'] = 0   # reset counter

					# Randomly mutate velocity, ensure both not 0
					while(True):
						vx = vx if (np.random.rand() > 0.02) else get_rand_velocity(1, 1) 
						vy = vy if (np.random.rand() > 0.02) else get_rand_velocity(1, 1)
						if (vx != 0 or vy != 0):   # loop while both == 0
							break
					x, y, vx, vy = update_x_with_v(x, y, vx, vy, particle)

				else:
					# particle is in color

					#print "X(%d, %d), V(%d, %d), RED, CC=%d : in red" % (x,y,vx,vy, particle['in_color_count'])

					# Check if travelled far enough into blob
					d = math.sqrt( (vx * particle['in_color_count'])**2 + (vy * particle['in_color_count'])**2 )  # distance travelled
					if (d >= min_blob_size):
						# First blob found for group
						#print 'assigning new blob num -', next_blob_num

						particle['state'] = 1
						
						blobs.resize(next_blob_num + 1, refcheck=False)   # add new blob to list
						swarm[particle['group_num'] * step : particle['group_num'] * step + step]['blob_num'] = next_blob_num
						blobs[next_blob_num]['position'] = (x, y)   # set approximate position of blob
						next_blob_num += 1

						#print "\tEntered in blob state"
					else:
						particle['in_color_count'] += 1    # increment counter
						x, y, vx, vy = update_x_with_v(x, y, vx, vy, particle)

			else:
				# Group is assigned a blob

				# if travelling and a blob is found for group, head towards it
				dx = blobs[particle['blob_num']]['position'][0] - x
				dy = blobs[particle['blob_num']]['position'][1] - y

				d = math.sqrt(dx**2 + dy**2)

				#print "HEADING TOWARDS BLOB"
				#print "\tx:%d, y:%d,   dx:%d, dy:%d,  d:%.4f " % (x, y, dx, dy, d)
				#print "\tblob_num:%d, blob_x:%d, blob_y:%d" % (particle['blob_num'],blobs[particle['blob_num']]['position'][0],blobs[particle['blob_num']]['position'][1])

				if (d <= min_blob_size and is_in_color(position_color)):
					# particle is within blob
					particle['state'] = 1
					#print "\tSetting state to 1: %.4f <= %.4f" % (d , min_blob_size) 
				else:
					# particle still travelling towards blob
					if (d != 0):   # TODO: not sure if this fixes the d==0 issue
						vx = dx / d * (velocity_range / 2)
						vy = dy / d * (velocity_range / 2)

					x, y, vx, vy = update_x_with_v(x, y, vx, vy, particle)

		# Check that state is searching blob
		if (particle['state'] == 1):
			#print "X(%d, %d), V(%d, %d), %s : State == 1" % (x,y,vx,vy,"RED" if is_in_color(position_color) else "",)

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

				safety = 40
				while (True):   # loop to ensure both components != 0
					safety -= 1
					if (safety == 0):
						print "NEXT VELOCITY LOOP BROKEN"*5
						break

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

				safety = 40
				while (True):   # loop to find nearest position that's in color
					safety -= 1
					if (safety == 0):
						print "NEAREST IN COLOR X LOOP BROKEN"*5
						break
					#print ("\tnearest in color : (%d, %d) : %s" % (vx, vy, is_in_color(tuple(img[y + vy][x + vx]))))
					if (vx != 0):
						vx += -1 if vx > 0 else 1
					if (is_in_color(tuple(img[y + vy][x + vx]))):
						break
					#print ("\tnearest in color : (%d, %d) : %s" % (vx, vy, is_in_color(tuple(img[y + vy][x + vx]))))
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
				r2 = c2 / 4        #   this code is attemptingt to avoid square roots
				approx_blob_area = calculate_A_circle_r2(r2)

				#print "\tflipped V, setting x=%d,y=%d, COUNT=%d, A=%.2f" % \
				#		(x,y, particle['in_color_count'], approx_blob_area)

				particle['in_color_count'] = 0   # reset counter

				blob_num = particle['blob_num']    # get particle's blob num
				blobs[blob_num]['num_reflections'] += 1   # increment reflections in blob
				if (r2 > blobs[blob_num]['max_r2_found']):   # set max squared radius if found is greater
					#print '\tsetting max area of blob,'
					blobs[blob_num]['max_r2_found'] = r2
					if (particle['reflection_position'][0] > 0 and particle['reflection_position'][1] > 0):   # ensure position is valid
						#print '\tsetting position of blob P(x:%d, y:%d), Bold(%d, %d), Bnew(%d, %d)' % \
						(x,y,particle['reflection_position'][0], particle['reflection_position'][0], abs(x + particle['reflection_position'][0]) / 2, particle['reflection_position'][1] / 2)
						blobs[blob_num]['position'][0] = abs(x + particle['reflection_position'][0]) / 2   # Set blob position as midpoint of particle path
						blobs[blob_num]['position'][1] = abs(y + particle['reflection_position'][1]) / 2

				particle['reflection_position'][0] = x   # set reflection position
				particle['reflection_position'][1] = y

			else:
				# particle traversing blob

				#print "\tnormal update"
				particle['in_color_count'] += 1    # increment counter
				x, y, vx, vy = update_x_with_v(x, y, vx, vy, particle)

		# set particle data
		try:
			particle['position'][0] = x
			particle['position'][1] = y
			particle['velocity'][0] = vx
			particle['velocity'][1] = vy
			particle['color'] = position_color
			markers[p_idx] = (3, 0, math.degrees(math.atan2(vy, vx))-90)
		except Exception as e:
			print e
			pass

	set_markers()   # update rotation of plot markers

    # Update the scatter collection
	if (use_position_colors):
		scatter_plot.set_facecolor(swarm['color'] / 255.0)
	scatter_plot.set_offsets(swarm['position'])
	
	global run_anim
	if (frame_number == max_num_frames):
		run_anim = False
		print_data()
		animation.event_source.stop()

# Mouse click event
last_click_position = (0, 0)
def onclick(event):
	global last_click_position

	try:
		# Print image data at click location
		if (event.ydata is not None and event.xdata is not None):
			x = int(round(event.xdata))
			y = int(round(event.ydata))
			color = tuple(img[y][x])
			print "click at P(%d, %d) : C%s : %s.   r2 from P(%d, %d) = %.4f" \
				% (x,y, color, "IN_COLOR" if is_in_color(color) else "NOT_IN_COLOR", \
					last_click_position[0], last_click_position[1],	((x-last_click_position[0])**2+(y-last_click_position[1])**2))
			
			last_click_position = (x, y)
	except Exception as e:
		print e
		pass

# Keyboard click event
def onpress(event):
	global run_anim
	global interval, min_interval, max_interval
	global swarm
	global blobs
	global global_frame_number
	
	# Start/Stop animation on any key press
	if (show_anim):
		if (event.key == "x"):

			if (run_anim):
				run_anim = False
				animation.event_source.stop()

				print_data()
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
interval = 1
min_interval = 200
max_interval = 500
iterations = 180
click_cid = fig.canvas.mpl_connect('button_press_event', onclick)
btn_cid = fig.canvas.mpl_connect('key_press_event', onpress)

plt.grid(True)   # Show grid on axes

if (show_anim):
	animation = FuncAnimation(fig, update, interval=interval)#, frames=iterations)
else:
	start_time = time.time()

	for frame_number in range(max_num_frames):
		update(frame_number)
	print_data()

	stop_time = time.time()

	print "Runtime for %d frames: %.2fs" % (max_num_frames, stop_time - start_time)

plt.show()   # Show plot
#animation.save("id.mp4", fps=20)


