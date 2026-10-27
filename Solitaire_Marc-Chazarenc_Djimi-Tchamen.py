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
# CRÉATION DU JEU  (fait)
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
        "cartesPiochees": 1,   # nombre de cartes retournées à chaque pioche (1 ou 3)
        "aideActive": True     # le joueur a-t-il droit à l'aide ?
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
        "pioche": pioche,           # cartes restantes, faces cachées
        "defausse": [],             # cartes retournées depuis la pioche
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
# AFFICHAGE  (fait)
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

# Cette fonction transforme une carte (tuple) en texte pour chercher une carte
def texteEnCarte(texte):
    num = {"A" : 1,  "V": 11, "D":12, "R":13}
    texte = {"♥": "coeur", "♦": "carreau", "♣": "trefle", "♠": "pique"}

    num = text[0]
    couleur = carte[1]

    if valeur in noms:
        texteValeur = noms[valeur]
    else:
        texteValeur = str(valeur)

    return texteValeur + symboles[couleur]

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

    # --- Ligne du haut : pioche, défausse et fondations ---
    if len(partie["pioche"]) > 0:
        textePioche = "[XX]"
    else:
        textePioche = "[  ]"

    if len(partie["defausse"]) > 0:
        texteDefausse = carteEnCouleur(partie["defausse"][-1], 0)
    else:
        texteDefausse = "[  ]"

    ligneHaut = "Pioche: " + textePioche + "  Défausse: " + texteDefausse + "    Fondations: "
    for couleur in partie["fondations"]:
        fondation = partie["fondations"][couleur]
        if len(fondation) > 0:
            ligneHaut += carteEnCouleur(fondation[-1], largeur)
        else:
            ligneHaut += "[  ]".ljust(largeur)

    print(ligneHaut)
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
            print("Choix invalide, tapez un nombre entre 1 et 5.")


# Cette fonction fait tourner une partie jusqu'à ce que le joueur
# quitte ou gagne
# Elle prend en paramètre la partie (dictionnaire) et ne renvoie rien
def jouer(partie):
    enCours = True

    while enCours:
        print()
        afficherPartie(partie)
        print()
        print("Commandes : [p] piocher  [d] déplacer  [a] aide  [s] sauvegarder  [q] quitter")
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
            print("Commande inconnue.")

        if partieGagnee(partie):
            afficherPartie(partie)
            print("Bravo, vous avez gagné !")
            enCours = False


# =====================================================================
# FONCTIONNALITÉS À DÉVELOPPER
# Chaque fonction ci-dessous est un "bouchon" : elle existe pour que le
# programme tourne déjà, et sera remplie au point d'étape indiqué.
# =====================================================================

# À FAIRE - Point 1 : demander au joueur la source et la destination,
# vérifier que le déplacement est autorisé puis l'effectuer
def deplacer(partie):
    print("Quel carte faut il déplacer (pour coeur écrire co, pour carreau ca, pour pique, pi, pour tréfle tr.")
    carte = input(" -> ")
    carte = carte.replace(" " "")
    carte = carte.lower()




# À FAIRE - Point 2 : retourner une (ou trois) carte(s) de la pioche
# vers la défausse, et remettre la défausse dans la pioche si elle est vide
def piocher(partie):
    print("Pioche : fonctionnalité pas encore disponible.")


# À FAIRE - Point 2 : renvoyer True si les 4 fondations contiennent 13 cartes
def partieGagnee(partie):
    return False


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