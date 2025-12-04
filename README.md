# Black Hole Simulation

This project is a real‑time 2D visualization of a spinning stellar‑mass black hole with an accretion disk, relativistic jets, gravitational lensing, Hawking‑like particle effects, and tidal disruption events. It is implemented in Python using Pygame.

## Features

- Gravitational lensing of background stars around the black hole shadow
- Accretion disk with approximate temperature profile and Doppler beaming
- Event horizon, photon sphere, and ISCO visualized at different radii
- Relativistic jets with simple Doppler boosting model
- Hawking‑like particle flicker just outside the horizon
- Tidal disruption of infalling bodies (“spaghettification”) into fragments
- Optional labels and in‑scene help overlay
- Simple camera panning with arrow keys

## Requirements

- Python 3.8+
- [Pygame](https://www.pygame.org/news)

Install dependencies with:

```bash
pip install pygame
```

## Running the simulation

From the directory containing `blackhole.py`, run:

```bash
python blackhole.py
```

A 900×900 window will open with the black hole in the center.

## Controls

- `L` – Toggle labels (Event Horizon, Photon Sphere, ISCO)
- `H` – Toggle help overlay
- Arrow keys – Pan the camera (move the center of the scene)
- `Esc` / window close – Quit

## Code structure

- **Global constants** – Physical constants and scale factors (G, c, solar mass, black‑hole mass, Schwarzschild radius, etc.).
- **Initialization** – Star field, accretion‑disk particles, jets, photon ring, Hawking‑like particles, and tidal bodies.
- **Rendering functions**
  - `draw_lensed_background()` – Gravitationally lenses background stars around the black hole.
  - `draw_accretion_disk_doppler()` – Draws a Doppler‑boosted accretion disk with an approximate temperature profile.
  - `draw_blackhole_core()` – Renders the event horizon, glow, photon sphere, Hawking‑like particles, and lensing rings.
  - `draw_relativistic_jets()` – Renders top/bottom jets with Doppler boosting.
  - `draw_tidal_bodies()` / `draw_tidal_fragments()` – Simulates and renders tidal disruption of infalling bodies.
  - `draw_labels()` / `draw_help()` – Optional overlays for educational labeling and controls.
- **Update functions**
  - `update_tidal_bodies()` / `update_tidal_fragments()` – Advance orbital and radial motion, spawn and remove bodies.
  - `draw_particles()` – Advances and draws accretion‑disk tracer particles with simple viscosity.

The main loop handles user input, updates the scene, and renders each frame at ~60 FPS.

## Notes and limitations

- This is a **visual/educational** simulation, not a full GR ray‑tracer. Several effects (lensing, Doppler, redshift) are approximated for performance and clarity.
- Physical scales are heavily compressed into screen pixels; the constants are adapted to keep motion visually interesting.
- You are encouraged to tweak parameters (particle counts, radii, speeds, colors) to experiment with different visual styles.

## Contributing

If you extend the simulation (better GR modeling, UI overlays, more educational annotations, or performance tweaks), consider:

- Keeping functions small and focused
- Preserving 60 FPS performance where possible
- Making new effects togglable via keys

## License

This project is licensed under the MIT License. See [`LICENSE`](./LICENSE) for details.
