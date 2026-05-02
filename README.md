# Projet : Serveur Memoire, Projet de système d’exploitation - L2 Université de Nice

**Auteur :** Gaetan Rogeron
**Numero etudiant :** 22314014

## 1. Auto-evaluation du projet

Le projet a ete mene a terme. Le code a ete structuree pour garantir la securite des executions (gestion des erreurs, fermeture propre des processus et des sockets). 

Etapes reussies : Etapes 1 a 7 incluses.

*   **Etape 1 & 2 : Backend et Signaux**
    *   Allocation de la memoire.
    *   Verification des limites (IndexError, depassement de capacite).
    *   Implementation de SIGALRM pour le log periodique et interception propre de SIGINT (Ctrl+C).
*   **Etape 3 : Frontend et Allocation**
    *   Implementation fonctionnelle de l'algorithme d'allocation continue First-Fit.
    *   Traductions vers le Backend via stdout, logs et erreurs vers stderr.
*   **Etape 4 : Composition de processus (Pipes & Forks)**
    *   Architecture multi-processus (os.fork) respectant le schema attendu.
    *   Communication inter-processus via 3 descripteurs de tubes (pipes) avec redirection standard (os.dup2).
    *   Fermeture des descripteurs inutilises pour prevenir les fuites de ressources (BrokenPipeError).
*   **Etape 5 : Serveur Reseau (Sockets TCP)**
    *   Mise en place d'un serveur TCP iteratif.
    *   Gestion de l'option SO_REUSEADDR et nettoyage systeme (envoi SIGTERM aux processus enfants) lors de l'arret du serveur.
*   **Etape 6 : Librairie Client (RemoteMemory)**
    *   Utilisation de la classe client et creation d'un script de test.
    *   Adaptation du serveur principal (server_mem.py) pour assurer la compatibilite avec ce code client (traitement des separateurs de fin de ligne dans les requetes entrantes).
*   **Etape 7 : Cache Local et Algorithme LRU**
    *   Mise en place de la pagination pour reduire la charge reseau.
    *   Implementation du LRU avec gestion du bit de modification (dirty bit).
    *   Impact du parametre sigma.

Etapes partiellement reussies ou non traitees :
*   Les extensions "pour les motives" n'ont pas ete faites. Le developpement s'est arrete a la fin de l'Etape 7 comme prevu.

## 2. Estimation de la note

**Note estimee : 19/20**

**Justification :** 
L'integralite des fonctionnalites requises jusqu'a l'Etape 7 a ete implementee et testee. De plus, suite a l'entretien du TP 3 avec le professeur, le code a ete entierement revise pour securiser au maximum l'architecture et gerer les cas d'usage limites :
*   Validation du format et du nombre des arguments.
*   Protection contre les debordements de memoire avec prise en compte de la taille des pages.
*   Gestion des deconnexions reseau imprevues.
*   Structure du code systeme maintenable (points d'entree if __name__ == "__main__":, flush des tubes, gestion des signaux).
