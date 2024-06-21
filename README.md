
[[English](https://github.com/MathieuChailloux/MitiConnect/blob/main/README.md) | [Français](https://github.com/MathieuChailloux/MitiConnect/blob/main/docs/fr/README_fr.md)]

# Overview

*MitiConnect* is a QGIS 3 plugin to assess ecological connectivity in mitigation herarchy.

*MitiConnect* uses resistance surfaces and landscape graphs to assess ecological connectivity at a given state. It provides an all-in-one tool with a dedicated GUI allowing user to define target species, resistance values, mitigation scenarios, ect., and then calls QGIS or Graphab functionalities to compute each step.

![Compare](/docs/pictures/metricsCmp+Graph.png)

*MitiConnect* has been designed as a 6-steps plugin from raw data preprocessing to landscape graphs comparison.
Parameters settings can be saved to and loaded from a configuration file.

*MitiConnect* steps are:
 1. Parameters setting
 2. Data import
 3. Species definition
 4. Resistance values definition
 5. Mitigation scenarios definition
 6. Launches manager
    1. Land use layer
    2. Resitance surfaces
    3. Graphab project
	4. Link set
	5. Landscape graph
	6. Dispersal areas
	7. Prioritization (local metrics)
	8. Mitigation scenarios comparison (global metrics)
    
Each step is detailed in plugin help panel.

![Compare](/docs/pictures/stepsGIF.gif)

*MitiConnect* has been developped by [*INRAE*](http://www.inrae.fr), 
on mission for the [*French ecological network resource center*](http://www.trameverteetbleue.fr/) 
(driven by [*French ministry of ecology*](hhttps://www.ecologie.gouv.fr/)).

# Contact

*Development* : Mathieu Chailloux (mathieu@chailloux.org)

*Design* : Simon Tarabon (s.tarabon@ubiquiste.fr)

*Coordination* : Jennifer Amsallem (jennifer.amsallem@inrae.fr)

# Quotation

> Chailloux M., Tarabon S., Papet G., Amsallem J. & Vanpeene S (2024). MitiConnect : a QGIS plugin to assess ecological connectivity in mitigation hierarchy

# Installation

*MitiConnect* requires QGIS 3.16 (or superior version).

Go to plugins menu, *Install/manage plugins*, type *MitiConnect* and click on *Install* button. MitiConnect icon should appear. Otherwise, it is available in plugins menu.

# Documentation

Available documentation:
 - [Video tutorials](https://www.youtube.com/watch?v=uhbXupWRqGk) (English subtitles) 
 - [Method guide](https://github.com/MathieuChailloux/MitiConnect/blob/main/docs/en/MitiConnect_MethodGuide.pdf)
 - [MitiConnect user guide](https://github.com/MathieuChailloux/MitiConnect/blob/main/docs/en/MitiConnect_UserGuide.pdf)
 
    
# Links
 - [MitiConnect git repository](https://github.com/MathieuChailloux/MitiConnect)
 - [INRAE](http://www.inrae.fr)
 - [French ecological network resource center](http://www.trameverteetbleue.fr/)
 - [French ministry of ecology](https://www.ecologie.gouv.fr/)

