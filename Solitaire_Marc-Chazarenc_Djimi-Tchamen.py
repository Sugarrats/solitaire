# ------------
# Importations
# ------------
import random
import os
import ctypes

ROUGE = "\033[91m"
NORMAL = "\033[0m"

# ---------------
# Sous-programmes
# ---------------

# =====================================================================
# CRÉATION DU JEU
# =====================================================================

# Cette fonction va créer le paquets de carte pour notre jeu
# Elle ne prend pas de paramétre et renvoi la pioche ( une liste )
def creerPioche():
    pioche = []
    for couleur in ["coeur", "carreau", "trefle", "pique"]:
        for i in range(13):
            pioche.append((i + 1, couleur))

    random.shuffle(pioche)

    return pioche


# Cette fonction crée les 7 colonnes du jeu à partir de la pioche
# Elle prend en paramètre la pioche (une liste de cartes)
# Elle renvoie la liste des colonnes
# Les cartes distribuées sont retirées de la pioche
def creerColonnes(pioche):
    colonnes = []

    for i in range(7):
        colonne = {"cachees": [], "visibles": []}

        # La colonne i reçoit i cartes cachées
        for j in range(i):
            colonne["cachees"].append(pioche.pop())

        # Puis une carte visible par-dessus
        colonne["visibles"].append(pioche.pop())

        colonnes.append(colonne)

    return colonnes


# Cette fonction crée les paramètres par défaut du jeu
# Elle ne prend pas de paramètre et renvoie un dictionnaire
# (ils seront modifiables au point d'étape 4)
def creerParametres():
    parametres = {
        "cartesPiochees": 1,   
        "aideActive": True     
    }
    return parametres


# Cette fonction crée une nouvelle partie
# Elle prend en paramètre les paramètres du jeu (dictionnaire)
# Elle renvoie un dictionnaire contenant tous les éléments du jeu
def creerPartie(parametres):
    pioche = creerPioche()
    colonnes = creerColonnes(pioche)

    # Une fondation par couleur, vide au départ
    fondations = {
        "coeur": [],
        "carreau": [],
        "trefle": [],
        "pique": []
    }

    partie = {
        "pioche": pioche,           
        "defausse": [],             
        "colonnes": colonnes,
        "fondations": fondations,
        "parametres": parametres
    }

    return partie

def activerCouleurs():
    if os.name == "nt":  
        kernel32 = ctypes.windll.kernel32
        console = kernel32.GetStdHandle(-11)            
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(console, ctypes.byref(mode))
        kernel32.SetConsoleMode(console, mode.value | 0x0004) 



# =====================================================================
# AFFICHAGE 
# =====================================================================

# Cette fonction transforme une carte (tuple) en texte lisible pour l'affichage
def carteEnTexte(carte):
    noms = {1: "A", 11: "V", 12: "D", 13: "R"}
    symboles = {"coeur": "♥", "carreau": "♦", "trefle": "♣", "pique": "♠"}

    valeur = carte[0]
    couleur = carte[1]

    if valeur in noms:
        texteValeur = noms[valeur]
    else:
        texteValeur = str(valeur)

    return texteValeur + symboles[couleur]

# Cette fonction transforme un texte rentré par l'utilisateur en carte (tuple)
# Elle prend en paramètre le texte saisi
# Elle renvoie la carte (valeur, couleur), ou None si la saisie est invalide
def texteEnCarte(texte):
    num = {"a": 1, "v": 11, "d": 12, "r": 13}
    symboles = {"co": "coeur", "ca": "carreau", "tr": "trefle", "pi": "pique"}

    valeur = texte[:-2]    
    couleur = texte[-2:]  

    if couleur not in symboles:
        carteCherchee = None

    elif valeur in num:
        carteCherchee = (num[valeur], symboles[couleur])

    elif valeur.isdigit() and 1 <= int(valeur) <= 13:
        carteCherchee = (int(valeur), symboles[couleur])

    else:
        carteCherchee = None

    return carteCherchee


# Cette fonction renvoie le texte d'une carte, complété par des espaces
# jusqu'à la largeur demandée, et écrit en rouge si c'est un coeur ou un carreau
# Elle prend en paramètre la carte (tuple) et la largeur (entier)
def carteEnCouleur(carte, largeur):
    # On complète AVANT d'ajouter la couleur : les codes couleur sont des
    # caractères invisibles qui fausseraient le calcul de ljust()
    texte = carteEnTexte(carte).ljust(largeur)

    if carte[1] == "coeur" or carte[1] == "carreau":
        return ROUGE + texte + NORMAL
    else:
        return texte


