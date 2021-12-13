import matplotlib.pyplot as plt
import numpy as np

total_pulses = 30

x = np.linspace(0, total_pulses, 1000)
fig, ax = plt.subplots()

begin = 0
end = 50
ax.plot(x, x * (end - begin)/total_pulses + begin)

ax.plot(x, -(x-15)**2 * 5/total_pulses + 15**2 * 5/total_pulses)

plt.show()
