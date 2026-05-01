import sys

segments_table = {}
taille_memoire = 0
debug = False

def affichage_debug():
    if debug :
        print(f"[debug] segments_table={segments_table}", file=sys.stderr)

def put(nom, taille, pagesize):
    # 1 on verifie que le nom est pas utilise
    if nom in segments_table:
        print(f"error: le segment {nom} existe deja", file=sys.stderr)
        return
    
    # 2 on construit la liste
    L = [0]
    for segment in segments_table.values():
        L.append(segment['base'] + segment['size'])

    L.sort()

    # 3
    for a in L:
        # verification depassement memoire physique
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
            segments_table[nom] = {"base": a, "size": taille, "pagesize": pagesize}
            affichage_debug()
            print("ok", file=sys.stderr)
            return

    # le PUT echoue
    print(f"error: not enough memory to create segment {nom} of size {taille}", file=sys.stderr)


def main():
    global taille_memoire
    global debug

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 server_mem_frontend.py taille_memoire --debug", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) == 3 and sys.argv[2] != "--debug":
        print("Usage: python3 server_mem_frontend.py taille_memoire --debug", file=sys.stderr)
        print("Erreur: argument optionnel inconnu", file=sys.stderr)
        sys.exit(1)

    try:
        taille_memoire = int(sys.argv[1])
    except ValueError:
        print("Erreur: la taille memoire doit etre un entier", file=sys.stderr)
        sys.exit(1)

    if "--debug" in sys.argv:
        debug = True
    try:
        for ligne in sys.stdin:
            mots = ligne.split()
            if not mots: 
                continue
            
            commande = mots[0]

            if commande == "PUT":
                if len(mots) != 4:
                    print("usage: PUT nom taille pagesize", file=sys.stderr)
                    continue
                
                try:
                    taille = int(mots[2])
                    pagesize = int(mots[3])
                    if taille <= 0 or pagesize <= 0:
                        print("error: taille et pagesize doivent etre positifs", file=sys.stderr)
                    else:
                        put(mots[1], taille, pagesize)
                except ValueError:
                    print("error: taille et pagesize doivent etre des entiers", file=sys.stderr)

            elif commande == "GET":
                # GET nom page_num
                if len(mots) != 3:
                    print("usage: GET <nom> <page_num>", file=sys.stderr)
                    continue

                try:
                    nom = mots[1]
                    page_num = int(mots[2])

                    if nom not in segments_table:
                        print(f"error: {nom} inconnu", file=sys.stderr)
                    else:
                        seg = segments_table[nom]
                        
                        if page_num < 0 or (page_num * seg['pagesize']) >= seg['size']:
                            print(f"error: page {page_num} out of bounds pour {nom}", file=sys.stderr)
                        else:
                            # Traduction Page -> Adresse Physique
                            adresse_physique = seg['base'] + (page_num * seg['pagesize'])
                            
                            # On demande au Backend une plage d'octets
                            print(f"GET {adresse_physique} {seg['pagesize']}")
                            sys.stdout.flush()
                except ValueError:
                    print("error: page_num doit etre un entier", file=sys.stderr)

            elif commande == "POST":
                # POST nom page_num hex_data
                if len(mots) != 4:
                    print("usage: POST nom page_num hex_data", file=sys.stderr)
                    continue

                try:
                    nom = mots[1]
                    page_num = int(mots[2])
                    hex_data = mots[3]

                    if nom not in segments_table:
                        print(f"error: {nom} inconnu", file=sys.stderr)
                    else:
                        seg = segments_table[nom]

                        if page_num < 0 or (page_num * seg['pagesize']) >= seg['size']:
                            print(f"error: page {page_num} out of bounds pour {nom}", file=sys.stderr)
                        else:
                            adresse_physique = seg['base'] + (page_num * seg['pagesize'])
                            
                            # On envoie les donnees hex au backend
                            print(f"POST {adresse_physique} {hex_data}")
                            sys.stdout.flush() #
                except ValueError:
                    print("error: page_num doit etre un entier", file=sys.stderr)

            elif commande == "DELETE":
                if len(mots) != 2:
                    print("usage: DELETE <nom>", file=sys.stderr)
                    continue

                if mots[1] in segments_table:
                    del segments_table[mots[1]]
                    print("ok", file=sys.stderr)
                else:
                    print(f"error: segment {mots[1]} inconnu", file=sys.stderr)
            
            else:
                print(f"error: commande inconnue '{commande}'", file=sys.stderr)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()