HELP = {
    "TITLE": f'***Liste des commandes disponibles :*** \n ',
    "ADD": "Ajoute/Modifie ton tag afin d'activer le bot",
    "ADD_WRONG": "Usage: !add <tag>",
    "REMOVE": "Supprime ton tag (fin c'est sad)",
    "CLAN": "Obtiens des infos sur le clan mon gars",
    "WAR": "Obtiens des infos sur la bagarre"
}

TAG = {
    "NO_PLAYER_FOUND": lambda mention, tag : f"{mention} fait un effort, aucun joueur trouvé avec ton tag \"{tag}\"",
    "SUCCESS": lambda mention, player : f"{mention} ton compte **{player['name']}** est sur la liste",
    "NO_TAG_FOUND": lambda mention : f"{mention} n'a pas de tag enregistré.",
    "TAG_REMOVED": lambda mention : f"Tag supprimé pour {mention}"
}

WAR = {
    "STATUS_NOT_IN_WAR": "Pas de guerre en cours, repose toi soldat",
    "STATUS_ENDED": "Guerre terminée",
    "IN_MATCHMAKING": "Recherche d'un adversaire en cours... On va les péter"
}