# Cette fonction affiche l'état du jeu dans la console
# Elle prend en paramètre la partie (dictionnaire) et ne renvoie rien
def afficherPartie(partie):
    largeur = 6 
    nbPioche = len(partie["pioche"])
    nbDefausse = len(partie["defausse"])

    # --- Ligne du haut : pioche, défausse et fondations ---
    if len(partie["pioche"]) > 0:
        textePioche = "[XX]"
    else:
        textePioche = "[  ]"

    if len(partie["defausse"]) > 0:
        texteDefausse = carteEnCouleur(partie["defausse"][-1], 0)
    else:
        texteDefausse = "[  ]"

    ligneHaut = "Pioche: " + textePioche + " (" + str(nbPioche) + ") " +  "Défausse: " + texteDefausse + " (" + str(nbDefausse) + ")" 
    ligneFondation = "Fondations: "
    for couleur in partie["fondations"]:
        fondation = partie["fondations"][couleur]
        if len(fondation) > 0:
            ligneFondation += carteEnCouleur(fondation[-1], largeur)
        else:
            ligneFondation += "[  ]".ljust(largeur)

    print(ligneHaut)
    print(ligneFondation)
    print()

    # --- Les colonnes ---
    # Numéros des colonnes
    entete = ""
    for i in range(len(partie["colonnes"])):
        entete += str(i + 1).ljust(largeur)
    print(entete)

    # Hauteur de la plus grande colonne
    hauteurMax = 0
    for colonne in partie["colonnes"]:
        hauteur = len(colonne["cachees"]) + len(colonne["visibles"])
        if hauteur > hauteurMax:
            hauteurMax = hauteur

    # On affiche ligne par ligne
    for ligne in range(hauteurMax):
        texteLigne = ""
        for colonne in partie["colonnes"]:
            nbCachees = len(colonne["cachees"])
            nbVisibles = len(colonne["visibles"])

            if ligne < nbCachees:
                texteLigne += "[XX]".ljust(largeur)
            elif ligne < nbCachees + nbVisibles:
                carte = colonne["visibles"][ligne - nbCachees]
                texteLigne += carteEnCouleur(carte, largeur)
            else:
                texteLigne += " " * largeur
        print(texteLigne)


# =====================================================================
# MENUS ET BOUCLE DE JEU
# =====================================================================

# Cette fonction affiche les règles du jeu
# Elle ne prend pas de paramètre et ne renvoie rien
def afficherRegles():
    print()
    print("===== RÈGLES DU SOLITAIRE =====")
    print("But : ranger toutes les cartes par famille dans les fondations, de l'As au Roi.")
    print("- Dans les colonnes, on pose une carte de valeur inférieure d'un rang")
    print("  et de couleur opposée (rouge sur noir, noir sur rouge).")
    print("- Seul un Roi peut être posé sur une colonne vide.")
    print("- Quand on libère une carte cachée, elle est retournée.")
    print("- La pioche permet de retourner des cartes sur la défausse.")
    input("Appuyez sur Entrée pour revenir au menu...")


# Cette fonction est le menu principal du jeu
# C'est la seule fonction appelée par le programme principal
# Elle ne prend pas de paramètre et ne renvoie rien
def menu():
    activerCouleurs()
    parametres = creerParametres()
    continuer = True

    while continuer:
        print()
        print("========== Bienvenue dans le jeu du SOLITAIRE ==========")
        print("1. Nouvelle partie")
        print("2. Reprendre une partie sauvegardée")
        print("3. Paramètres")
        print("4. Règles du jeu")
        print("5. Quitter")
        choix = input("-> ")

        if choix == "1":
            partie = creerPartie(parametres)
            jouer(partie)
        elif choix == "2":
            partie = chargerPartie()
            if partie is not None:
                jouer(partie)
        elif choix == "3":
            modifierParametres(parametres)
        elif choix == "4":
            afficherRegles()
        elif choix == "5":
            continuer = False
            print("Au revoir !")
        else:
            print("Choix invalide, tapez un nombre entre 1 et 5 (｡ᵕ ◞ _◟)")


