# ------------
# Importations
# ------------
import random
import json   
import os 

# ---------------
# Sous-programmes
# ---------------

# Ce sous programme est une procédure qui va demander à l'utilisateur
# si il faut lancer une nouvelle partie accéder au paramétres ou quitter le jeu. 
# c'est le sous programme qui sera appeller au début de notre programme.
def menu():
    parametres = {"aide": True, "nbCartesPiochees": 1}
    quitter = False

    print("========================== Bienvenue dans le jeu de solitaire !  ==========================")

    while not quitter:
        print("1 - Nouvelle partie")
        print("2 - Reprendre la partie sauvegardée")
        print("3 - Accéder aux paramètres")
        print("4 - Quitter le jeu")
        reponse = input(" -> ").replace(" ", "")

        while reponse not in ("1", "2", "3", "4"):
            print("Saisie incorrecte, tapez 1, 2, 3 ou 4")
            reponse = input(" -> ").replace(" ", "")

        if reponse == "1":
            print("========================== Lancement d'une nouvelle partie ==========================")
            partie = initialisationPartie(parametres)
            jouerPartie(partie)

        elif reponse == "2":
            partie = chargerPartie()
            if partie is None:
                print("Aucune partie sauvegardée.")
            else:
                print("========================== Reprise de la partie ==========================")
                jouerPartie(partie)

        elif reponse == "3":
            menuParametres(parametres)

        else:
            print("========================== Au revoir ! ==========================")
            quitter = True

# Affiche les paramètres actuels et permet au joueur de les modifier
# Le dictionnaire parametres est modifié directement
def menuParametres(parametres):
    retour = False

    while not retour:
        print("========================== Paramètres ==========================")
        if parametres["aide"]:
            etatAide = "activée"
        else:
            etatAide = "désactivée"
        print(f"1 - Activer ou désactiver l'aide au coups possibles : {etatAide}")
        print(f"2 - Changer le nombre de cartes piochés ( 1 ou 3 ) : {parametres['nbCartesPiochees']}")
        print("3 - Retour au menu principal")

        reponse = input(" -> ")
        reponse = reponse.replace(" ", "")
        while reponse not in ("1", "2", "3"):
            print("Saisie incorrecte, tapez 1, 2 ou 3")
            reponse = input(" -> ")
            reponse = reponse.replace(" ", "")

        if reponse == "1":
            parametres["aide"] = not parametres["aide"]
        elif reponse == "2":
            if parametres["nbCartesPiochees"] == 1:
                parametres["nbCartesPiochees"] = 3
            else:
                parametres["nbCartesPiochees"] = 1
        else:
            retour = True

# Crée une nouvelle partie : paquet mélangé, colonnes distribuées, pioche
# Renvoie un dictionnaire contenant tous les éléments du jeu
def initialisationPartie(parametres):

    familles = ["coeur", "carreau", "trefle", "pique"]
    paquet = []
    for famille in familles:
        for valeur in range(1, 14):
            paquet.append((valeur, famille))

    random.shuffle(paquet)

    colonnes = []
    for i in range(7):
        cachees = []
        for j in range(i):
            cachees.append(paquet.pop())
        visibles = [paquet.pop()]
        colonnes.append({"cachees": cachees, "visibles": visibles})

    partie = {
        "pioche": paquet,
        "defausse": [],
        "fondations": {"coeur": [], "carreau": [], "trefle": [], "pique": []},
        "colonnes": colonnes,
        "parametres": parametres.copy(),
        "nbCoups": 0
    }

    return partie

# Renvoie la liste des cartes pouvant aller en fondation
# Chaque élément est un tuple (source, carte) :
# source vaut "d" pour la défausse, ou le numéro de colonne (1 à 7)
def listerCoupsFondation(partie):
    coups = []

    # Dessus de la défausse
    if len(partie["defausse"]) > 0:
        carte = partie["defausse"][-1]
        if peutAllerEnFondation(partie, carte):
            coups.append(("d", carte))

    # Dernière carte visible de chaque colonne
    for i in range(7):
        visibles = partie["colonnes"][i]["visibles"]
        if len(visibles) > 0:
            carte = visibles[-1]
            if peutAllerEnFondation(partie, carte):
                coups.append((i + 1, carte))

    return coups

