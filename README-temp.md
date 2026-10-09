<!--
RTSOS — Radiative Transfer model based on Successive Orders of Scattering
Copyright © 2025 Pengwang Zhai.

Licensed under the Creative Commons Attribution–NonCommercial 4.0
International License (CC BY-NC 4.0).
You may use, modify, and share this code for research and
educational purposes with proper attribution.
Commercial use requires written permission from the author.

Full license: https://creativecommons.org/licenses/by-nc/4.0/
Contact: Pengwang Zhai  |  [pwzhai@gmail.com]
-->

# Radiative Transfer model based on Successive Orders of Scattering (RTSOS)

RTSOS can solve the multiple scattering radiative transfer equation from UV, visible, to infrared. It can handle atmosphere-land or atmosphere-ocean coupled systems. The atmosphere can be a mixture of molecules, aerosols, and cloud droplets. The land bottom can be Lambertian, snow surface, Ross-Li, and a number of other surfaces. The ocean waters are modeled by a mixture of pure ocean water, phytoplankton, and colored dissolved organic matter (CDOM), and other hydrosols. The sensors can be placed at arbitrary levels in the Earth system. The output of the sensor can include the full polarized Stokes parameters (I, Q, U, V). For more information, see References at the end of this document.

PACE simulator is a wrapper built around the monochromatic RTSOS, which has a list of built-in aerosol and ocean inherent optical properties. A publication on the PACE simulator is published on Frontiers in Remote Sensing (Zhai et al., 2022). 

GSFC AC LUT is a wrapper built around the monochromatic RTSOS which
builds look up tables for atmospheric correction for retrievals of surface reflectance from top-of-atmosphere measurements.
