# Line 


### Scan to AzEl creates a 180deg cutoff of az (0:180) 
x_values, _ = scan_to_az_el(theta, np.full_like(theta, phi))

# sets 0:360, should always be -180:180
ax.set_xlim((-180, 180)) #if self.plot_phi_theta.isChecked() else (0, 360))
