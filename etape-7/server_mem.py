import sys, os, socket, signal

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage: python server_mem.py <memsize> <port> [--debug] [--periodic-log <logfile>]", file=sys.stderr)
        sys.exit(1)
    
    taille_memoire = sys.argv[1]
    port = int(sys.argv[2])

    debug = False
    sauvegarde_periodique = False
    fichier_log = ""

    cmd_backend = ["python3","-u","server_mem_backend.py",taille_memoire] # -u pour enlever le buffering "toutes les reponses viennent apres le ctrl+D"
    cmd_frontend =["python3","-u","server_mem_frontend.py",taille_memoire]

    if "--periodic-log" in sys.argv:
        sauvegarde_periodique = True
        cmd_backend.append("--periodic-log")
        for i in range (len(sys.argv)):
            if sys.argv[i] == "--periodic-log" and i + 1 < len(sys.argv):
                fichier_log = sys.argv[i+1]
                break

    if "--debug" in sys.argv:
        debug = True
        cmd_frontend.append("--debug")


    # read (sortie) write (entrée) 
    r_StoF,w_StoF = os.pipe() # serveur --> frontend
    r_FtoB,w_FtoB = os.pipe() # frontend --> backend
    r_FBtoS,w_FBtoS = os.pipe() # front et back --> serveur


    pid_frontend = os.fork()
    if pid_frontend == 0 :
        os.dup2(r_StoF, 0) # lit depuis la sortie du server
        os.dup2(w_FtoB, 1) # ecrit vers le backend
        os.dup2(w_FBtoS, 2) # ecrit les erreurs vers le serveur

        # on ferme les originaux
        for file in [r_StoF,w_StoF,r_FtoB,w_FtoB,r_FBtoS,w_FBtoS]:
            os.close(file)


        # on lance le frontend
        os.execvp(cmd_frontend[0], cmd_frontend)
        sys.exit(1)


    pid_backend = os.fork()
    if pid_backend == 0:
        os.dup2(r_FtoB,0) # lit depuis le frontend
        os.dup2(w_FBtoS,1) # ecrit vers le serveur
        

        # si il y a la sauvegarde periodique on redirige la sortie d'erreur vers le fichier log
        if sauvegarde_periodique :
            fd_log = os.open(fichier_log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644) # permission pour executer
            os.dup2(fd_log, 2)
            os.close(fd_log)

        # on ferme les originaux
        for file in [r_StoF,w_StoF,r_FtoB,w_FtoB,r_FBtoS,w_FBtoS]:
            os.close(file)


        # on lance le backend
        os.execvp(cmd_backend[0],cmd_backend)
        sys.exit(1)

    # on ferme ceux dont on a pas besoin
    os.close(r_StoF)
    os.close(w_FtoB)
    os.close(r_FtoB)
    os.close(w_FBtoS)

    # init server
    serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # eviter l'erreur "address already use" quand on relance
    serveur_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    serveur_socket.bind(('',port))
    serveur_socket.listen(5) # jusqu'a 5 clients en attente

    print(f"Serveur en marche sur le port {port}")

    try:
        while True:
            # accepte un client
            client_socket, addr = serveur_socket.accept()
            
            # le serveur lit la requete 
            data = client_socket.recv(4046)
            if not data :
                client_socket.close()
                continue
            
            # fix pour etape 6 : rajoute un \n a la fin vu que remotememory ne le fait pas
            if not data.endswith(b'\n'):
                data += b'\n'

            
            # envoie la requete dans le pipe vers Frontend
            os.write(w_StoF, data)

            # attend la reponse du front et back (modif pour le 6.2)
            reponse = b""
            while b'\n' not in reponse:
                chunk = os.read(r_FBtoS, 4096)
                if not chunk: # securite si le pipe se casse
                    break
                reponse += chunk

            # renvoie la reponse au client
            client_socket.sendall(reponse)
            client_socket.close()

    except KeyboardInterrupt:
        print("Arret du serveur")
    
    finally:
        # nettoyage propre quand Ctrl + C
        serveur_socket.close()
        os.close(w_StoF)
        os.close(r_FBtoS)

        #tue les processus enfants
        os.kill(pid_frontend, signal.SIGTERM)
        os.kill(pid_backend, signal.SIGTERM)
        os.waitpid(pid_backend,0)
        os.waitpid(pid_frontend,0)
        