# Renvoie une carte sous forme de texte, par exemple "Dame♥"
def carteEnTexte(carte):
    noms = {1: "As", 11: "Valet", 12: "Dame", 13: "Roi"}
    symboles = {"coeur": "♥", "carreau": "♦", "trefle": "♣", "pique": "♠"}
    valeur = noms.get(carte[0], str(carte[0]))
    return valeur + symboles[carte[1]]


# Affiche les 7 colonnes : les cartes cachées en [##], puis les visibles
def afficherColonnes(partie):
    for i in range(7):
        colonne = partie["colonnes"][i]
        texte = ""
        for carte in colonne["cachees"]:
            texte += "[##] "
        for carte in colonne["visibles"]:
            texte += "[" + carteEnTexte(carte) + "] "
        print(f"Colonne {i + 1} : {texte}")

# Affiche les quatre fondations : la carte du dessus, ou un emplacement vide
def afficherFondations(partie):
    texte = ""
    for famille in partie["fondations"]:
        pile = partie["fondations"][famille]
        if len(pile) == 0:
            texte += "[  ] "
        else:
            texte += "[" + carteEnTexte(pile[-1]) + "] "
    print(f"Fondations : {texte}")

# Cette fonction renvoie True si la carte peut être posée sur sa fondation
def peutAllerEnFondation(partie, carte):
    pile = partie["fondations"][carte[1]]
    return carte[0] == len(pile) + 1

# Affiche les cartes pouvant aller en fondation, demande au joueur
# laquelle déplacer, puis effectue le déplacement
# il s'agit de la fonction appelé quand l'aide est active
def choisirCoupFondation(partie):
    coups = listerCoupsFondation(partie)

    if len(coups) == 0:
        print("Aucune carte ne peut aller en fondation pour le moment.")
        return

    # Affichage numéroté
    print("Cartes pouvant aller en fondation :")
    for i in range(len(coups)):
        source = coups[i][0]
        carte = coups[i][1]
        if source == "d":
            provenance = "défausse"
        else:
            provenance = f"colonne {source}"
        print(f"  {i + 1} - {carteEnTexte(carte)} ({provenance})")

    # Choix du joueur, redemandé tant qu'il n'est pas valide
    choix = input("Votre choix -> ")
    choix = choix.replace(" ", "")
    while not choix.isdigit() or int(choix) < 1 or int(choix) > len(coups):
        print(f"Saisie incorrecte, tapez un nombre entre 1 et {len(coups)}")
        choix = input("Votre choix -> ")
        choix = choix.replace(" ", "")

    # Déplacement
    source = coups[int(choix) - 1][0]
    envoyerVersFondation(partie, source)

# Demande au joueur d'où vient la carte à envoyer en fondation
# (défausse ou colonne), sans lui indiquer les coups possibles
def choisirSourceFondation(partie):
    source = input("Source (d pour la défausse, 1 à 7 pour une colonne) -> ")
    source = source.replace(" ", "")
    while source not in ("d", "1", "2", "3", "4", "5", "6", "7"):
        print("Saisie incorrecte, tapez d ou un nombre entre 1 et 7")
        source = input("Source -> ")
        source = source.replace(" ", "")

    if not envoyerVersFondation(partie, source):
        input("Appuyez sur Entrée pour continuer...")

