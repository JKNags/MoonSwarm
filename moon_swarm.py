import matplotlib.image as mpimg 
import matplotlib.pyplot as plt 
import numpy as np

# Read Image
img = mpimg.imread('grail_gravity_map_moon.jpg') 
  
#print(img)
#print("Data type of img > ", type(img))
#print("Shape of img > ", img.shape)
#print("Dimention of img > ",img.ndim)
img_x = img.shape[1]
img_y = img.shape[0]
print ("X=", img.shape[1])
print ("Y=", img.shape[0])

# Output Images 
plt.imshow(img, alpha=0.5)
plt.xlim(0,img_x)
plt.ylim(0,img_y)

swarm_size = 50
swarm = np.zeros(swarm_size, dtype=[('position', float, 2),
                                    ('velocity', float, 2),
                                    ('size',     float, 1),
                                    ('color',    float, 4)])

swarm['position'] = np.random.uniform(0, img_x, (swarm_size, 2))
swarm['size'] = 10
swarm['color'] = (0, 0, 0, 1)

print(swarm)

plt.scatter(swarm['position'][:, 0], swarm['position'][:, 1],
                  c=swarm['color'], s=swarm['size'], lw=0.5, edgecolors=swarm['color'],
                  facecolors='none')

#plt.legend()
plt.grid(True)

print swarm['position'][:, 0]

plt.show()
