
[[English](https://github.com/MathieuChailloux/MitiConnect/blob/main/README.md) | [Français](https://github.com/MathieuChailloux/MitiConnect/blob/main/docs//README_fr.md)]

# Aperçu

*MitiConnect* est une extension QGIS qui permet d'évaluer les continuités écologiques lors de la séquence ERC (Eviter-Réduire-Compenser).

*MitiConnect* se base sur les coefficients de friction et les graphes paysagers pour évaluer la qualité du réseau écologique à un état donné. C'est un outil tout-en-un avec une interface graphique dédiée qui permet à l'utilisateur de définir les espèces cibles, les coefficients de friction, les scénarios de la séquence, etc., puis fait appel à QGIS et Graphab pour calculer le résultat de chaque étape.


![Compare](/docs/pictures/metricsCmp+Graph.png)

*MitiConnect* définit une procédure en 6 étapes depuis le prétraitement des données jusqu'à la comparaison des scenarios quant à leur impact sur l'état du réseau écologique.
Le paramétrage de l'outil peut être exporté et importé par le biais d'un fichier de configuration.

Les étapes de *MitiConnect* :
 1. Définition des paramètres généraux
 2. Import et uniformisation des données
 3. Définition des espèces cibles
 4. Définition des coefficients de friction
 5. Définition des scenarios
 6. Gestion des lancements
	1. Occupation du sol
	2. Couche de friction
	3. Projet Graphab
	4. Jeu de liens
	5. Graphe paysager
	6. Aires de dispersion
	6. Hiérarchisation des enjeux (métriques locales)
	7. Comparaison des scénarios (métriques globales)
    
Chaque étape est détaillée dans le panneau d'aide.

![Compare](/docs/pictures/stepsGIF.gif)

*MitiConnect* a été développé par l'[*INRAE*](http://www.inrae.fr), 
en mission pour le [*Centre de ressources Trame verte et bleue*](http://www.trameverteetbleue.fr/) 
(piloté par le [*Ministère de la Transition Écologique et Solidaire*](https://www.ecologie.gouv.fr/)).

# Contact

*Développement* : Mathieu Chailloux (mathieu@chailloux.org)

*Conception* : Simon Tarabon (s.tarabon@ubiquiste.fr)

*Coordination* : Jennifer Amsallem (jennifer.amsallem@inrae.fr)
    
# Citation

> Chailloux M., Tarabon S., Papet G., Amsallem J. & Vanpeene S (2024). MitiConnect : une extension QGIS pour intégrer les continuités écologiques dans la séquence Éviter, Réduire, Compenser (ERC)

# Installation

*MitiConnect* doit être lancé depuis QGIS 3.16 ou version supérieure avec la bilbiothèque GRASS.

Aller dans le menu *Installer/gérer les extensions*, taper *MitiConnect* dans la barre de recherche et appuyer sur *Installer*. L'icône de MitiConnect apparaît alors dans la barre d'outils.

# Documentation

Documentation disponible :
 - [Tutoriels vidéo](https://vimeo.com/922467098)
 - [Guide de mise en œuvre de la méthode](https://github.com/MathieuChailloux/MitiConnect/blob/main/docs/fr/GuideMethode_MitiConnect.pdf)
 - [Guide d'utilisation de MitiConnect](https://github.com/MathieuChailloux/MitiConnect/blob/main/docs/fr/MitiConnect_ManuelUtilisation.pdf)
 
    
# Liens
 - [Dépôt git](https://github.com/MathieuChailloux/MitiConnect)
 - [INRAE](http://www.inrae.fr)
 - [Centre de ressources Trame verte et bleue](http://www.trameverteetbleue.fr/)
 - [Ministère de la Transition Écologique et Solidaire](https://www.ecologie.gouv.fr/)