# Déplace une carte de la source (défausse ou colonne) vers sa fondation
# Renvoie True si le déplacement a été fait, False sinon
def envoyerVersFondation(partie, source):

    # On récupère la liste d'où vient la carte
    if source == "d":
        pileSource = partie["defausse"]
    else:
        colonne = partie["colonnes"][int(source) - 1]
        pileSource = colonne["visibles"]

    if len(pileSource) == 0:
        print("Il n'y a pas de carte à déplacer ici.")
        return False

    carte = pileSource[-1]
    if not peutAllerEnFondation(partie, carte):
        print(f"Le {carteEnTexte(carte)} ne peut pas aller sur sa fondation.")
        return False

    # Déplacement
    pileSource.pop()
    partie["fondations"][carte[1]].append(carte)

    # Si la colonne n'a plus de carte visible, on retourne une carte cachée
    if source != "d" and len(colonne["visibles"]) == 0 and len(colonne["cachees"]) > 0:
        colonne["visibles"].append(colonne["cachees"].pop())

    partie["nbCoups"] += 1

    return True

# Retourne des cartes de la pioche vers la défausse, selon le paramètre
# nbCartesPiochees. Si la pioche est vide, la défausse est remise dans la pioche.
# Renvoie True si une action a été faite, False sinon
def piocher(partie):
    pioche = partie["pioche"]
    defausse = partie["defausse"]

    if len(pioche) == 0:
        if len(defausse) == 0:
            print("La pioche et la défausse sont vides.")
            return False
        # On remet la défausse dans la pioche, dans l'ordre inverse
        partie["pioche"] = defausse[::-1]
        partie["defausse"] = []
        print("La défausse a été remise dans la pioche.")
    else:
        nb = partie["parametres"]["nbCartesPiochees"]
        i = 0
        while i < nb and len(pioche) > 0:
            defausse.append(pioche.pop())
            i += 1

    partie["nbCoups"] += 1
    return True

# Affiche le nombre de cartes de la pioche et la carte du dessus de la défausse
def afficherPiocheDefausse(partie):
    if len(partie["defausse"]) == 0:
        dessus = "[  ]"
    else:
        dessus = "[" + carteEnTexte(partie["defausse"][-1]) + "]"
    print(f"Pioche : {len(partie['pioche'])} carte(s)   Défausse : {dessus}")

# Affiche les coups possibles du moment (utilisée si l'aide est activée)
def afficherCoupsPossibles(partie):
    print("========================== Coups possibles ==========================")
    coupsFondation = listerCoupsFondation(partie)
    coupsColonne = listerCoupsColonne(partie)
    coupsDefausse = listerCoupsDefausse(partie)

    if len(coupsFondation) == 0 and len(coupsColonne) == 0 and len(coupsDefausse) == 0:
        print("Aucun coup disponible pour l'instant, essayez de piocher !")
        return

    for coup in coupsFondation:
        source = coup[0]
        carte = coup[1]
        if source == "d":
            provenance = "défausse"
        else:
            provenance = f"colonne {source}"
        print(f"- {carteEnTexte(carte)} ({provenance}) peut aller en fondation")

    for coup in coupsColonne:
        source, indice, dest, carte = coup
        print(f"- {texteSuite(partie, source, indice)} peut aller de la colonne {source} à la colonne {dest}")

    for dest in coupsDefausse:
        carte = partie["defausse"][-1]
        print(f"- {carteEnTexte(carte)} (défausse) peut aller sur la colonne {dest}")

# Renvoie "rouge" ou "noir" selon la famille de la carte
def couleur(carte):
    if carte[1] in ("coeur", "carreau"):
        return "rouge"
    return "noir"

# Renvoie True si la carte peut être posée en bas de la colonne
# (numeroColonne de 1 à 7)
def peutAllerSurColonne(partie, carte, numeroColonne):
    visibles = partie["colonnes"][numeroColonne - 1]["visibles"]

    # Colonne vide : seul un Roi est accepté
    if len(visibles) == 0:
        return carte[0] == 13

    derniere = visibles[-1]
    return derniere[0] == carte[0] + 1 and couleur(derniere) != couleur(carte)

