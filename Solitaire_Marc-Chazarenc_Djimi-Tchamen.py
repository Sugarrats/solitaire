# ------------
# Importations
# ------------
import random
import os
import ctypes
import json

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
            pioche.append([i + 1, couleur])

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

    # 4 fondations numérotées (f1 à f4), vides au départ
    # Chacune accueille la famille de l'As qui y est posé en premier
    fondations = [[], [], [], []]

    partie = {
        "pioche": pioche,           
        "defausse": [],             
        "colonnes": colonnes,
        "fondations": fondations,
        "parametres": parametres
    }

    return partie

# ---------------------------------------------------------------------
# TEST - À RETIRER AVANT LE RENDU
# Cette fonction crée une partie presque gagnée pour tester la victoire assurée :
# il ne reste qu'une carte dans la défausse (le valet de carreau).
# En la jouant (sur la fondation ou sur la dame de trèfle), la victoire devient assurée.
# Elle prend en paramètre les paramètres du jeu (dictionnaire)
# Elle renvoie la partie (dictionnaire)
def creerPartieTest(parametres):
    # Fondations remplies de l'As au 10
    fondations = []
    for couleur in ["coeur", "carreau", "trefle", "pique"]:
        fondation = []
        for valeur in range(1, 11):
            fondation.append([valeur, couleur])
        fondations.append(fondation)

    # Les figures restantes, toutes visibles, en suites décroissantes alternées
    colonnes = [
        {"cachees": [], "visibles": [[13, "pique"], [12, "coeur"], [11, "pique"]]},
        {"cachees": [], "visibles": [[13, "coeur"], [12, "pique"], [11, "coeur"]]},
        {"cachees": [], "visibles": [[13, "trefle"], [12, "carreau"], [11, "trefle"]]},
        {"cachees": [], "visibles": [[13, "carreau"], [12, "trefle"]]},
        {"cachees": [], "visibles": []},
        {"cachees": [], "visibles": []},
        {"cachees": [], "visibles": []}
    ]

    partie = {
        "pioche": [],
        "defausse": [[11, "carreau"]],
        "colonnes": colonnes,
        "fondations": fondations,
        "parametres": parametres
    }

    return partie
# ---------------------------------------------------------------------


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

# Cette fonction transforme une carte (liste) en texte lisible pour l'affichage
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

# Cette fonction transforme un texte rentré par l'utilisateur en carte (liste)
# Elle prend en paramètre le texte saisi
# Elle renvoie la carte [valeur, couleur], ou None si la saisie est invalide
def texteEnCarte(texte):
    num = {"a": 1, "v": 11, "d": 12, "r": 13}
    symboles = {"co": "coeur", "ca": "carreau", "tr": "trefle", "pi": "pique"}

    valeur = texte[:-2]    
    couleur = texte[-2:]  

    if couleur not in symboles:
        carteCherchee = None

    elif valeur in num:
        carteCherchee = [num[valeur], symboles[couleur]]

    elif valeur.isdigit() and 1 <= int(valeur) <= 13:
        carteCherchee = [int(valeur), symboles[couleur]]

    else:
        carteCherchee = None

    return carteCherchee


# Cette fonction transforme une carte (liste) en texte tel que le joueur doit le saisir
# Elle prend en paramètre la carte (liste)
# Elle renvoie le texte, par exemple [7, "coeur"] -> "7co" et [1, "pique"] -> "api"
def carteEnSaisie(carte):
    noms = {1: "a", 11: "v", 12: "d", 13: "r"}
    codes = {"coeur": "co", "carreau": "ca", "trefle": "tr", "pique": "pi"}

    valeur = carte[0]

    if valeur in noms:
        texteValeur = noms[valeur]
    else:
        texteValeur = str(valeur)

    return texteValeur + codes[carte[1]]


# Cette fonction transforme un texte rentré par l'utilisateur en destination
# Elle prend en paramètre le texte saisi
# Elle renvoie une liste [type, indice] :
#   "3"  -> ["colonne", 2]     (colonnes 1 à 7 -> indices 0 à 6)
#   "f2" -> ["fondation", 1]   (fondations f1 à f4 -> indices 0 à 3)
# ou None si la saisie est invalide
def texteEnDestination(texte):
    if texte.isdigit() and 1 <= int(texte) <= 7:
        destination = ["colonne", int(texte) - 1]

    elif len(texte) == 2 and texte[0] == "f" and texte[1] in "1234":
        destination = ["fondation", int(texte[1]) - 1]

    else:
        destination = None

    return destination


