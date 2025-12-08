# orbel

<i>**orbel** is a Python program designed to help understand orbital elements by visualising relative and absolute Keplerian orbits in both 3D and 2D.</i>  

---

It was originally created during my master's thesis work on astrometry, starting as a simple tool to explore orbital dynamics, and later evolved into a complete program for educational and research purposes. During my studies, I noticed that both I and many other students struggled to fully understand these elements in lectures and online resources, and found it difficult to visualise them in space. This motivated me to develop this program.


##  Features

- Visualisation of relative and absolute orbits  
- 3D orbit geometry and sky-plane projection views  
- Customisable orbital parameters via interactive sliders  
- Orientation aids with arcs and wedges make the orbit's orientation in space easier to understand  
- Bodies move according to Kepler's laws of planetary motion  
- Supports both educational use and research presentations  

---

##  Workflow

1. **Launch** the application with `python -m orbel`.  
2. **Select a view** (Relative / Absolute) using the tabs above the canvases.  
3. **Adjust orbital parameters** (`a`, `e`, `i`, `ω`, `Ω`, starting anomaly) and **masses** (`m1`, `m2`) using the sliders and spin boxes.  
4. **Toggle visual aids** (nodes, `Ω` and `ω` arcs, inclination wedge, sky plane, axis triad, centers, bodies) via the option checkboxes.  
5. **Start the animation** with the play button to see bodies move along their orbits according to Kepler’s laws.  
6. **Pause or reset** to inspect specific configurations or return to the default state.  

For a more detailed, step-by-step description with explanations of each visual element, see `docs/user_workflow.md`.


##  Screenshots

### Relative Orbit

- Shows the relative Keplerian orbit in 3D and on the sky plane, with nodes, `ω` arc and inclination wedge enabled.  
<img src="images/orbel2.png" width="600" height="800">

### Absolute Orbit

- Shows both components orbiting the barycenter, with a periapsis link and separate `Ω` arcs for each body.  
<img src="images/orbel3.png" width="600" height="800">

### Orbital Parameters and Controls

- Shows the parameter sliders, mass controls, option checkboxes and playback controls used to drive the canvases.  
<img src="images/orbel1.png" width="300" height="600">


##  Running the Program

1. Create an isolated Python environment (optional but recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

2. Install the pinned dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python -m orbel
   ```


## Tests

Automated tests are implemented with `pytest` and cover the orbital mechanics helpers, numerical models, Qt/Matplotlib canvases, and the main window / control flow wiring.

To run the test suite:

```bash
pytest
```


##  Project Layout

- `orbel_app/app.py` – creates the `QApplication` and wires the main window  
- `orbel_app/ui/` – higher-level widgets, panels, styles, and the refactored `MainWindow`  
- `orbel_app/plotting/` – Matplotlib canvases for the 3D and 2D orbit views  
- `orbel_app/core/orbit_math.py` – numerical helpers (rotations, Kepler solver, anomaly conversions)  
- `icons/`, `images/` – UI assets and screenshots used by the documentation  


## Contact

If you have ideas or suggestions for improving orbel, feel free to reach out:  
efurkanakar@gmail.com


## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

