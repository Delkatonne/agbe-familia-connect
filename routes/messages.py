from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import or_, and_

from extensions import db
from models import Message, User

messages_bp = Blueprint("messages", __name__, url_prefix="/messages")


@messages_bp.route("/")
@login_required
def index():
    envoyes = Message.query.filter_by(expediteur_id=current_user.id).all()
    recus = Message.query.filter_by(destinataire_id=current_user.id).all()

    ids_correspondants = set()
    for m in envoyes:
        ids_correspondants.add(m.destinataire_id)
    for m in recus:
        ids_correspondants.add(m.expediteur_id)

    conversations = []
    for user_id in ids_correspondants:
        correspondant = User.query.get(user_id)
        if not correspondant:
            continue
        dernier = (
            Message.query.filter(
                or_(
                    and_(Message.expediteur_id == current_user.id, Message.destinataire_id == user_id),
                    and_(Message.expediteur_id == user_id, Message.destinataire_id == current_user.id),
                )
            )
            .order_by(Message.date_envoi.desc())
            .first()
        )
        non_lus = Message.query.filter_by(
            expediteur_id=user_id, destinataire_id=current_user.id, lu=False
        ).count()
        conversations.append({
            "correspondant": correspondant,
            "dernier_message": dernier,
            "non_lus": non_lus,
        })

    conversations.sort(key=lambda c: c["dernier_message"].date_envoi, reverse=True)

    # Autres membres inscrits avec qui on n'a pas encore de conversation
    autres_membres = (
        User.query.filter(User.id != current_user.id, ~User.id.in_(ids_correspondants))
        .all()
    )

    return render_template(
        "messages/index.html", conversations=conversations, autres_membres=autres_membres
    )


@messages_bp.route("/<int:user_id>", methods=["GET", "POST"])
@login_required
def conversation(user_id):
    correspondant = User.query.get_or_404(user_id)
    if correspondant.id == current_user.id:
        abort(404)

    if request.method == "POST":
        contenu = request.form.get("contenu", "").strip()
        if contenu:
            message = Message(
                expediteur_id=current_user.id,
                destinataire_id=correspondant.id,
                contenu=contenu,
            )
            db.session.add(message)
            db.session.commit()
        return redirect(url_for("messages.conversation", user_id=user_id))

    messages_thread = (
        Message.query.filter(
            or_(
                and_(Message.expediteur_id == current_user.id, Message.destinataire_id == user_id),
                and_(Message.expediteur_id == user_id, Message.destinataire_id == current_user.id),
            )
        )
        .order_by(Message.date_envoi.asc())
        .all()
    )

    # Marquer comme lus les messages reçus dans cette conversation
    a_marquer = [m for m in messages_thread if m.destinataire_id == current_user.id and not m.lu]
    for m in a_marquer:
        m.lu = True
    if a_marquer:
        db.session.commit()

    return render_template(
        "messages/conversation.html", correspondant=correspondant, messages_thread=messages_thread
    )