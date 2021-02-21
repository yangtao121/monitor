import numpy as np
import quaternion

a = np.quaternion(0, 0, 0, 1)
print(quaternion.as_euler_angles(a))
