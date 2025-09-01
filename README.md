# 🥳 Discord Bump Bot — By **El Titano**

**Automatise un `/bump` toutes les 2h**, via Selenium & Chrome.
Interface terminal **claire**, **pédagogique**, avec **session persistante** (profil Chrome dédié) et **gestion automatique** de l’écran “**Application Discord détectée** → Continuer dans le navigateur”.

---

## ⚡️ Installation & Mise en route (le plus simple possible)

### 1) Prérequis

* **Windows / macOS / Linux**
* **Google Chrome** installé (version récente)
* **Python 3.9+** installé

  * Windows : [python.org](https://www.python.org/downloads/) → cocher *Add Python to PATH* à l’installation.
* Accès à Internet pour installer la dépendance `selenium`.

### 2) Télécharger le projet

* Télécharge le fichier .zip et decompresse le.

### 3) Installer la dépendance

Dans le **terminal** ouvert dans le dossier du script :

```bash
pip install -r requirements.txt
```

> Pas de `chromedriver` à installer à la main : **Selenium Manager** s’en charge automatiquement 💫

### 4) Lancer le bot

Toujours dans le dossier :

```bash
python discord_bump_bot.py
```

### 5) Configurer (1ère fois)

Dans le **menu** :

1. **Configurer**

   * Colle l’URL du **salon/fil** où tu bump (doit contenir `https://discord.com/channels/...`).
   * Choisis **Login** (`o`) pour te connecter une bonne fois pour toutes.
     ➜ Le bot ouvre `discord.com/login`. Connecte-toi normalement.
   * Le bot détecte ton panneau utilisateur (ton pseudo) et **sauvegarde la session** :

     * **Profil Chrome dédié** (`./chrome_profile`) ✅ *La méthode la plus fiable*
     * **Cookies** (`cookies.pkl`) en **secours**
   * L’URL + le pseudo sont enregistrés dans `config.json`.

2. **Lancer**

   * Donne une **heure de départ** au format 24h (`21:30`) ou tape **`now` / `maintenant`** pour démarrer **tout de suite**.
   * À l’heure dite :

     * Le bot ouvre l’URL du salon, **trouve la zone de texte**, envoie :

       * `/bump` + **Entrée x2**
       * puis : `Bot made with <3 by El Titano` + **Entrée**
     * Il **attend 2h01** (compte à rebours **en direct** ⏳) et recommence en boucle 🔁.

> **Stopper** : `Ctrl + C` dans le terminal.

---

## ✨ Ce que fait ce bot (et pourquoi il est cool)

* **Menu ultra simple** : 1) Configurer, 2) Lancer, 3) Explications, 4) Quitter
* **Session persistante** via **profil Chrome** → tu ne te reconnectes **plus** à chaque lancement
* **Cookies** sauvegardés en **fallback** si jamais
* **Détection automatique** du bouton **“Continuer dans le navigateur”** (FR/EN)
* **Attente planifiée** avec **compte à rebours** lisible
* **Logs ChromeDriver masqués** → terminal propre (pas de “DevTools listening…”)
* **Messages d’erreur pédagogiques** + contact **@el\_titano**

---

## 📂 Arborescence (une fois lancé)

```
discord-bump-bot/
├─ discord_bump_bot.py         # le script principal
├─ requirements.txt            # (optionnel) selenium>=4.20.0
├─ config.json                 # URL + pseudo détecté (créé automatiquement)
├─ cookies.pkl                 # cookies de secours (créé automatiquement)
└─ chrome_profile/             # PROFIL CHROME (session persistante ✅)
   └─ ...                      # ne pas modifier manuellement
```
---

## 🧰 Dépannage (FAQ + check-list)

### “Je dois encore me reconnecter…”

* Assure-toi que le dossier `chrome_profile/` est **créé** dans le même dossier que le script.
* Lance **1) Configurer** → **Login** (o).
* Si ça bugge après une mise à jour Chrome, **ferme tout**, supprime le dossier `chrome_profile/` (⚠️ tu perds la session), relance **Config** + **Login**.
* Évite d’ouvrir **en même temps** la même session Chrome “normale” qui pourrait écraser certaines infos.

### “J’ai un écran ‘Application Discord détectée’”

* Le bot **clique automatiquement** “Continuer dans le navigateur”.
  Si tu le vois encore, **attends 2–3 secondes**, ou clique **manuellement** une fois, puis relaisse faire.

### “Textbox introuvable / rien ne s’écrit”

* Vérifie que tu es bien sur un **salon texte** ou un **thread** où l’envoi est possible.
* Ton rôle a-t-il le droit d’écrire dans ce salon ?
* Réseau lent → ajoute 0.2–0.5 s dans les `time.sleep()` si besoin.

### “Ça n’envoie pas /bump”

* Assure-toi que le **bot de bump** (ex : Disboard) est **présent** et **actif** sur le serveur.
* Disboard **limite** le bump : **toutes les 2h** → on envoie toutes **2h01** pour être safe.

### “La fenêtre se ferme toute seule”

* Un crash Selenium ? Relance le script.
* Chrome bloqué par antivirus ? Ajoute une exception.

### “Le PC passe en veille…”

* Désactive la **veille automatique** pendant l’exécution (Options d’alimentation → Jamais).

---

## 🧱 Limitations connues

* **Mises à jour Discord** : les attributs HTML peuvent changer. J’ai choisi des sélecteurs **stables** (ARIA & roles), mais si Discord modifie l’éditeur, il faudra adapter.
* **Droits d’écriture** requis dans le salon ciblé.
* **PC doit rester allumé** et **Chrome ouvert**.

---

## 🔒 Éthique & responsabilité

* **Respecte les règles** de ton serveur et les **Conditions d’utilisation** de Discord.
  L’automatisation n’est pas autorisée partout. Utilise ce script **à tes risques**, pour un usage **personnel** et **raisonnable**.
* Ne spamme pas. Ce bot est conçu pour un **/bump toutes les 2h** (pratique courante avec Disboard).

---

## 🤝 Support & Contact

* Un bug, une idée, un merci ?
  **Discord : `@el_titano`**

