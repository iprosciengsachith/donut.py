import os
import time
import numpy as np

# Parameters for the animation
screen_size = 40
theta_spacing = 0.07
phi_spacing = 0.02
illumination = np.fromiter(".,-~:;=!*#$@", dtype="<U1")  # Characters used for shading
clear_frame = True  # Whether to clear the frame before printing a new one
sleep_time = 0.1  # Time interval between frames

# Constants for the donut shape
A = 1
B = 1
R1 = 1
R2 = 2
K2 = 5
K1 = screen_size * K2 * 3 / (8 * (R1 + R2))


def render_frame(A: float, B: float) -> np.ndarray:
    """
    Returns a frame of the spinning 3D donut.
    Based on the pseudocode from: https://www.a1k0n.net/2011/07/20/donut-math.html
    """
    # Precompute trigonometric functions for efficiency
    cos_A = np.cos(A)
    sin_A = np.sin(A)
    cos_B = np.cos(B)
    sin_B = np.sin(B)

    # Initialize arrays for output and z-buffer
    output = np.full((screen_size, screen_size), " ")  # Frame buffer
    zbuffer = np.zeros((screen_size, screen_size))  # Depth buffer

    # Generate donut shape points
    cos_phi = np.cos(phi := np.arange(0, 2 * np.pi, phi_spacing))
    sin_phi = np.sin(phi)
    cos_theta = np.cos(theta := np.arange(0, 2 * np.pi, theta_spacing))
    sin_theta = np.sin(theta)
    circle_x = R2 + R1 * cos_theta
    circle_y = R1 * sin_theta

    # Compute 3D coordinates of each point on the donut
    x = (np.outer(cos_B * cos_phi + sin_A * sin_B * sin_phi, circle_x) - circle_y * cos_A * sin_B).T
    y = (np.outer(sin_B * cos_phi - sin_A * cos_B * sin_phi, circle_x) + circle_y * cos_A * cos_B).T
    z = ((K2 + cos_A * np.outer(sin_phi, circle_x)) + circle_y * sin_A).T
    ooz = np.reciprocal(z)  # Calculates 1/z
    xp = (screen_size / 2 + K1 * ooz * x).astype(int)
    yp = (screen_size / 2 - K1 * ooz * y).astype(int)

    # Compute shading
    L1 = (((np.outer(cos_phi, cos_theta) * sin_B) - cos_A * np.outer(sin_phi, cos_theta)) - sin_A * sin_theta)
    L2 = cos_B * (cos_A * sin_theta - np.outer(sin_phi, cos_theta * sin_A))
    L = np.around(((L1 + L2) * 8)).astype(int).T
    mask_L = L >= 0
    chars = illumination[L]

    # Update frame buffer with shading
    for i in range(90):
        mask = mask_L[i] & (ooz[i] > zbuffer[xp[i], yp[i]])
        zbuffer[xp[i], yp[i]] = np.where(mask, ooz[i], zbuffer[xp[i], yp[i]])
        output[xp[i], yp[i]] = np.where(mask, chars[i], output[xp[i], yp[i]])

    # Clear frame before printing new one if specified
    if clear_frame:
        os.system('cls')
    return output


def pprint(array: np.ndarray) -> None:
    """Pretty print the frame."""
    print(*[" ".join(row) for row in array], sep="\n")


if __name__ == "__main__":
    # Main loop for rendering the animation
    for _ in range(screen_size * screen_size):
        A += theta_spacing
        B += phi_spacing
        print("\x1b[H")  # Move cursor to home position
        pprint(render_frame(A, B))
        time.sleep(sleep_time)
