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
            segments_table[nom] = {"base": a, "size": taille, "pagesize": pagesize}
            affichage_debug()
            print("ok", file=sys.stderr)
            return

    # le PUT echoue
    print(f"error: not enough memory to create segment {nom} of size {taille}", file=sys.stderr)

if __name__ == "__main__":
    taille_memoire = int(sys.argv[1])
    if "--debug" in sys.argv:
        debug = True
    
    for ligne in sys.stdin:
        mots = ligne.split()
        if not mots: continue
        commande = mots[0]

        if commande == "PUT":
            # Syntaxe : PUT <nom> <taille> <pagesize>
            put(mots[1], int(mots[2]), int(mots[3]))

        elif commande == "GET":
            # GET nom page_num
            nom, page_num = mots[1], int(mots[2])
            if nom not in segments_table:
                print(f"error: {nom} inconnu", file=sys.stderr)
            else:
                seg = segments_table[nom]
                # Traduction Page -> Adresse Physique
                adresse_physique = seg['base'] + (page_num * seg['pagesize'])
                # On demande au Backend une plage d'octets
                print(f"GET {adresse_physique} {seg['pagesize']}")

        elif commande == "POST":
            # POST nom page_num hex_data
            nom, page_num, hex_data = mots[1], int(mots[2]), mots[3]
            if nom not in segments_table:
                print(f"error: {nom} inconnu", file=sys.stderr)
            else:
                seg = segments_table[nom]
                adresse_physique = seg['base'] + (page_num * seg['pagesize'])
                # On envoie les donnees hex au backend
                print(f"POST {adresse_physique} {hex_data}")

        elif commande == "DELETE":
            if mots[1] in segments_table:
                del segments_table[mots[1]]
                print("ok", file=sys.stderr)