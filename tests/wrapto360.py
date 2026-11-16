import numpy as np

# a = np.array(np.arange(-180,181,1))
a = np.linspace(0,360,361)
# a = np.linspace(-180,180,361)
# print(a[:10])
# print(np.size(a))

def wrap360(a):
    values = np.mod(np.asarray(a, dtype=float), 360.0)
    # print(values[:180])
    # print(np.size(values))
    return values

t = wrap360(180.0 - np.asarray(a, dtype=float))
# print(f'178 to 182: {t[178:182]}')
# print(f'Last 10: {t[:-1]}')
print(t)
print(np.size(t))