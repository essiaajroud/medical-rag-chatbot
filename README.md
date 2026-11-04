# MediBot — Documentation technique du projet

**Version :** 1.0 — Documentation initiale  
**Type de projet :** Chatbot médical intelligent basé sur le RAG  
**Statut :** Prototype fonctionnel en phase de validation

---

## 1. Présentation générale

MediBot est un chatbot médical conçu pour fournir aux utilisateurs des informations générales sur la santé à partir d'une base documentaire médicale.

Le système repose sur une architecture RAG (*Retrieval-Augmented Generation*). Cette approche permet de rechercher des informations dans une base documentaire avant de générer une réponse avec un modèle de langage.

L'objectif principal est de limiter les réponses médicales non documentées et de fournir des réponses accompagnées de références médicales lorsque celles-ci sont disponibles.

MediBot ne remplace pas un médecin et ne doit pas être utilisé comme outil de diagnostic médical.

## 2. Architecture technique

### 2.1 Technologies utilisées

| Composant | Technologie | Rôle |
|---|---|---|
| Frontend | React | Interface utilisateur |
| Langage frontend | TypeScript | Typage et structuration du frontend |
| Outil frontend | Vite | Environnement de développement et compilation |
| Backend | Python | Logique applicative |
| API | FastAPI | Communication entre frontend et backend |
| Orchestration IA | LangGraph | Routage et organisation des étapes de traitement |
| Recherche vectorielle | FAISS | Recherche des documents pertinents |
| Embeddings | Sentence Transformers | Transformation des textes en vecteurs |
| Modèle d'embeddings | paraphrase-multilingual-MiniLM-L12-v2 | Représentation vectorielle multilingue |
| LLM | Gemini | Génération des réponses à partir du contexte |
| Format documentaire | JSON | Stockage des fiches médicales |

### 2.2 Architecture générale

Le système est organisé en deux parties principales :

- **Frontend :** permet à l'utilisateur de communiquer avec MediBot.
- **Backend :** traite les questions, effectue la recherche documentaire, organise le routage et génère les réponses.

Le fonctionnement général est le suivant :

1. L'utilisateur saisit une question dans l'interface React.
2. Le frontend envoie la question et l'historique conversationnel à l'API FastAPI.
3. Le backend transmet les informations au workflow LangGraph.
4. Le routeur analyse la question et détermine le chemin de traitement.
5. Si une recherche documentaire est appropriée, FAISS recherche les fiches médicales pertinentes.
6. Les documents retenus sont transmis au pipeline RAG.
7. Gemini génère une réponse à partir du contexte documentaire.
8. Le backend retourne la réponse et les sources disponibles.
9. Le frontend affiche le résultat dans la conversation.

### 2.3 Schéma fonctionnel

```text
                    UTILISATEUR
                         |
                         v
                FRONTEND REACT
                 + TypeScript
                         |
                         v
                  API FASTAPI
                      /ask
                         |
                         v
                 WORKFLOW LANGGRAPH
                         |
                         v
                  ROUTER NODE
                         |
       +-----------------+------------------+
       |                 |                  |
       v                 v                  v
   URGENCE          CLASSIFICATION       AUTRES CAS
       |                 |
       |          +------+-------+
       |          |              |
       |          v              v
       |         RAG          NO EVIDENCE
       |          |
       |          v
       |      FAISS SEARCH
       |          |
       |          v
       |    DOCUMENT FILTER
       |          |
       |          v
       |     RAG PIPELINE
       |          |
       |          v
       |        GEMINI
       |          |
       +----------+-------------------------+
                         |
                         v
                 RÉPONSE FINALE
                         |
                         v
                    FRONTEND
```

*Ce schéma représente le fonctionnement logique observé et défini dans le projet. Les connexions exactes entre tous les nœuds doivent être confirmées dans le code LangGraph.*

## 3. Organisation du backend

Le backend est organisé autour de plusieurs responsabilités.

### 3.1 Chargement des données

Le fichier documentaire utilisé est :

`backend/data/data_enriched_v3.json`

Le chargement est effectué dans `backend/app/main.py`, avec le loader situé dans :

`backend/app/data/loader.py`

Le loader utilise `json.load()` pour lire les fiches médicales.

Au démarrage, les données sont chargées et utilisées pour initialiser le moteur de recherche vectorielle.

### 3.2 Recherche vectorielle — FAISS

Le composant FAISS permet de retrouver les documents correspondant le mieux à une question.

Les embeddings sont calculés à partir des informations textuelles des fiches, notamment :

- La question.
- La réponse.
- Les mots-clés.
- Les questions associées.
- La catégorie.

Le modèle utilisé est :

`paraphrase-multilingual-MiniLM-L12-v2`

La recherche retourne les documents candidats accompagnés de scores de similarité.

Les seuils actuellement observés dans les logs sont :