# Déplace une carte (et toutes celles posées dessus) d'une colonne à une autre
# numeroSource et numeroDest : numéros de colonnes de 1 à 7
# indice : position de la carte dans les cartes visibles de la colonne source
# Renvoie True si le déplacement a été fait, False sinon
def deplacerVersColonne(partie, numeroSource, indice, numeroDest):
    if numeroSource == numeroDest:
        print("La colonne de départ et d'arrivée sont les mêmes.")
        return False

    colonneSource = partie["colonnes"][numeroSource - 1]
    visibles = colonneSource["visibles"]

    if indice < 0 or indice >= len(visibles):
        print("Il n'y a pas de carte visible à cette position.")
        return False

    carte = visibles[indice]
    if not peutAllerSurColonne(partie, carte, numeroDest):
        print(f"Le {carteEnTexte(carte)} ne peut pas aller sur la colonne {numeroDest}.")
        return False

    # Déplacement de la suite
    suite = visibles[indice:]
    del visibles[indice:]
    partie["colonnes"][numeroDest - 1]["visibles"].extend(suite)

    # Si la colonne source n'a plus de carte visible, on retourne une carte cachée
    if len(visibles) == 0 and len(colonneSource["cachees"]) > 0:
        visibles.append(colonneSource["cachees"].pop())

    partie["nbCoups"] += 1
    return True

# Demande un nombre entier entre minimum et maximum, et redemande
# tant que la saisie n'est pas valide. Renvoie le nombre (int)
def demanderNombre(message, minimum, maximum):
    saisie = input(message).replace(" ", "")
    while not saisie.isdigit() or int(saisie) < minimum or int(saisie) > maximum:
        print(f"Saisie incorrecte, tapez un nombre entre {minimum} et {maximum}")
        saisie = input(message).replace(" ", "")
    return int(saisie)

# Demande au joueur la colonne de départ, la carte à prendre et la colonne
# d'arrivée, puis effectue le déplacement (version sans aide)
def choisirDeplacementColonne(partie):
    numeroSource = demanderNombre("Colonne de départ (1 à 7) -> ", 1, 7)
    visibles = partie["colonnes"][numeroSource - 1]["visibles"]

    if len(visibles) == 0:
        print("Cette colonne est vide.")
        input("Appuyez sur Entrée pour continuer...")
        return

    # Choix de la carte à prendre
    if len(visibles) == 1:
        indice = 0
    else:
        print("Cartes visibles de cette colonne :")
        for i in range(len(visibles)):
            print(f"  {i + 1} - {carteEnTexte(visibles[i])}")
        indice = demanderNombre("Carte à déplacer (avec celles posées dessus) -> ", 1, len(visibles)) - 1

    numeroDest = demanderNombre("Colonne d'arrivée (1 à 7) -> ", 1, 7)

    if not deplacerVersColonne(partie, numeroSource, indice, numeroDest):
        input("Appuyez sur Entrée pour continuer...")

# Renvoie la liste des déplacements possibles entre colonnes
# Chaque élément est un tuple (numeroSource, indice, numeroDest, carte)
def listerCoupsColonne(partie):
    coups = []

    for source in range(1, 8):
        colonne = partie["colonnes"][source - 1]
        visibles = colonne["visibles"]

        for indice in range(len(visibles)):
            carte = visibles[indice]

            # Un déplacement n'est utile que s'il libère quelque chose :
            # la carte doit être la première visible de sa colonne, et
            # il doit rester des cartes cachées dessous, ou la colonne
            # doit se vider sans que ce soit un Roi qui change de place
            utile = indice == 0 and (len(colonne["cachees"]) > 0 or carte[0] != 13)

            for dest in range(1, 8):
                if dest != source and utile and peutAllerSurColonne(partie, carte, dest):
                    coups.append((source, indice, dest, carte))

    return coups