# Cette fonction renvoie le texte d'une carte, complété par des espaces
# jusqu'à la largeur demandée, et écrit en rouge si c'est un coeur ou un carreau
# Elle prend en paramètre la carte (liste) et la largeur (entier)
def carteEnCouleur(carte, largeur):
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

    # affichage de la défausse
    if len(partie["defausse"]) > 0:

        # si on pioche une carte seule la derniére est affiché
        if partie["parametres"]["cartesPiochees"] == 1:
            texteDefausse = carteEnCouleur(partie["defausse"][-1], 0)

        # sinon les trois derniéres sont affichées
        else:
            texteDefausse = ""
            for carte in partie["defausse"][-3:]:
                texteDefausse += carteEnCouleur(carte, 4)
            

    else:
        texteDefausse = "[  ]"

    ligneHaut = "Pioche: " + textePioche + " (" + str(nbPioche) + ") " +  "Défausse: " + texteDefausse + " (" + str(nbDefausse) + ")" 
    # Numéros des fondations, alignés au-dessus de chaque fondation
    debutLigne = "Fondations: "
    numerosFondation = " " * len(debutLigne)
    ligneFondation = debutLigne
    for f in range(len(partie["fondations"])):
        numerosFondation += ("f" + str(f + 1)).ljust(largeur)

        fondation = partie["fondations"][f]
        if len(fondation) > 0:
            ligneFondation += carteEnCouleur(fondation[-1], largeur)
        else:
            ligneFondation += "[  ]".ljust(largeur)

    print(ligneHaut)
    print(numerosFondation)
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
    input("Appuyez sur Entrée pour quitter les régles...")


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
        elif choix == "t":   # TEST - À RETIRER AVANT LE RENDU
            partie = creerPartieTest(parametres)
            jouer(partie)
        else:
            print("Choix invalide, tapez un nombre entre 1 et 5 (｡ᵕ ◞ _◟)")


# Cette fonction fait tourner une partie jusqu'à ce que le joueur
# quitte ou gagne
# Toutes les commandes se font en une seule saisie, par exemple :
#   p          -> piocher
#   d 7co 3    -> déplacer le 7 de coeur sur la colonne 3
#   d aco f1   -> déplacer l'as de coeur sur la fondation 1
# Elle prend en paramètre la partie (dictionnaire) et ne renvoie rien
def jouer(partie):
    enCours = True
    historique = []

    while enCours:
        print()
        afficherPartie(partie)
        print()
        print("Commandes : [p] piocher  [d] déplacer (ex : d 7co 3, d aco f1)")
        print("            [a] aide [s] sauvegarder")
        print("            [an] annuler coup [r] régles")
        print("            [q] quitter")

        # On découpe la saisie en mots : "d 7co 3" -> ["d", "7co", "3"]
        mots = input("> ").lower().split()

        if len(mots) == 0:
            print("Commande vide (｡ᵕ ◞ _◟)")

        elif mots[0] == "d":
            if len(mots) != 3:
                print("Format : d <carte> <destination>, ex : d 7co 3 ou d aco f1 (｡ᵕ ◞ _◟)")

            else:
                carte = texteEnCarte(mots[1])
                destination = texteEnDestination(mots[2])

                if carte is None:
                    print("Carte invalide (valeur A, 2-10, V, D, R puis co, ca, tr, pi) (｡ᵕ ◞ _◟)")

                elif destination is None:
                    print("Destination invalide (1 à 7 pour les colonnes, f1 à f4 pour les fondations) (｡ᵕ ◞ _◟)")

                else:
                    historique.append(json.dumps(partie))
                    deplacer(partie, carte, destination)

        elif len(mots) > 1:
            print("Commande inconnue (｡ᵕ ◞ _◟)")

        elif mots[0] == "p":
            historique.append(json.dumps(partie))
            piocher(partie)

        elif mots[0] == "a":
            if partie["parametres"]["aideActive"] == True:
                proposerCoups(partie)

            else:
                print("L'aide est désactivée")

        elif mots[0] == "s":
            sauvegarderPartie(partie)

        elif mots[0] == "an":
            if len(historique) == 0:
                print("aucun coup à annuler (｡ᵕ ◞ _◟)")

            else :
                partie = json.loads(historique.pop())

        elif mots[0] == "r":
            afficherRegles()

        elif mots[0] == "q":
            enCours = False

        else:
            print("Commande inconnue (｡ᵕ ◞ _◟)")

        if victoireAssuree(partie):
            print("Bien joué ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧")
            rangerAutomatiquement(partie)
            enCours = False




