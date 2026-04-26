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
            if len(mots) != 3:
                print("usage : GET index taille")
                continue

            indice = int(mots[1])
            taille = int(mots[2])
            
            # verification indice valide
            if indice >= taille_memoire or indice < 0 :
                print(f"error: index {indice} out of bounds")
                continue
            else:
                # on envoie la portion de bytearray en hex
                print(memoire[indice:indice+taille].hex())

        elif mots[0] == "POST" :
            #verification arguments
            if len(mots) != 3:
                print("usage : POST index hex_val")
                continue

            indice = int(mots[1])
            hex_val = int(mots[2])
            data_bytes = bytearray.fromhex(hex_val)
            taille = len(data_bytes)

            if indice < 0 or indice + taille > taille_memoire:
                print(f"error: out of bounds")
            else:
                # on ecrit toute la portion d'un coup
                memoire[indice:indice+taille] = data_bytes
                print('ok')
    
    print("bye")