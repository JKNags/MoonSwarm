import matplotlib.image as mpimg 
import matplotlib.pyplot as plt 
import numpy as np
import math

# Read Image
img = mpimg.imread('grail_gravity_map_moon.jpg') 
  
#print(img)
#print("Data type of img > ", type(img))
#print("Shape of img > ", img.shape)
#print("Dimention of img > ",img.ndim)

img_x = img.shape[1]   # get x size
img_y = img.shape[0]   # get y size
plt.xlim(0,img_x)   # set x limits of plot
plt.ylim(0,img_y)   # set y limits of plot

print ("X=", img.shape[1])
print ("Y=", img.shape[0])

# Output Images 
plt.imshow(img)   # show gravity map on plot

# Create Swarm
swarm_size = 25
swarm = np.zeros(swarm_size, dtype=[('position',  float, 2),   # Position (x,y)
                                    ('velocity',  float, 2),   # Velocity (dx,dy)
                                    ('color',     float, 4)])  # Color (r,g,b,a)
scale = 8
particle_size = 25 * scale  # Set particle size
radius = particle_size * 0.08
arrow_width = particle_size * 0.05
arrow_head_width = particle_size * 0.12
arrow_head_length = particle_size * 0.12
edge_color = (0, 0, 0, 1)   # Set global outline color
swarm['position'][:, 0] = np.random.randint(0, img_x, swarm_size)   # Set random Y position in px
swarm['position'][:, 1] = np.random.randint(0, img_y, swarm_size)   # Set random X position in px
swarm['velocity'] = np.random.choice([-5,-4,-3,-2,-1,1,2,4,5], (swarm_size, 2))   # Set velocity components in px
swarm['color'] = (1, 0.0784, 0.576, 1)   # Set initial RGBA color to pink, can change on location?

#print swarm

# Create initial scatter plot
plt.scatter(swarm['position'][:, 0], swarm['position'][:, 1],
            c=swarm['color'], s=particle_size, lw=0.5, 
            edgecolors=edge_color, facecolors='none')  

# Create arrows for scatter plot
ax = plt.axes()
for particle in swarm:
	x = particle['position'][0]   # position x coordinate
	y = particle['position'][1]   # position y coordinate
	vx = particle['velocity'][0]   # velocity x component
	vy = particle['velocity'][1]   # velocity y component
	rad = math.atan2(vy, vx)   # rotation in rad of velocity
	arrow_x = math.cos(rad) * radius   # base of velocity arrow x
	arrow_y = math.sin(rad) * radius   # base of belocity arrow y
	arrow_dx = arrow_x * abs(vx) * 0.3   # tip of velocity arrow x
	arrow_dy = arrow_y * abs(vy) * 0.3   # tip of velocity arrow y
	ax.arrow(x + arrow_x, y + arrow_y, 
			arrow_dx, arrow_dy,
			fc=particle['color'], ec=edge_color, width=arrow_width,
			head_width=arrow_head_width, head_length=arrow_head_length)

plt.grid(True)   # Show grid on axes
plt.show()   # Show plot
