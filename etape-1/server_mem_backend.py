import sys

if __name__ == "__main__":
    # verification des arguments
    if len(sys.argv) != 2 :
        print("Usage: python server_mem_backend.py memsize")
        sys.exit(1)

    # initialisation memoire
    taille_memoire = int(sys.argv[1]) # conversion string -> int
    memoire = bytearray([32] * taille_memoire)

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