# Cette fonction indique si une carte est rouge (coeur ou carreau)
# Elle prend en paramètre une carte (liste) et renvoie un booléen
def estRouge(carte):
    return carte[1] == "coeur" or carte[1] == "carreau"

# Cette fonction vérifie si une carte peut être posée sur une colonne
# Elle prend en paramètre la carte (liste) et la colonne (dictionnaire)
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
# Elle prend en paramètre la carte (liste) et la fondation  (liste)
# Elle renvoie True si le déplacement respecte les règles, False sinon
def peutPoserSurFondation(carte, fondation):

    # Fondation vide : seul un As peut y être posé
    if len(fondation) == 0:
        autorise = carte[0] == 1

    # Sinon : même famille et valeur supérieure d'un rang
    else:
        carteDessous = fondation[-1]
        autorise = carte[0] == carteDessous[0] + 1 and carte[1] == carteDessous[1]

    return autorise


# Cette fonction cherche une fondation sur laquelle la carte peut être posée
# Elle prend en paramètre la carte (liste) et la liste des fondations
# Elle renvoie l'indice de la première fondation possible (0 à 3), ou None s'il n'y en a pas
def trouverFondation(carte, fondations):
    numero = None

    for f in range(len(fondations)):
        if numero is None and peutPoserSurFondation(carte, fondations[f]):
            numero = f

    return numero


# Cette fonction retourne la dernière carte cachée d'une colonne
# si plus aucune carte n'est visible
# Elle prend en paramètre la colonne (dictionnaire) et ne renvoie rien
def retournerCarteCachee(colonne):
    if len(colonne["visibles"]) == 0 and len(colonne["cachees"]) > 0:
        colonne["visibles"].append(colonne["cachees"].pop())



# Cette fonction gère un déplacement complet demandé par le joueur
# Elle prend en paramètre la partie (dictionnaire), la carte à déplacer (liste)
# et la destination (liste ["colonne", indice] ou ["fondation", indice])
# La carte et la destination ont déjà été vérifiées par jouer()
# Elle ne renvoie rien
def deplacer(partie, carte, destination):
    # Emplacement de la carte, sous forme de liste :
    #   ["colonne", indice de la colonne, position dans les cartes visibles]
    #   ["defausse"]
    #   ["fondation", indice de la fondation]
    emplacementCarte = None

    # Recherche dans les cartes visibles de chaque colonne
    for i in range(len(partie["colonnes"])):
        visibles = partie["colonnes"][i]["visibles"]
        for j in range(len(visibles)):
            if visibles[j] == carte:
                emplacementCarte = ["colonne", i, j]

    # Recherche sur la dernière carte de la défausse
    if len(partie["defausse"]) > 0 and partie["defausse"][-1] == carte:
        emplacementCarte = ["defausse"]

    # Recherche sur la dernière carte de chaque fondation
    for f in range(len(partie["fondations"])):
        fondation = partie["fondations"][f]
        if len(fondation) > 0 and fondation[-1] == carte:
            emplacementCarte = ["fondation", f]

    typeArrivee = destination[0]
    indiceArrivee = destination[1]

    if emplacementCarte is None:
        print("Cette carte n'est pas disponible (｡ᵕ ◞ _◟)")

    elif emplacementCarte[0] == typeArrivee and emplacementCarte[1] == indiceArrivee:
        print("La carte est déjà là (｡ᵕ ◞ _◟)")

    elif typeArrivee == "fondation":
        fondationArrivee = partie["fondations"][indiceArrivee]

        if not peutPoserSurFondation(carte, fondationArrivee):
            print("Déplacement interdit par les règles (｡ᵕ ◞ _◟)")

        elif emplacementCarte[0] == "defausse":
            fondationArrivee.append(partie["defausse"].pop())

        elif emplacementCarte[0] == "fondation":
            fondationArrivee.append(partie["fondations"][emplacementCarte[1]].pop())

        else:
            colonneDepart = partie["colonnes"][emplacementCarte[1]]

            if emplacementCarte[2] != len(colonneDepart["visibles"]) - 1:
                print("Une seule carte à la fois dans la fondation (｡ᵕ ◞ _◟)")

            else:
                fondationArrivee.append(colonneDepart["visibles"].pop())
                retournerCarteCachee(colonneDepart)

    elif not peutPoserSurColonne(carte, partie["colonnes"][indiceArrivee]):
        print("Déplacement interdit par les règles (｡ᵕ ◞ _◟)")

    else:
        colonneArrivee = partie["colonnes"][indiceArrivee]

        if emplacementCarte[0] == "defausse":
            colonneArrivee["visibles"].append(partie["defausse"].pop())

        elif emplacementCarte[0] == "fondation":
            colonneArrivee["visibles"].append(partie["fondations"][emplacementCarte[1]].pop())

        else:
            colonneDepart = partie["colonnes"][emplacementCarte[1]]
            position = emplacementCarte[2]

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
                numero = trouverFondation(carte, partie["fondations"])

                if numero is not None:
                    partie["fondations"][numero].append(colonne["visibles"].pop())
                    nbCartesRestantes -= 1

