# Protocole prospectif d’évaluation relationnelle indépendante

Le protocole et les seuils sont gelés dans `relation_independent_protocol.py` avant toute collecte de labels. Les 17 cas `FINAL_CANDIDATES` restent **hors métriques** jusqu’à validation indépendante. Aucun de ces cas ne doit servir à modifier le détecteur, ses alias, ses profils ou son seuil.

## État du jeu candidat

- 6 formulations de développement et 17 formulations finales; les familles sémantiques et les questions exactes sont disjointes entre ces deux partitions.
- EN, FR et AR sont présents. Les traductions FR/AR exigent une revue par des locuteurs compétents; la terminologie médicale arabe peut varier selon le registre et la région.
- Les familles finales sont medication→glucose, dehydration→fatigue, glucose→vision, flu↔COVID, anémie (information simple) et entités non précisées.
- Les paires finales n’apparaissent pas telles quelles dans le profil de concepts actuel. Il y a néanmoins du recouvrement de concepts et de documents : glucose/médicaments (notice 36), déshydratation (4), fatigue (10), grippe (1/5); COVID et anémie ne sont pas des sujets attestés dans le corpus identifié. Ces références sont à revérifier contre le snapshot exact avant annotation.
- Tous les champs de référence (`gold_intent`, IDs de preuve/contexte et niveau de preuve) sont `null` et leur statut est `needs_independent_clinical_and_language_validation`. Les formulations sont des candidats à annoter, pas des faits médicaux validés.
- Avant collecte : les propositions FR/AR lisibles et leurs chaînes brutes observées sont consignées dans `relation_candidate_restorations.json`. Les reconstitutions sont techniquement réversibles, mais aucune n'a reçu de validation linguistique ou médicale. Soumettre les propositions à des humains; ne pas les traiter comme validées ni compter leur score officiellement avant cela.

## Annotation et adjudication

1. Figer la version du corpus, les questions, le code A/D/E et le seuil 0,50 avant de révéler les questions finales aux évaluateurs.
2. Utiliser `relation_annotation_template.json`. Créer deux copies séparées par cas. Les annotateurs voient l'ID, la question exacte, la langue et le corpus figé, mais aucune sortie ou prédiction de A, D ou E. Conserver leurs fichiers séparément et horodater leur soumission avant tout calcul de prédiction.
3. Deux annotateurs travaillent indépendamment. Obtenir une revue médicale qualifiée pour la validation clinique et une revue linguistique compétente pour chaque langue; ne pas supposer que la compétence en anglais valide FR/AR. Un troisième arbitre les désaccords et consigne chaque décision. Sans expertise appropriée, laisser `needs_validation`.
4. Distinguer l'intention, le type et la direction de relation, et le niveau de preuve du corpus. Une cooccurrence ou deux documents séparés ne prouvent pas la relation. Affecter chaque document candidat à une seule catégorie : preuve de la relation, contexte partiel, ou hors sujet.
5. Utiliser `supported` si une source identifiée énonce la relation demandée avec ses nuances; `partial_context` si elle ne soutient que des concepts/faits isolés; `not_demonstrated` si aucune preuve suffisante n'est fournie. `not_demonstrated` ne signifie jamais que la relation médicale est fausse.
6. Garder les annotations, corrections et justifications versionnées. Ne pas exposer les prédictions avant les deux soumissions. Une référence est admissible aux métriques officielles seulement si deux évaluations sont soumises, les statuts médical et linguistique nécessaires sont validés, et l'accord est consigné ou arbitré.
7. Conserver développement pour les choix méthodologiques; exécuter le test final une seule fois après gel. Aucun réglage de paramètres à partir du score final.

## Métriques et seuils décidés à l’avance

Définitions complètes dans `relation_independent_protocol.py`. Comparer A, D (profil manuel oracle, référence expérimentale) et E sur exactement les mêmes questions validées. Rapporter séparément la classification d’intention et le retrieval, puis découper par langue, type de relation et niveau de preuve.

Seuils prospectifs minimaux pour considérer E : macro-F1 d’intention ≥ 0,80; rappel relationnel ≥ 0,85; précision relationnelle ≥ 0,90; rappel relationnel ≥ 0,75 dans chaque langue; faux positifs relationnels ≤ 0,05; faux rejets couverts ≤ 0,10; baisse de Recall@2 par rapport à A ≤ 0,02 et gain de Precision@2 ≥ 0,05. Ces seuils ne sont pas ajustés sur le jeu final actuel.

## Limites et statut

Le jeu final historique de 27 cas a été écrit pendant le même travail que E; il n’est pas aveugle, ses concepts recoupent le corpus et ses annotations nécessitent les vérifications consignées dans l’audit. Le nouveau jeu est un protocole préparé, **pas encore un benchmark médical indépendant scoré** : les résultats A/D/E sont volontairement différés jusqu’à adjudication. Aucune méthode expérimentale n’est branchée à Gemini ni à la production.

## États de publication et règles d'arrêt

- **Exploratoire actuel** : les 27 cas historiques et leurs métriques peuvent être reproduits à titre descriptif uniquement. Le script les étiquette `exploratory_historical_not_independent_confirmation`, indique `official_metrics: false` et ne compte aucun comme validé par ce protocole.
- **Développement** : les six candidats servent à tester l'annotation et, après gel de leurs références, à modifier les choix méthodologiques. Les scores sont publiés séparément, avec effectifs et statut; ils ne sont pas une confirmation indépendante.
- **Final indépendant** : les 17 candidats restent exclus tant que la double annotation, les validations et l'arbitrage ne sont pas terminés. Après gel de code, corpus, seuil, références et analyse, publier un seul rapport final. Toute modification après ouverture du final entraîne un nouveau jeu final.
- `official_cases()` applique un filtre fermé : un cas sans deux annotations soumises, validation médicale et linguistique, et état d'adjudication explicite est exclu. Une référence absente ne doit jamais être remplacée par la prédiction de E ou le profil oracle de D.
- Rapporter les effectifs validés par méthode, langue, type de relation et niveau de preuve. Les résultats de sous-groupes avec moins de 10 familles sémantiques sont descriptifs seulement; un résultat global avec moins de 30 familles est insuffisant pour une affirmation confirmatoire. Les variantes traduites d'une même famille ne gonflent pas l'effectif indépendant. Signaler les intervalles d'incertitude et les cellules vides; ne pas publier un taux sans son dénominateur.
- Séparer les trois objets du rapport : intention annotée, intention prédite par E et profil oracle manuel donné à D. D est une référence expérimentale, jamais une méthode déployée. Séparer aussi les listes de documents de preuve, de contexte partiel et hors sujet.

## Étapes manuelles restantes

1. Revoir les recommandations sans modifier automatiquement les questions dans `RELATION_CANDIDATE_AUDIT.md`.
2. Choisir des annotateurs médicaux et linguistiques qualifiés; si ce n'est pas possible, ne pas produire de gold médical.
3. Figer le corpus et les fichiers de questions, distribuer deux formulaires aveugles par cas, puis effectuer l'arbitrage documenté.
4. Ajouter uniquement les cas entièrement validés à un manifeste de références versionné. Vérifier les familles et les partitions avant de révéler les sorties A/D/E.
5. Exécuter le protocole gelé; publier les résultats exploratoires, développement et final dans des sections distinctes. N'ajuster aucun paramètre à partir des résultats finaux.
