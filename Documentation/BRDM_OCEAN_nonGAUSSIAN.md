# Facet slopes and wind coordinates in BRDM_OCEAN_nonGAUSSIAN

This note explains the facet-slope and wind-coordinate calculations in
[rtsos_rao_dg.f90](rtsos_rao_dg.f90).

The calculation has two steps:

1. Find the surface-facet slopes required to reflect the incoming ray into the outgoing ray.
2. Express those slopes in the crosswind and upwind coordinates used by Cox–Munk Eq. (18).

## 1. Incoming and outgoing propagation directions

The incoming and outgoing photon propagation unit vectors are

$$
\mathbf{k}_{\mathrm{in}}=
\begin{pmatrix}
SA\\
SB\\
COST1
\end{pmatrix},
\qquad
\mathbf{k}_{\mathrm{out}}=
\begin{pmatrix}
FA\\
FB\\
COST2
\end{pmatrix}.
$$

Their horizontal components are computed from their zenith and azimuth angles:

$$
SA=\sin\theta_1\cos\phi_1,\qquad
SB=\sin\theta_1\sin\phi_1,
$$

$$
FA=\sin\theta_2\cos\phi_2,\qquad
FB=\sin\theta_2\sin\phi_2.
$$

Here, the vectors describe the directions in which photons travel.
For reflection from air onto the water surface, the incoming vertical component
is negative and the outgoing vertical component is positive.

## 2. Recover the required facet slopes

For a unit facet normal $\hat{\mathbf n}$, the reflection law is

$$
\mathbf{k}_{\mathrm{out}}
=\mathbf{k}_{\mathrm{in}}
-2\left(\mathbf{k}_{\mathrm{in}}\cdot\hat{\mathbf n}\right)
\hat{\mathbf n}.
$$

Consequently, the reflecting facet normal is parallel to the difference between
the outgoing and incoming propagation vectors:

$$
\mathbf n\parallel
\mathbf{k}_{\mathrm{out}}-\mathbf{k}_{\mathrm{in}}
=
\begin{pmatrix}
FA-SA\\
FB-SB\\
COST2-COST1
\end{pmatrix}.
$$

Describe the local surface by its height $z=h(x,y)$, with positive z pointing
upward. Define the height gradients

$$
h_x=\frac{\partial h}{\partial x},
\qquad
h_y=\frac{\partial h}{\partial y}.
$$

An upward normal is proportional to

$$
\mathbf n\parallel
\begin{pmatrix}
-h_x\\
-h_y\\
1
\end{pmatrix}.
$$

Therefore,

$$
h_x=-\frac{n_x}{n_z}
=-\frac{FA-SA}{COST2-COST1}
=\frac{SA-FA}{COST2-COST1},
$$

$$
h_y=-\frac{n_y}{n_z}
=-\frac{FB-SB}{COST2-COST1}
=\frac{SB-FB}{COST2-COST1}.
$$

These are the quantities computed by:

~~~fortran
SLOPE_X=(SA-FA)/(COST2-COST1)
SLOPE_Y=(SB-FB)/(COST2-COST1)
~~~

**SLOPE_X and SLOPE_Y are height gradients, not horizontal components of the
facet normal.** That distinction explains the minus signs in the derivation.
Normalizing the facet normal is unnecessary because its magnitude cancels in
the component ratios.

## 3. Define the crosswind and upwind axes

The normalized horizontal wind vector is

$$
\hat{\mathbf w}
=
\begin{pmatrix}
w_x\\
w_y
\end{pmatrix}
=
\begin{pmatrix}
WX\_UNIT\\
WY\_UNIT
\end{pmatrix}.
$$

It points **toward where the wind blows**, so it is a downwind unit vector.

Define a crosswind unit vector by rotating the downwind vector counterclockwise
by $90^\circ$ when viewed from above:

$$
\hat{\mathbf e}_c=
\begin{pmatrix}
-w_y\\
w_x
\end{pmatrix}.
$$

The upwind unit vector points opposite to the wind:

$$
\hat{\mathbf e}_u=
\begin{pmatrix}
-w_x\\
-w_y
\end{pmatrix}.
$$

Both vectors have unit length, and they are perpendicular.

## 4. Project and standardize the slopes

Let the horizontal slope vector be

$$
\mathbf s=
\begin{pmatrix}
h_x\\
h_y
\end{pmatrix}
=
\begin{pmatrix}
SLOPE\_X\\
SLOPE\_Y
\end{pmatrix}.
$$

Its crosswind and upwind components are

$$
s_c=\mathbf s\cdot\hat{\mathbf e}_c=-w_yh_x+w_xh_y,
$$

$$
s_u=\mathbf s\cdot\hat{\mathbf e}_u=-w_xh_x-w_yh_y.
$$

Cox–Munk Eq. (18) uses standardized slope components:

$$
\xi=\frac{s_c}{\sigma_c}
=\frac{-w_yh_x+w_xh_y}{\sigma_c},
$$

$$
\eta=\frac{s_u}{\sigma_u}
=-\frac{w_xh_x+w_yh_y}{\sigma_u}.
$$

The code stores the slope variances as

$$
SIGMACSQ=\sigma_c^2,\qquad SIGMAUSQ=\sigma_u^2.
$$

Taking their square roots supplies the corresponding rms slopes:

~~~fortran
XI=(-WY_UNIT*SLOPE_X+WX_UNIT*SLOPE_Y)/SQRT(SIGMACSQ)
ETA=-(WX_UNIT*SLOPE_X+WY_UNIT*SLOPE_Y)/SQRT(SIGMAUSQ)
~~~

Thus XI and ETA measure the slopes in units of their respective rms values.
The minus sign in ETA converts the input's downwind direction into the paper's
positive upwind direction.

## 5. Example: wind blowing toward azimuth zero

For wind blowing toward the positive x-axis,

$$
w_x=1,\qquad w_y=0.
$$

The crosswind axis points along positive y, and the upwind axis points along
negative x. The formulas reduce to

$$
\xi=\frac{h_y}{\sigma_c},
\qquad
\eta=-\frac{h_x}{\sigma_u}.
$$

A surface rising toward positive x rises **downwind**, giving negative $\eta$.
A surface rising toward negative x rises **upwind**, giving positive $\eta$.
This sign convention matters because the skewness terms in Eq. (18) distinguish
positive and negative upwind slopes.