# Cette procédure enregistre l'état de la partie dans un fichier json
# Elle prend la partie en paramétre et ne retourne rien
# Les cartes sont des listes, elles sont donc enregistrées telles quelles dans le fichier
def sauvegarderPartie(partie):
    with open('sauvegarde_partie.json','w') as file:
        json.dump(partie, file)
        print("partie sauvegardée ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧")



# Cette fonction lit le fichier json de sauvegarde de l'état de la partie
# Elle ne prend pas de paramètre
# Elle renvoie la partie (dictionnaire), ou None si aucune sauvegarde n'existe
def chargerPartie():
    if os.path.exists('sauvegarde_partie.json'):
        with open('sauvegarde_partie.json','r') as file:
            partie = json.load(file)
    else:
        print("Aucune partie sauvegardée (｡ᵕ ◞ _◟)")
        partie = None

    return partie


# Cette fonction va afficher touts les coups disponibles par ordre d'importance.
# elle prend la partie en paramétre et retourne une liste de coups
def proposerCoups(partie):
    coups = []
    nbCarteDansPioche = len(partie["pioche"])
    nbCarteDansDefausse = len(partie["defausse"])
    nbCartesCachees = 0

    for colonne in partie["colonnes"]:
        if len(colonne["cachees"]) > 0:
            nbCartesCachees += len(colonne["cachees"])


    # Colonne -> fondation
    for nbCachees in range(6, -1, -1):
        for i in range(len(partie["colonnes"])):
            visibles = partie["colonnes"][i]["visibles"]

            cachees = partie["colonnes"][i]["cachees"]
            if len(cachees) == nbCachees and len(visibles) > 0:
                carte = visibles[-1]
                numero = trouverFondation(carte, partie["fondations"])

                if numero is not None:
                    nomFondation = "f" + str(numero + 1)

                    # Si c'est un coup gagnant
                    if nbCarteDansPioche == 0 and nbCarteDansDefausse == 0 and nbCartesCachees == 1 and len(cachees) == 1 and len(visibles) == 1:
                        coupPropose = "★ Coup gagnant : "+ carteEnTexte(carte) + " (colonne "+ str(i+1) + ") " + "-> fondation " + nomFondation + " : range une carte en fondation"
                        coupPropose += "  -> tapez : d " + carteEnSaisie(carte) + " " + nomFondation
                        coups.insert(0, coupPropose)

                    else :
                        coupPropose = carteEnTexte(carte) + " (Colonne " + str(i+1) +") " + "-> fondation " + nomFondation + " : range une carte en fondation"
                        coupPropose += "  -> tapez : d " + carteEnSaisie(carte) + " " + nomFondation
                        coups.append(coupPropose)

    # Défausse -> fondation
    if len(partie["defausse"]) > 0:
        carte = partie["defausse"][-1]
        numero = trouverFondation(carte, partie["fondations"])

        if numero is not None:
            nomFondation = "f" + str(numero + 1)

            # Si c'est un coup gagnant
            if nbCartesCachees == 0 and nbCarteDansDefausse == 1 and nbCarteDansPioche == 0:
                coupPropose = "★ Coup gagnant : "+ carteEnTexte(carte) + " (défausse) -> fondation " + nomFondation + " : range une carte en fondation"
                coupPropose += "  -> tapez : d " + carteEnSaisie(carte) + " " + nomFondation
                coups.insert(0, coupPropose)

            else:
                coupPropose = carteEnTexte(carte) + " (défausse) -> fondation " + nomFondation + " : range une carte en fondation"
                coupPropose += "  -> tapez : d " + carteEnSaisie(carte) + " " + nomFondation
                coups.append(coupPropose)

    # Colonne -> colonne
    for nbCachees in range(6, 0, -1):
        for i in range(len(partie["colonnes"])):
            visibles = partie["colonnes"][i]["visibles"]
            cachees = partie["colonnes"][i]["cachees"]
            
            if len(cachees) == nbCachees and len(visibles) > 0:
                carte = visibles[0]

        for k in range(len(partie["colonnes"])):
            visibles = partie["colonnes"][i]["visibles"]
            cachees = partie["colonnes"][i]["cachees"]

            if k != i:
                if peutPoserSurColonne(carte, partie["colonnes"][k]):
                    if nbCartesCachees == 1 and len(cachees) == 1:
                         coupPropose = "★ Coup gagnant : "+ carteEnTexte(carte) + " (colonne "+ str(i+1) + ") " + "-> colonne" + str(k+1) + " : retourne une carte caché"
                         coupPropose += "  -> tapez : d " + carteEnSaisie(carte) + " " + str(k+1)
                         coups.insert(0, coupPropose)

                    else :
                        coupPropose = carteEnTexte(carte) + " (colonne " + str(i+1) + ") -> colonne " + str(k+1) + " : retourne une carte cachée"
                        coupPropose += "  -> tapez : d " + carteEnSaisie(carte) + " " + str(k+1)
                        coups.append(coupPropose)

    for i in range(len(coups)):
        print(str(i + 1) + ". " + coups[i])