# Affiche les déplacements possibles entre colonnes, demande au joueur
# lequel faire, puis l'effectue (version avec aide)
def choisirCoupColonne(partie):
    coups = listerCoupsColonne(partie)

    if len(coups) == 0:
        print("Aucun déplacement possible entre les colonnes.")
        input("Appuyez sur Entrée pour continuer...")
        return

    print("Déplacements possibles :")
    for i in range(len(coups)):
        source, indice, dest, carte = coups[i]
        print(f"  {i + 1} - {texteSuite(partie, source, indice)} : colonne {source} -> colonne {dest}")

    choix = demanderNombre("Votre choix -> ", 1, len(coups))
    source, indice, dest, carte = coups[choix - 1]
    deplacerVersColonne(partie, source, indice, dest)

# Déplace la carte du dessus de la défausse vers une colonne (1 à 7)
# Renvoie True si le déplacement a été fait, False sinon
def defausseVersColonne(partie, numeroDest):
    defausse = partie["defausse"]

    if len(defausse) == 0:
        print("La défausse est vide.")
        return False

    carte = defausse[-1]
    if not peutAllerSurColonne(partie, carte, numeroDest):
        print(f"Le {carteEnTexte(carte)} ne peut pas aller sur la colonne {numeroDest}.")
        return False

    defausse.pop()
    partie["colonnes"][numeroDest - 1]["visibles"].append(carte)

    partie["nbCoups"] += 1
    return True

# Renvoie la liste des numéros de colonnes (1 à 7) où la carte
# du dessus de la défausse peut être posée
def listerCoupsDefausse(partie):
    coups = []
    if len(partie["defausse"]) > 0:
        carte = partie["defausse"][-1]
        for dest in range(1, 8):
            if peutAllerSurColonne(partie, carte, dest):
                coups.append(dest)
    return coups

# Fait choisir au joueur la colonne où poser la carte de la défausse
# Avec l'aide, seules les colonnes possibles sont proposées
def choisirDefausseVersColonne(partie):
    if len(partie["defausse"]) == 0:
        print("La défausse est vide.")
        input("Appuyez sur Entrée pour continuer...")
        return

    carte = partie["defausse"][-1]

    if partie["parametres"]["aide"]:
        coups = listerCoupsDefausse(partie)
        if len(coups) == 0:
            print(f"Le {carteEnTexte(carte)} ne peut aller sur aucune colonne.")
            input("Appuyez sur Entrée pour continuer...")
            return
        print(f"Colonnes possibles pour le {carteEnTexte(carte)} :")
        for i in range(len(coups)):
            print(f"  {i + 1} - colonne {coups[i]}")
        choix = demanderNombre("Votre choix -> ", 1, len(coups))
        defausseVersColonne(partie, coups[choix - 1])
    else:
        numeroDest = demanderNombre("Colonne d'arrivée (1 à 7) -> ", 1, 7)
        if not defausseVersColonne(partie, numeroDest):
            input("Appuyez sur Entrée pour continuer...")

# Renvoie le texte décrivant les cartes déplacées depuis une colonne,
# par exemple "Roi♠" ou "Roi♠ et 2 carte(s) posée(s) dessus"
def texteSuite(partie, source, indice):
    visibles = partie["colonnes"][source - 1]["visibles"]
    carte = visibles[indice]
    nbCartes = len(visibles) - indice

    if nbCartes > 1:
        return f"{carteEnTexte(carte)} et {nbCartes - 1} carte(s) posée(s) dessus"
    return carteEnTexte(carte)

# Enregistre la partie en cours dans le fichier sauvegarde.json
# (une seule sauvegarde : une nouvelle sauvegarde remplace l'ancienne)
def sauvegarderPartie(partie):
    with open("sauvegarde.json", "w") as fichier:
        json.dump(partie, fichier)
    print("Partie sauvegardée.")

# Transforme une liste de cartes [[valeur, famille], ...] en liste de tuples
def cartesEnTuples(cartes):
    resultat = []
    for carte in cartes:
        resultat.append((carte[0], carte[1]))
    return resultat


