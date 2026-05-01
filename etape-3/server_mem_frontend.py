import sys

segments_table = {}
taille_memoire = 0
debug = False

def affichage_debug():
    if debug :
        print(f"[debug] segments_table={segments_table}", file=sys.stderr)

def put(nom, taille):
    # 1 on verifie que le nom est pas utilise
    if nom in segments_table:
        print(f"error: le segment {nom} existe deja", file= sys.stderr)
    
    # 2 on construit la liste
    L = [0]
    for segment in segments_table.values():
        L.append(segment['base'] + segment['size'])

    L.sort()

    # 3
    for a in L:
        # verification depassement
        if a + taille > taille_memoire:
            continue
            
        intersection = False
        debut_nouveau = a
        fin_nouveau = a + taille - 1

        # verification intersection
        for _ , seg_data in segments_table.items():
            debut_existant = seg_data['base']
            fin_existant = debut_existant + seg_data['size'] - 1

            if max(debut_nouveau, debut_existant) <= min(fin_nouveau, fin_existant):
                intersection = True
                break
        
        # on place name en a
        if not intersection:
            segments_table[nom] = {"base": a, "size": taille}
            affichage_debug()
            print("ok", file=sys.stderr)
            return

    # le PUT echoue
    affichage_debug()
    print(f"error: not enough memory to create segment {nom} of size {taille}", file=sys.stderr)

def delete(nom):
    # verification existance
    if nom in segments_table:
        del segments_table[nom]
        affichage_debug()
        print("ok", file=sys.stderr)
    else :
        print(f"error : le segments {nom} n'existe pas", file= sys.stderr)


def main():
    global taille_memoire
    global debug

    # verification du nombre d'arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 server_mem_frontend.py taille_memoire (--debug)", file=sys.stderr)
        sys.exit(1)

    # Verification du --debug
    if len(sys.argv) == 3 and sys.argv[2] != "--debug":
        print("Usage: python3 server_mem_frontend.py taille_memoire (--debug)", file=sys.stderr)
        print("erreur: argument optionnel", file=sys.stderr)
        sys.exit(1)

    try:
        taille_memoire = int(sys.argv[1])
    except ValueError:
        print("erreur: la taille memoire doit etre un entier", file=sys.stderr)
        sys.exit(1)

    if "--debug" in sys.argv:
        debug = True
    
    for ligne in sys.stdin:

        mots = ligne.split()

        # si on entre uniquement entree
        if not mots:
            continue

        commande = mots[0]

        if commande == "PUT":
            if len(mots) != 3:
                    print("usage : PUT nom taille", file=sys.stderr)
                    continue
            
            try:
                taille = int(mots[2])
                if taille <= 0:
                    print("erreur: taille > 0 ", file=sys.stderr)
                else:
                    put(mots[1], taille)
            except ValueError:
                print("erreur: la taille doit etre un nombre entier", file=sys.stderr)

        elif commande == "DELETE":
            if len(mots) != 2:
                    print("usage : DELETE nom", file=sys.stderr)
                    continue
            
            delete(mots[1])

        elif commande == "GET":
            if len(mots) != 3:
                    print("usage : GET nom indice", file=sys.stderr)
                    continue

            try:
                nom = mots[1]
                indice = int(mots[2])

                # verification existance
                if nom not in segments_table:
                    print(f"le segment {nom} n'existe pas", file=sys.stderr)

                # verification indice
                elif indice< 0 or indice>= segments_table[nom]['size']:
                    print("indice invalide", file=sys.stderr)

                else:
                    # Traduction addresse virtuelle -> addresse physique
                    addresse_physique = segments_table[nom]['base'] + indice
                    print(f"GET {addresse_physique}")
                    sys.stdout.flush() # force l'envoi immediat dans le pipe
            except ValueError:
                print("erreur: l'indice doit etre un entier", file=sys.stderr)

        elif commande == "POST":

            if len(mots) != 4:
                print("usage : POST nom indice octet", file=sys.stderr)
                continue
            try:
                nom = mots[1]
                indice = int(mots[2])
                octet = int(mots[3])

                if nom not in segments_table:
                    print(f"segment {nom} n'existe pas",file = sys.stderr)
                elif indice < 0 or indice >= segments_table[nom]['size']:
                    print(f"error: index {indice} out of bounds, {nom} size is {segments_table[nom]['size']}", file=sys.stderr)
                elif octet < 0 or octet > 255:
                    print("error: la valeur doit etre un octet (0-255)", file=sys.stderr)
                else:
                    # traduction et envoie sur stdout
                    addresse_physique = segments_table[nom]['base'] + indice
                    print(f"POST {addresse_physique} {octet}")
                    sys.stdout.flush()
            except ValueError:
                print("erreur: l'indice et l'octet doivent etre des entiers", file=sys.stderr)
        else:
            print("erreur: commande inconnue", file=sys.stderr)

if __name__ == "__main__":
    main()