# Cette fonction fait tourner une partie jusqu'à ce que le joueur
# quitte ou gagne
# Elle prend en paramètre la partie (dictionnaire) et ne renvoie rien
def jouer(partie):
    enCours = True

    while enCours:
        print()
        afficherPartie(partie)
        print()
        print("Commandes : [p] piocher  [d] déplacer")
        print("            [a] aide [s] sauvegarder")
        print("            [q] quitter")
        commande = input("> ").lower()
        commande = commande.replace(" ","")

        if commande == "p":
            piocher(partie)
        elif commande == "d":
            deplacer(partie)
        elif commande == "a":
            proposerCoups(partie)
        elif commande == "s":
            sauvegarderPartie(partie)
        elif commande == "q":
            enCours = False
        else:
            print("Commande inconnue (｡ᵕ ◞ _◟)")

        if not victoireAssuree(partie):
            print("Bien joué ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧")
            rangerAutomatiquement(partie)
            enCours = False




# Cette fonction indique si une carte est rouge (coeur ou carreau)
# Elle prend en paramètre une carte (tuple) et renvoie un booléen
def estRouge(carte):
    return carte[1] == "coeur" or carte[1] == "carreau"

# Cette fonction vérifie si une carte peut être posée sur une colonne
# Elle prend en paramètre la carte (tuple) et la colonne (dictionnaire)
# Elle renvoie True si le déplacement respecte les règles, False sinon
def peutPoserSurColonne(carte, colonne):
    # Colonne vide : seul un Roi peut y être posé
    if len(colonne["cachees"]) == 0 and len(colonne["visibles"]) == 0:
        autorise = carte[0] == 13

    else:
        carteDessous = colonne["visibles"][-1]
        autorise = carte[0] == carteDessous[0] - 1 and estRouge(carte) != estRouge(carteDessous)

    return autorise

# Cette fonction vérifie si une carte peut être posée sur une fondation
# Elle prend en paramètre la carte (tuple) et la fondation  (liste)
# Elle renvoie True si le déplacement respecte les règles, False sinon
def peutPoserSurFondation(carte, fondation):

    if len(fondation) == 0:
        autorise = carte[0] == 1

    else:
        carteDessous = fondation[-1]
        autorise = carte[0] == carteDessous[0] + 1

    return autorise

# Cette fonction demande au joueur la destination
# Elle ne prend pas de paramètre
# Elle renvoie l'indice de la colonne si la destination est une colonne (0 à 6), 
# f si c'est une fondation 
# ou None si la saisie est invalide
def demanderDestination():
    print("Ou faut il poser la carte ? (1 à 7 pour les colonnes f pour une fondation)")
    saisie = input(" -> ").replace(" ", "")
    saisie = saisie.lower()

    if saisie.isdigit() and 1 <= int(saisie) <= 7:
        destination = int(saisie) - 1  

    elif saisie == "f" :
        destination = "f"

    else:
        destination = None

    return destination



# Cette fonction demande au joueur la carte à déplacer
# Elle ne prend pas de paramètre
# Elle renvoie la carte (tuple), ou None si la saisie est invalide
def demanderCarte():
    print("Quelle carte faut-il déplacer ? (valeur A, 2-10, V, D, R puis couleur co, ca, tr, pi)")
    saisie = input(" -> ")
    saisie = saisie.replace(" ", "")
    saisie = saisie.lower()

    return texteEnCarte(saisie)

# Cette fonction retourne la dernière carte cachée d'une colonne
# si plus aucune carte n'est visible
# Elle prend en paramètre la colonne (dictionnaire) et ne renvoie rien
def retournerCarteCachee(colonne):
    if len(colonne["visibles"]) == 0 and len(colonne["cachees"]) > 0:
        colonne["visibles"].append(colonne["cachees"].pop())