# Cette fonction crée les préréglages de difficulté
# Elle ne prend pas de paramètre et renvoie un dictionnaire
# Chaque difficulté correspond à des valeurs déjà choisies pour les paramètres
def creerDifficultes():
    difficultes = {
        "facile":    {"cartesPiochees": 1, "aideActive": True},
        "normal":    {"cartesPiochees": 3, "aideActive": True},
        "difficile": {"cartesPiochees": 3, "aideActive": False}
    }
    return difficultes


# Cette fonction retrouve le nom de la difficulté qui correspond aux paramètres actuels
# Elle prend en paramètre les paramètres (dictionnaire)
# Elle renvoie le nom de la difficulté, ou "personnalisée" si aucune ne correspond
def trouverDifficulte(parametres):
    difficultes = creerDifficultes()
    nom = "personnalisée"

    for d in difficultes:
        if difficultes[d]["cartesPiochees"] == parametres["cartesPiochees"] and difficultes[d]["aideActive"] == parametres["aideActive"]:
            nom = d

    return nom


# Cette procédure permet de choisir une difficulté
# Elle prend en paramètre les paramètres (dictionnaire) et les modifie directement
def choisirDifficulte(parametres):
    difficultes = creerDifficultes()
    noms = ["facile", "normal", "difficile"]

    print("1 - Facile    : 1 carte piochée, aide activée")
    print("2 - Normal    : 3 cartes piochées, aide activée")
    print("3 - Difficile : 3 cartes piochées, aide désactivée")

    reponse = input(" -> ").replace(" ", "")

    while reponse not in ("1", "2", "3"):
        print("Saisie incorrecte, tapez 1, 2 ou 3")
        reponse = input(" -> ").replace(" ", "")

    choisie = difficultes[noms[int(reponse) - 1]]

    # On modifie le dictionnaire existant (on ne le remplace pas)
    # pour que le changement soit visible dans menu()
    parametres["cartesPiochees"] = choisie["cartesPiochees"]
    parametres["aideActive"] = choisie["aideActive"]

# Cette procédure permet de changer les paramétres
# elle prend en paramétre le dictionnaire paramétres
def modifierParametres(parametres):
    retour = False

    print("========================== Paramètres ==========================")
    while not retour:

        if parametres["aideActive"]:
            etatAide = "activée"
        else:
            etatAide = "désactivée"

        print(f"Difficulté actuelle : {trouverDifficulte(parametres)}")
        print(f"1 - Activer ou désactiver l'aide aux coups possibles : {etatAide}")
        print(f"2 - Changer le nombre de cartes piochées (1 ou 3) : {parametres['cartesPiochees']}")
        print("3 - Choisir une difficulté (facile, normal, difficile)")
        print("4 - Retour au menu principal")

        reponse = input(" -> ").replace(" ", "")

        while reponse not in ("1", "2", "3", "4"):
            print("Saisie incorrecte, tapez 1, 2, 3 ou 4")
            reponse = input(" -> ").replace(" ", "")

        if reponse == "1":
            parametres["aideActive"] = not parametres["aideActive"]

        elif reponse == "2":
            if parametres["cartesPiochees"] == 1:
                parametres["cartesPiochees"] = 3
            else:
                parametres["cartesPiochees"] = 1

        elif reponse == "3":
            choisirDifficulte(parametres)

        else:
            retour = True

# -------------------
# Programme principal
# -------------------
menu()