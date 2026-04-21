import sys, signal

memoire = None #declaration de la memoire pour quelle soit globale

def sauvegarde_periodique(signum, frame):
    global memoire
    print(list(memoire), file=sys.stderr) # print vers la sortie 2 erreur et liste pour que ca affiche bien

    signal.alarm(1) # continuer la boucle toutes les secondes


if __name__ == "__main__":
   
    # verification des arguments
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: python server_mem_backend.py memsize (--periodic-log)")
        sys.exit(1)

    # initialisation memoire
    taille_memoire = int(sys.argv[1]) # conversion string -> int
    memoire = bytearray([32] * taille_memoire)

    # intitialisation sauvegarde periodique
    if "--periodic-log" in sys.argv :
        signal.signal(signal.SIGALRM, sauvegarde_periodique)
        signal.alarm(1)

    # boucle de lecture
    for ligne in sys.stdin : # lit ligne par ligne jusqu'a un Ctrl + D

        mots = ligne.split() # sans argument coupe au espace et enleve les \n
        if not mots:
            continue

        if mots[0] == "GET":
            # verification arguments
            if len(mots) != 2:
                print("usage : GET index")
                continue

            indice = int(mots[1])
            
            # verification indice valide
            if indice >= taille_memoire or indice < 0 :
                print(f"error: index {indice} out of bounds")
                continue

            print(memoire[indice])


        elif mots[0] == "POST" :
            #verification arguments
            if len(mots) != 3:
                print("usage : POST index valeur")
                continue

            indice = int(mots[1])
            valeur = int(mots[2])

            # verification indice valide
            if indice >= taille_memoire or indice < 0 :
                print(f"error: index {indice} out of bounds")
                continue

            #verification 2eme argument
            if valeur > 255 or valeur < 0:
                print(f'error: POST instruction requires a byte as a second argument “{valeur}” out of byte range (0-255)')
                continue

            memoire[indice] = valeur
            print('ok')
    
    print("bye")