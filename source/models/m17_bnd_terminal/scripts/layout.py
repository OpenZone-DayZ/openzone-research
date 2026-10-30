"""M17 - shared sizes of the exchange window and the place of the teller: read by the window generator
(build_m17.py) and by the trader figure generator.

Blender axes of the window: X is width, Y is depth (face, the customer side, toward -Y), Z is up, the
floor is 0. The figure is built in its own axes: the origin is the FIG proxy point (on the podium under
the seat), the face toward -Y like the window's; a proxy with an identity rotation puts it as is
(kexport.proxy_points).

Sizes:
- the teller's tray LK-1 is 500 x 300 x 175 mm, here a tray well 500 x 300, depth 90;
- the teller desk is 500-600 mm deep (bank cash-booth requirements), here 0.45: with a deeper desk a
  full-figured teller (her belly presses against the desk edge) cannot reach the tray;
- glazing up to ~2.0 m from the floor (bank cash booths), the window ~0.30 x 0.25;
- the counter is ~1.0 m; the teller sits on a 0.30 podium - the desk is 0.70 above her floor (the teller
  is short, ~1.58 m: the seat is 0.39 by her pose, the desk 0.31 higher - as with an ordinary desk and
  chair).
"""
# window box
X0, X1 = -0.90, 0.90
Y0, Y1 = -0.70, 0.70
H = 2.10                       # top of the canopy
YP = -0.40                     # partition plane (the frame face on the teller side)
ZC = 1.00                      # customer counter and teller desk
ZG = 2.00                      # top of the glazing
LEDGE = (-0.68, YP - 0.02)     # customer shelf along Y
PODIUM_Z = 0.30                # teller podium (the desk is 0.70 above her floor: she is short)
DESK_Y = (YP, YP + 0.45)       # teller desk along Y (0.45: a full-figured teller's belly touches the edge)
# tray LK-1: a well in the desk under the window, half on the customer side, half on the teller side
TRAY = (-0.25, 0.25, YP - 0.20, YP + 0.10, 0.09)    # x0 x1 y0 y1 depth
WIN_W, WIN_H = 0.30, 0.25      # semicircular window over the tray

# figure: the proxy point (on the podium), the chair seat - the height above the podium by the figure pose
FIG = (-0.14, 0.30, PODIUM_Z)
SEAT_Z = 0.39                  # seat top above the podium (by the pose: bottom of the buttocks, make_human prints it)


def to_fig(x, y, z):
    """Window point -> figure axes."""
    return (x - FIG[0], y - FIG[1], z - FIG[2])


# where the figure puts its hands (window axes): the left on the inner edge of the tray, the right holds banknotes
HAND_L = (0.03, YP + 0.30, ZC + 0.03)
HAND_R = (-0.30, YP + 0.38, ZC + 0.10)
# where it looks: the customer's face behind the window
LOOK = (0.05, -0.95, 1.62)
