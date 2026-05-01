import sys, signal

memoire = None #declaration de la memoire pour quelle soit globale

def sauvegarde_periodique(signum, frame):
    global memoire
    print(list(memoire), file=sys.stderr) # print vers la sortie 2 erreur et liste pour que ca affiche bien

    signal.alarm(1) # continuer la boucle toutes les secondes


def main():
    global memoire

    # verification du nombres d'arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python server_mem_backend.py memsize (--periodic-log)",file=sys.stderr)
        sys.exit(1)

    # Verification stricte du 3eme argument s'il existe
    if len(sys.argv) == 3 and sys.argv[2] != "--periodic-log":
        print("Usage: python server_mem_backend.py memsize (--periodic-log)",file=sys.stderr)
        print("erreur: argument optionnel inconnu",file=sys.stderr)
        sys.exit(1)

    # initialisation memoire + verification taille --> int
    try:
        taille_memoire = int(sys.argv[1]) # conversion string -> int
    except ValueError:
        print("Erreur: la taille memoire doit etre un entier",file=sys.stderr)
        sys.exit(1)
    
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
                print("usage : GET index taille",file=sys.stderr)
                continue
            try:        
                indice = int(mots[1])
                taille = int(mots[2])
                
                # verification indice valide
                if indice < 0 or indice + taille > taille_memoire :
                    print(f"error: index {indice} out of bounds", file=sys.stderr)
                    continue
                else:
                    # on envoie la portion de bytearray en hexca
                    print(memoire[indice:indice+taille].hex())
                    sys.stdout.flush()
            except ValueError:
                print("erreur: l'index et la taille doit etre un nombre", file=sys.stderr)


        elif mots[0] == "POST" :
            #verification arguments
            if len(mots) != 3:
                print("usage : POST index hex_val", file=sys.stderr)
                continue
            
            try:
                indice = int(mots[1])
                hex_val = mots[2]
                data_bytes = bytearray.fromhex(hex_val)
                taille = len(data_bytes)

                if indice < 0 or indice + taille > taille_memoire:
                    print(f"error: out of bounds", file=sys.stderr)
                else:
                    # on ecrit toute la portion d'un coup
                    memoire[indice:indice+taille] = data_bytes
                    print('ok')
                    sys.stdout.flush()
            except ValueError:
                print("erreur: l'index et la valeur doit etre un nombre",file=sys.stderr)

        

if __name__ == "__main__":
    main() 