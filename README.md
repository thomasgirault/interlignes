C'est la nuit. Des gens passent, se croisent, se rencontrent, s'arrêtent. Dans leur sillage, des mots surgissent. Peu à peu, c'est tout un texte qui se déploie sous leurs pieds et commence à danser avec eux. L'interligne habituel entre les phrases, bien sage et bien rangé, se met soudain à suivre les mouvements de leurs vies. Il bifurque, s'agrandit, dessine des boucles et tisse de nouveaux motifs.

Interlignes vous invite à venir lire en marchant, à moins ce que soit réécrire en dansant, un texte de Georges Perec, Tentative d'épuisement d'un lieu parisien, ainsi libéré de sa page et glissant joyeusement sur les pavés, guidé par le souffle des déplacements de vos corps.

# Dispositif technique
Concrètement, l’installation prend place dans un espace urbain délimité par une zone rectangulaire régie par un dispositif vidéo. 
En la traversant, les passants sont détectés par une caméra infrarouge placée en hauteur (7 à 10m) qui permettra de de cartographier en temps réel les déplacements des passants. 
Cette détection identifie chaque corps comme une zone d’apparition du texte dont l’orientation s’adapte dynamiquement aux trajectoires. 
Les textes parcourus seront alors projetés directement sur le sol où les spectateurs pourront voir les mots apparaître et disparaître sous leurs pas.


## Composants logiciels
## Version 1
- capation du signal vidéo (libfreenect2 adaptée pour capter un signal sur un rayon de 15m) ;
- nettoyage des images et detection des corps évoluant dans l'espace de captation (opencv) ;
- tracking prédictif avec filtres de Kalman + algo des k plus proches voisins (filterpy et scikit-learn) ;
- une application Web pour le rendu et mapping vidéo ;

### Version 2 (en cours de développement)
- utilisation d'un caméra de vidéosurveillance classique (améloration de la portée et de la qualité du signal) ;
- detection et tracking : algorithme de deep learning (YoloV3) ré-entraîné sur des images infrarouges pour améliorer la robustesse du module de detection/tracking (pluie, changement de température...) ;
- rendu du texte : librairie WebGL ;
- developpement d'une API pour enrichir dynamiquement le corpus (participation par SMS / réseau sociaux ?) ;

## Structure métalique
Pour le moment, nous utilisons vidéoprojecteur de 6000 lumens avec une Kinect2.
Nous avons fabriqué une structure métallique qui nous permet de placer le dispositif au zenith au dessus du public pour éviter les zones d'ombre. 
