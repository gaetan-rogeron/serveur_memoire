import sys, os

if __name__ == "__main__":

    taille_memoire = sys.argv[1]
    port = sys.argv[2]

    debug = False
    sauvegarde_periodique = False

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
    r,w = os.pipe()

    pid_frontend = os.fork()
    if pid_frontend == 0 :
        # pas besoin du read côté frontend
        os.close(r)
        # la sortie standard du front va vers l'entré du pipe
        os.dup2(w, 1)
        # on ferme l'entrée
        os.close(w)
        # on lance le frontend
        os.execvp(cmd_frontend[0], cmd_frontend)
        sys.exit(1)

    pid_backend = os.fork()
    if pid_backend == 0:
        # pas besoin du write côté backend
        os.close(w)
        # l'entrée standard va vers la sortie du pipe
        os.dup2(r, 0)
        # on ferme read
        os.close(r)

        # si il y a la sauvegarde periodique on redirige la sortie d'erreur vers le fichier log
        if sauvegarde_periodique :
            fd_log = os.open(fichier_log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644) # permission pour executer
            os.dup2(fd_log, 2)
            os.close(fd_log)
        os.execvp(cmd_backend[0],cmd_backend)
        sys.exit(1)


    os.close(r)
    os.close(w)

    os.waitpid(pid_backend,0)
    os.waitpid(pid_frontend,0)


