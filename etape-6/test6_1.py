from remotememory import RemoteMemory

print("TEST")
try:
    # On utilise "with" pour activer le Context Manager (__enter__)
    with RemoteMemory("localhost", 12345, "testseg", 100, debug=True) as mem:
        
        mem[0] = 42 # POST
        print(f"Valeur lue : {mem[0]}") # GET
        
        print("ceci est un crash.")
        division = 1 / 0 # Provoque une ZeroDivisionError
        
        print("Cette ligne affichera pas")

except ZeroDivisionError:
    print("CRASH")