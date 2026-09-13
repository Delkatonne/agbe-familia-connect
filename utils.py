"""Utilitaires partagés entre les différents blueprints."""
import base64

TYPES_IMAGE_AUTORISES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
TAILLE_IMAGE_MAX = 2 * 1024 * 1024  # 2 Mo


def traiter_photo(fichier):
    """
    Retourne (photo_data, erreur).
    - photo_data est None si aucun fichier n'a été fourni.
    - erreur est une chaîne à afficher si le fichier fourni est invalide.
    """
    if not fichier or not fichier.filename:
        return None, None

    if fichier.mimetype not in TYPES_IMAGE_AUTORISES:
        return None, "Format d'image non supporté (JPEG, PNG, WEBP ou GIF uniquement)."

    contenu = fichier.read()
    if len(contenu) > TAILLE_IMAGE_MAX:
        return None, "L'image dépasse la taille maximale autorisée (2 Mo)."

    encode = base64.b64encode(contenu).decode("utf-8")
    return f"data:{fichier.mimetype};base64,{encode}", None