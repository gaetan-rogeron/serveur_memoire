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


if __name__ == "__main__":

    taille_memoire = int(sys.argv[1])

    if "--debug" in sys.argv:
        debug = True
    
    for ligne in sys.stdin:

        mots = ligne.split()

        # si on entre uniquement entree
        if not mots:
            continue

        commande = mots[0]

        if commande == "PUT":
            taille = int(mots[2])
            put(mots[1], taille)

        elif commande == "DELETE":
            delete(mots[1])

        elif commande == "GET":
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

        elif commande == "POST":
            nom = mots[1]

            indice = int(mots[2])
            octet = int(mots[3])

            if nom not in segments_table:
                print(f"segment {nom} n'existe pas",file = sys.stderr)
            elif indice < 0 or indice >= segments_table[nom]['size']:
                print(f"error: index {indice} out of bounds, {nom} size is {segments_table[nom]['size']}", file=sys.stderr)
            else:
                # traduction et envoie sur stdout
                addresse_physique = segments_table[nom]['base'] + indice
                print(f"POST {addresse_physique} {octet}")
