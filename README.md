# AGBE FAMILY

Site web familial privé (Flask + PostgreSQL) : présentation de la famille,
histoire, patrimoine et événements, avec système de comptes membres.

## Structure du projet

```
agbe_family/
├── app.py                  # Point d'entrée (application factory)
├── config.py                # Lecture des variables d'environnement
├── extensions.py            # Instances SQLAlchemy / Flask-Login
├── models.py                 # Modèles : User, FamilyMember, Event, HeritageItem
├── seed.py                   # Script pour créer les tables + contenu d'exemple
├── requirements.txt
├── .env.example               # Modèle du fichier .env (à copier)
├── routes/
│   ├── auth.py                # Inscription / connexion / déconnexion
│   └── main.py                 # Pages du site
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── famille.html
│   ├── histoire.html
│   ├── patrimoine.html
│   ├── evenements.html
│   └── auth/
│       ├── login.html
│       └── inscription.html
└── static/
    ├── css/style.css
    ├── js/main.js
    └── img/
```

## 1. Installation locale

```bash
cd agbe_family
python -m venv venv
source venv/bin/activate      # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Créer la base de données (Neon ou Aiven)

### Option A — Neon (recommandé, gratuit pour démarrer)
1. Créez un compte sur https://neon.tech
2. Créez un nouveau projet → une base est créée automatiquement
3. Dans le dashboard, copiez la "Connection string" (elle commence par `postgresql://`)

### Option B — Aiven
1. Créez un compte sur https://aiven.io
2. Créez un service "PostgreSQL" (plan gratuit disponible)
3. Dans l'onglet "Overview" du service, copiez le "Service URI"

## 3. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Puis éditez `.env` et remplacez :
- `SECRET_KEY` par une valeur aléatoire (voir commande dans le fichier)
- `DATABASE_URL` par l'URL copiée à l'étape 2

## 4. Initialiser la base de données

Cette commande crée toutes les tables et ajoute du contenu d'exemple
(membres, événements, patrimoine) que vous pourrez remplacer plus tard :

```bash
python seed.py
```

## 5. Lancer le site en local

```bash
python app.py
```

Le site est accessible sur http://127.0.0.1:5000

Créez votre premier compte via "Inscription", puis connectez-vous pour
accéder aux pages "La famille", "Notre histoire", "Notre patrimoine" et
"Événements" (protégées par connexion).

## 6. Remplacer le contenu d'exemple

- **Membres de la famille, événements, patrimoine** : modifiez directement
  les lignes dans `seed.py` puis relancez `python seed.py` (ou ajoutez plus
  tard une interface d'administration pour le faire depuis le site).
- **Texte de la page "Notre histoire"** : modifiez directement
  `templates/histoire.html`.
- **Photos** : déposez vos images dans `static/img/` et mettez à jour les
  `photo_url` correspondants (dans `seed.py` ou en base).

## 7. Déploiement (ex. Render, comme votre projet HITNA)

1. Poussez le projet sur GitHub (le `.env` ne sera pas inclus grâce au `.gitignore`)
2. Créez un "Web Service" sur Render, connecté au repo
3. Render build command : `pip install -r requirements.txt`
4. Render start command : `gunicorn app:app` (ajoutez `gunicorn` à `requirements.txt` avant de déployer)
5. Dans les variables d'environnement Render, ajoutez `SECRET_KEY` et `DATABASE_URL`
   (la même URL Neon/Aiven que celle utilisée en local)
6. Après le premier déploiement, exécutez une fois `python seed.py` via le
   shell Render (ou une tâche unique) pour créer les tables

## Prochaines étapes possibles

- Formulaire d'ajout/édition de membres, événements et patrimoine depuis le site (espace admin)
- Upload de vraies photos (au lieu d'URLs statiques)
- Arbre généalogique visuel
- Rôles utilisateurs (admin vs membre simple)