- Seuil du routeur : `0.35`
- Seuil de sélection du contexte RAG : `0.35`

Ces seuils doivent être évalués sur un ensemble représentatif de questions avant d'être considérés comme définitifs.

### 3.3 Orchestration avec LangGraph

LangGraph organise les différentes étapes de traitement.

Les nœuds identifiés dans l'architecture actuelle comprennent :

- `router_node` : analyse la question et détermine le chemin de traitement.
- `rag_node` : traite les questions pouvant être résolues avec la base documentaire.
- `llm_node` : traite les cas généraux autorisés.
- `emergency_node` : gère les situations d'urgence.
- `out_of_scope_node` : traite les questions hors du domaine médical.
- `unclear_node` : demande une reformulation lorsque la question n'est pas comprise.
- `sources_request_node` : traite les demandes de références.
- `no_evidence_node` : indique que la base documentaire ne contient pas suffisamment d'informations.

Le système doit éviter de générer une réponse médicale non documentée lorsqu'aucune preuve suffisante n'est disponible.

### 3.4 Génération avec Gemini

Gemini est utilisé pour formuler une réponse à partir des documents sélectionnés par le pipeline RAG.

Le pipeline transmet les documents disponibles au modèle et récupère les identifiants des documents effectivement utilisés.

Les sources retournées sont limitées aux documents validés comme utilisés pour produire la réponse.

Cette distinction permet d'éviter de présenter comme référence une fiche qui aurait simplement été retrouvée par FAISS, mais qui n'aurait pas servi à générer la réponse.

## 4. Structure des données médicales

Chaque fiche médicale contient les informations suivantes :

| Champ | Description |
|---|---|
| `id` | Identifiant unique |
| `question` | Question médicale principale |
| `answer` | Réponse documentaire |
| `keywords` | Mots-clés médicaux et synonymes |
| `category` | Catégorie de la fiche |
| `severity` | Niveau de gravité associé |
| `related_questions` | Questions associées |
| `source_name` | Nom de la source médicale |
| `source_url` | URL de la référence |
| `reviewed_at` | Date de vérification |
| `language` | Langue de la fiche |

Exemple simplifié :

```json
{
  "id": 37,
  "question": "What are the symptoms of appendicitis?",
  "answer": "Appendicitis often starts with abdominal pain...",
  "keywords": [
    "appendicitis",
    "abdominal pain",
    "nausea"
  ],
  "category": "disease",
  "severity": "high",
  "related_questions": [
    "What causes appendicitis?"
  ],
  "source_name": "NHS",
  "source_url": "https://www.nhs.uk/conditions/appendicitis/",
  "reviewed_at": null,
  "language": "en"
}
```

## 5. Gestion de la conversation

Le backend reçoit également l'historique conversationnel.

Chaque message possède deux champs :

- `sender` : utilisateur ou bot.
- `message` : contenu du message.

Exemple :

```json
[
  {
    "sender": "user",
    "message": "What are the symptoms of appendicitis?"
  },
  {
    "sender": "bot",
    "message": "Appendicitis often starts with pain..."
  }
]
```

Le système utilise notamment l'historique pour résoudre les questions de suivi et déterminer le sujet précédemment abordé.

La résolution des questions de suivi doit être testée afin de garantir que la question actuelle n'est pas confondue avec un ancien sujet.

## 6. Tests déjà réalisés

Les résultats suivants sont issus des logs de test communiqués.

### Test 1 — Symptômes de l'appendicite

**Question :** What are the symptoms of appendicitis?

Résultats :

- Document retrouvé : ID 37.
- Score FAISS : `0.8396`.
- Document retenu par le filtre : ID 37.
- Document utilisé par Gemini : ID 37.
- Source retournée : NHS.

**Résultat :** Réussi.

### Test 2 — Causes de l'appendicite

**Question :** What causes appendicitis?

Résultats :

- Le workflow est entré dans `unclear_node`.
- Aucune recherche RAG n'a été effectuée.
- MediBot a demandé une reformulation et a proposé des sujets sans rapport direct avec la question.

**Résultat :** Échec fonctionnel à corriger.

Cause possible : la classification de l'intention ou la résolution de la question n'identifie pas correctement cette question médicale. Le code du routeur et du nœud de clarification doit être inspecté pour déterminer la cause exacte.

### Test 3 — Antibiotiques et rhume

**Question :** Can antibiotics cure a common cold?

Résultats :

- Document ID 18 retrouvé avec un score de `0.8100`.
- Document ID 3 retrouvé avec un score de `0.4625`.
- Documents retenus : ID 18 et ID 3.
- Document utilisé par Gemini : ID 18.
- Source retournée : CDC.

**Résultat :** Réussi.

### Test 4 — Signes d'AVC

**Question :** What are the warning signs of a stroke?

Résultats :

