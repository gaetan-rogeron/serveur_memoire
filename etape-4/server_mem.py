import sys, os

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 server_mem.py taille_memoire port (--periodic-log fichier) (--debug)", file=sys.stderr)
        sys.exit(1)

    taille_memoire = sys.argv[1]
    port = sys.argv[2]

    sauvegarde_periodique = False
    fichier_log = "mem.log" # nom par default 

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
        cmd_frontend.append("--debug")


    # read (sortie) write (entrée) 
    r_StoF, w_StoF = os.pipe()
    r_FtoB, w_FtoB = os.pipe()

    pid_frontend = os.fork()
    if pid_frontend == 0 :
        # lit dans le tube 1
        os.dup2(r_StoF, 0)
        # ecrit dans le tube 2
        os.dup2(w_FtoB, 1)
        
        # ferme tous les acces originaux pour eviter les fuites
        os.close(r_StoF)
        os.close(w_StoF)
        os.close(r_FtoB)
        os.close(w_FtoB)
        
        os.execvp(cmd_frontend[0], cmd_frontend)
        sys.exit(1)

    pid_backend = os.fork()
    if pid_backend == 0:
        # lit le Tube 2
        os.dup2(r_FtoB, 0)
        
        # ferme tout le reste
        os.close(r_StoF)
        os.close(w_StoF)
        os.close(r_FtoB)
        os.close(w_FtoB)

        # si il y a la sauvegarde periodique on redirige la sortie d'erreur vers le fichier log
        if sauvegarde_periodique :
            fd_log = os.open(fichier_log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644) # permission pour executer
            os.dup2(fd_log, 2)
            os.close(fd_log)
        os.execvp(cmd_backend[0],cmd_backend)
        sys.exit(1)


    os.close(r_StoF)
    os.close(r_FtoB)
    os.close(w_FtoB)


    try:    
        for ligne in sys.stdin:
            os.write(w_StoF, ligne.encode()) # os.write demande des bytes donc .encode()
    except KeyboardInterrupt:
        print("Arret du serveur")
    finally:
        os.close(w_StoF)
        os.waitpid(pid_backend,0)
        os.waitpid(pid_frontend,0)


if __name__ == "__main__":
    main()