# Charge la partie sauvegardée et la renvoie,
# ou renvoie None s'il n'y a pas de sauvegarde
def chargerPartie():
    if not os.path.exists("sauvegarde.json"):
        return None

    with open("sauvegarde.json", "r") as fichier:
        partie = json.load(fichier)

    # Reconversion des cartes en tuples
    partie["pioche"] = cartesEnTuples(partie["pioche"])
    partie["defausse"] = cartesEnTuples(partie["defausse"])
    for famille in partie["fondations"]:
        partie["fondations"][famille] = cartesEnTuples(partie["fondations"][famille])
    for colonne in partie["colonnes"]:
        colonne["cachees"] = cartesEnTuples(colonne["cachees"])
        colonne["visibles"] = cartesEnTuples(colonne["visibles"])

    return partie

# Renvoie True si les quatre fondations sont complètes (13 cartes chacune)
def partieGagnee(partie):
    for famille in partie["fondations"]:
        if len(partie["fondations"][famille]) != 13:
            return False
    return True

# Cette sous fonction va prendre en paramétre partie.
# Elle va proposer toutes les actions possible au joueur et continura tant que ce dernier n'a pas abandonné ou qu'il 
# n'a pas gagné
def jouerPartie(partie):
    finie = False

    while not finie:
        print("========================== Etat du jeu ==========================")
        afficherPiocheDefausse(partie)
        afficherFondations(partie)
        afficherColonnes(partie)
        print(f"Nombre de coups : {partie['nbCoups']}")

        if partie["parametres"]["aide"]:
            afficherCoupsPossibles(partie)

        print("========================== Actions ==========================")
        print(f" 1 - Déplacer une carte vers la fondation")
        print(" 2 - Déplacer une carte d'une colonne à une autre")
        print(" 3 - Déplacer une carte de la défausse vers une colonne")
        print(f" 4 - Piocher")
        print(f"-1 -  Sauvegarder et quitter la partie")
        commande = input(" -> ")
        commande = commande.replace(" ", "")

        if commande == "-1":
            sauvegarderPartie(partie)
            finie = True

        elif commande == "1":
            if partie["parametres"]["aide"]:
                choisirCoupFondation(partie)
            else:
                choisirSourceFondation(partie)

        elif commande == "2":
            if partie["parametres"]["aide"]:
                choisirCoupColonne(partie)
            else:
                choisirDeplacementColonne(partie)

        elif commande == "3":
            choisirDefausseVersColonne(partie)
        
        elif commande == "4":
            if not piocher(partie):
                input("Appuyez sur Entrée pour continuer...")

        else:
            print("Commande inconnue")
            input("Appuyez sur Entrée pour continuer...")

        # Vérification de la victoire après chaque action
        if partieGagnee(partie):
            afficherFondations(partie)
            print("========================== Victoire ! ==========================")
            print(f"Bravo, vous avez gagné en {partie['nbCoups']} coups !")

            # La partie est terminée : on supprime la sauvegarde éventuelle
            if os.path.exists("sauvegarde.json"):
                os.remove("sauvegarde.json")

            input("Appuyez sur Entrée pour revenir au menu...")
            finie = True
            
# -------------------
# Programme principal
# -------------------

menu()

# partie = initialisationPartie({"aide": True, "nbCartesPiochees": 1})
# partie["colonnes"][0] = {"cachees": [], "visibles": [(9, "pique")]}
# print(peutAllerSurColonne(partie, (8, "coeur"), 1))    # True
# print(peutAllerSurColonne(partie, (8, "trefle"), 1))   # False : même couleur
# print(peutAllerSurColonne(partie, (7, "coeur"), 1))    # False : mauvaise valeur

# partie = initialisationPartie({"aide": True, "nbCartesPiochees": 1})
# partie["colonnes"][0] = {"cachees": [(5, "trefle")], "visibles": [(9, "pique"), (8, "coeur")]}
# partie["colonnes"][1] = {"cachees": [], "visibles": [(10, "carreau")]}
# print(deplacerVersColonne(partie, 1, 0, 2))   # True : 9♠ et 8♥ vont sur le 10♦
# afficherColonnes(partie)