- Document ID 20 retrouvé avec un score de `0.8117`.
- Document ID 21 retrouvé avec un score de `0.4539`.
- Documents retenus : ID 20 et ID 21.
- Document utilisé par Gemini : ID 20.
- Source retournée : NHS.

**Résultat :** Réussi.

### Test 5 — Douleur thoracique sévère

**Question :** What should I do if I have severe chest pain?

Résultat observé :

MediBot a répondu que la douleur thoracique pouvait signaler une urgence, a recommandé d'appeler immédiatement les services d'urgence locaux et de ne pas conduire soi-même.

**Résultat :** Réponse d'urgence appropriée observée.

**Limite du test :** Les lignes de routage correspondantes ne sont pas présentes dans les logs fournis. Le déclenchement exact du nœud d'urgence reste donc à confirmer.

### Test 6 — Question hors domaine

**Question :** What is the capital of Tunisia?

Résultat :

MediBot a expliqué qu'il s'agissait d'un assistant d'information médicale et qu'il ne pouvait pas traiter ce sujet.

**Résultat :** Réussi.

## 7. État actuel du projet

Les éléments suivants sont fonctionnels selon les tests disponibles :

- Communication avec l'API FastAPI.
- Recherche vectorielle FAISS.
- Sélection des documents pertinents.
- Génération de réponses avec Gemini.
- Retour des sources utilisées.
- Réponse à certaines questions médicales.
- Gestion d'une question hors domaine.
- Réponse d'urgence observée pour une douleur thoracique.

Les éléments qui nécessitent encore des vérifications :

- Résolution des questions de suivi.
- Classification des intentions médicales.
- Cohérence des messages du nœud `unclear_node`.
- Détection et routage des urgences.
- Gestion des erreurs et des réponses sans preuve.
- Qualité générale des réponses sur un ensemble de questions plus large.

## 8. Problèmes identifiés et améliorations

### Problème 1 — Question de suivi sur l'appendicite

La question « What causes appendicitis? » n'a pas été traitée par le RAG, alors qu'elle concerne le même sujet médical que la question précédente.

Action :

- Examiner la fonction de résolution des questions de suivi.
- Examiner la classification des intentions.
- Vérifier les conditions qui conduisent à `unclear_node`.
- Ajouter une fiche documentaire sur les causes de l'appendicite uniquement si la base ne couvre pas suffisamment ce sujet.

### Problème 2 — Fiabilité du routage d'urgence

Action :

- Tester plusieurs formulations de douleur thoracique.
- Tester les signes d'AVC.
- Tester les difficultés respiratoires.
- Vérifier que le routage d'urgence intervient avant la recherche documentaire classique lorsque les critères d'urgence sont présents.

### Problème 3 — Avertissement AFC de Gemini

Les logs affichent un avertissement concernant l'utilisation de l'Automatic Function Calling avec `AsyncModels.generate_content`.

Cet avertissement n'a pas empêché les réponses testées de fonctionner.

Action :

- Garder ce point comme amélioration technique.
- Examiner la documentation de la version Gemini utilisée avant de modifier l'implémentation.
- Ne pas modifier le système simplement pour supprimer un avertissement sans vérifier les conséquences.

## 9. Prochaines étapes de développement

Ordre de travail proposé :

1. Corriger le problème de compréhension de « What causes appendicitis? ».
2. Tester la résolution des questions de suivi.
3. Réaliser une campagne complète de tests d'urgence.
4. Tester les questions médicales absentes de la base.
5. Évaluer la qualité des résultats FAISS.
6. Améliorer progressivement la base documentaire.
7. Tester les échanges frontend/backend.
8. Vérifier l'affichage des sources médicales.
9. Mesurer les performances du système.
10. Préparer une documentation utilisateur et une démonstration finale.

## 10. Commandes de lancement

### Backend

Depuis le dossier `backend` :

```bash
uvicorn app.main:app --reload
```

Le serveur est actuellement utilisé localement sur :

`http://127.0.0.1:8000`

### Frontend

Depuis le dossier du frontend :

```bash
npm install
npm run dev
```

L'adresse exacte du frontend dépend de la configuration Vite.

## 11. Conclusion

MediBot dispose d'une première architecture RAG fonctionnelle combinant React, FastAPI, LangGraph, FAISS, Sentence Transformers et Gemini.

Les tests montrent que le système peut retrouver une fiche médicale pertinente, transmettre le contexte au modèle de langage et retourner une réponse accompagnée de sa source.

La priorité actuelle n'est pas d'ajouter immédiatement de nouvelles fonctionnalités, mais de fiabiliser le routage, la compréhension des questions de suivi et la gestion des situations urgentes.

Cette documentation constitue une première référence technique. Elle devra être complétée après vérification de l'ensemble des fichiers du dépôt, notamment des routes API, du graphe LangGraph, du pipeline RAG et de la configuration du frontend.