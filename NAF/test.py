import numpy as np
import xarray as xr
import matplotlib

print('Numpy version: ', np.__version__)
print('Xarray version: ', xr.__version__)

x = np.linspace(-np.pi, np.pi, 19)
f = np.sin(x)

da_f = xr.DataArray(f, dims=['x'], coords={'x': x})
print(da_f)

da_f.plot(marker='o').show()

