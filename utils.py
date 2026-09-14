"""Utilitaires partagés entre les différents blueprints."""
import base64

TYPES_IMAGE_AUTORISES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
TAILLE_IMAGE_MAX = 2 * 1024 * 1024  # 2 Mo

TYPES_VIDEO_AUTORISES = {"video/mp4", "video/webm", "video/ogg", "video/quicktime"}
TAILLE_VIDEO_MAX = 20 * 1024 * 1024  # 20 Mo

TYPES_AUDIO_AUTORISES = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg", "audio/webm", "audio/x-m4a", "audio/mp4"}
TAILLE_AUDIO_MAX = 10 * 1024 * 1024  # 10 Mo


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


def traiter_media(fichier):
    """
    Comme traiter_photo, mais accepte aussi vidéo et audio (pour la galerie).
    Retourne (media_data, type_media, erreur) où type_media vaut
    "image", "video" ou "audio".
    """
    if not fichier or not fichier.filename:
        return None, None, None

    mimetype = fichier.mimetype

    if mimetype in TYPES_IMAGE_AUTORISES:
        type_media = "image"
        taille_max = TAILLE_IMAGE_MAX
        message_taille = "L'image dépasse la taille maximale autorisée (2 Mo)."
    elif mimetype in TYPES_VIDEO_AUTORISES:
        type_media = "video"
        taille_max = TAILLE_VIDEO_MAX
        message_taille = "La vidéo dépasse la taille maximale autorisée (20 Mo)."
    elif mimetype in TYPES_AUDIO_AUTORISES:
        type_media = "audio"
        taille_max = TAILLE_AUDIO_MAX
        message_taille = "L'audio dépasse la taille maximale autorisée (10 Mo)."
    else:
        return None, None, "Format non supporté (image, vidéo MP4/WEBM ou audio MP3/WAV/OGG uniquement)."

    contenu = fichier.read()
    if len(contenu) > taille_max:
        return None, None, message_taille

    encode = base64.b64encode(contenu).decode("utf-8")
    return f"data:{mimetype};base64,{encode}", type_media, None