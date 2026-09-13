console.log("AGBE FAMILY est chargé !");

function basculerVisibiliteMotDePasse(champId, bouton) {
    const champ = document.getElementById(champId);
    if (!champ) return;

    if (champ.type === "password") {
        champ.type = "text";
        bouton.textContent = "🙈";
        bouton.setAttribute("aria-label", "Masquer le mot de passe");
    } else {
        champ.type = "password";
        bouton.textContent = "👁";
        bouton.setAttribute("aria-label", "Afficher le mot de passe");
    }
}