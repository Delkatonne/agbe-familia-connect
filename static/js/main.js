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

function basculerMenu() {
    const nav = document.getElementById("nav-principale");
    const bouton = document.getElementById("bouton-menu");
    if (!nav || !bouton) return;

    const estOuvert = nav.classList.toggle("nav-ouverte");
    bouton.setAttribute("aria-expanded", estOuvert ? "true" : "false");
    bouton.textContent = estOuvert ? "✕" : "☰";
}

// Referme le menu automatiquement si on clique sur un lien (mobile)
document.addEventListener("DOMContentLoaded", function () {
    const nav = document.getElementById("nav-principale");
    if (!nav) return;
    nav.querySelectorAll("a").forEach(function (lien) {
        lien.addEventListener("click", function () {
            nav.classList.remove("nav-ouverte");
            const bouton = document.getElementById("bouton-menu");
            if (bouton) {
                bouton.setAttribute("aria-expanded", "false");
                bouton.textContent = "☰";
            }
        });
    });
});