# Cette fonction gère un déplacement complet demandé par le joueur
# Elle prend en paramètre la partie (dictionnaire) et ne renvoie rien
def deplacer(partie):
    emplacementCarte = None

    carte = demanderCarte()

    if carte is None:
        print("Carte invalide.")
    else:
        # Recherche dans les cartes visibles de chaque colonne
        for i in range(len(partie["colonnes"])):
            visibles = partie["colonnes"][i]["visibles"]
            for j in range(len(visibles)):
                if visibles[j] == carte:
                    emplacementCarte = (i, j)

        # Recherche sur la dernière carte de la défausse
        if len(partie["defausse"]) > 0 and partie["defausse"][-1] == carte:
            emplacementCarte = "defausse"

        if emplacementCarte is None:
            print("Cette carte n'est pas disponible (｡ᵕ ◞ _◟)")
        else:
            destination = demanderDestination()

            if destination is None:
                print("Destination invalide (｡ᵕ ◞ _◟)")

            elif emplacementCarte != "defausse" and emplacementCarte[0] == destination:
                print("La carte est déjà là (｡ᵕ ◞ _◟)")

            elif destination == "f":

                if not peutPoserSurFondation(carte, partie["fondations"][carte[1]]):
                    print("Déplacement interdit par les règles (｡ᵕ ◞ _◟)")

                else :
                    fondationArrivee = partie["fondations"][carte[1]]

                    if emplacementCarte == "defausse":
                        fondationArrivee.append(partie["defausse"].pop())

                    else:
                        colonneDepart = partie["colonnes"][emplacementCarte[0]]

                        if emplacementCarte[1] != len(colonneDepart["visibles"]) - 1:
                            print("Une seule carte à la fois dans la fondation (｡ᵕ ◞ _◟)")

                        else:
                            fondationArrivee.append(colonneDepart["visibles"].pop())
                            retournerCarteCachee(colonneDepart)

            elif not peutPoserSurColonne(carte, partie["colonnes"][destination]):
                print("Déplacement interdit par les règles (｡ᵕ ◞ _◟)")

            else:
                colonneArrivee = partie["colonnes"][destination]

                if emplacementCarte == "defausse":
                    colonneArrivee["visibles"].append(partie["defausse"].pop())

                else:
                    colonneDepart = partie["colonnes"][emplacementCarte[0]]
                    position = emplacementCarte[1]

                    cartesDeplacees = colonneDepart["visibles"][position:]
                    colonneDepart["visibles"] = colonneDepart["visibles"][:position]
                    colonneArrivee["visibles"] += cartesDeplacees

                    retournerCarteCachee(colonneDepart)




# Cette procédure prend en paramétre le dictionnaire partie et ne renvoi rien
def piocher(partie):
    nbCartesPiochees = partie["parametres"]["cartesPiochees"]

    if partie["pioche"]:
        for i in range(nbCartesPiochees):
            if partie["pioche"] :
                cartePiochee = partie["pioche"].pop()
                partie["defausse"].append(cartePiochee)

    elif partie["defausse"]:
        partie["defausse"].reverse()
        partie["pioche"] = partie["defausse"]
        partie["defausse"] = []

    else:
        print("Plus aucune carte à piocher")


# Cette fonction vérifie si la partie est dans une situation de victoire assurée
# Elle prend en paramétre la partie (dictoinnaire)
# Elle renvoie True si la pioche et la défausse sont vide et si les colonnes n'ont aucune carte caché
def victoireAssuree(partie):
    assuree = len(partie["pioche"]) == 0 and len(partie["defausse"]) == 0

    for colonne in partie["colonnes"]:
        if len(colonne["cachees"]) > 0:
            assuree = False

    return assuree

# Cette fonction envoie automatiquement toutes les cartes des colonnes
# dans les fondations (à utiliser UNIQUEMENT quand la victoire est assurée)
# Elle prend en paramètre la partie (dictionnaire) et ne renvoie rien
def rangerAutomatiquement(partie):
    # On compte une seule fois les cartes restant dans les colonnes
    nbCartesRestantes = 0
    for colonne in partie["colonnes"]:
        nbCartesRestantes += len(colonne["visibles"])

    while nbCartesRestantes > 0:
        for colonne in partie["colonnes"]:
            if len(colonne["visibles"]) > 0:
                carte = colonne["visibles"][-1]
                fondation = partie["fondations"][carte[1]]

                if peutPoserSurFondation(carte, fondation):
                    fondation.append(colonne["visibles"].pop())
                    nbCartesRestantes -= 1

# À FAIRE - Point 3 : enregistrer la partie dans un fichier
def sauvegarderPartie(partie):
    print("Sauvegarde : fonctionnalité pas encore disponible.")


# À FAIRE - Point 3 : relire la partie depuis le fichier
# Doit renvoyer la partie (dictionnaire), ou None si aucune sauvegarde
def chargerPartie():
    print("Chargement : fonctionnalité pas encore disponible.")
    return None


# À FAIRE - Point 3 : afficher la liste des coups possibles
def proposerCoups(partie):
    print("Aide : fonctionnalité pas encore disponible.")


# À FAIRE - Point 4 : menu pour changer les paramètres (difficulté)
def modifierParametres(parametres):
    print("Paramètres : fonctionnalité pas encore disponible.")


# -------------------
# Programme principal
# -------------------
menu()