# Audit des erreurs du détecteur relationnel E

Audit calculé sur les 27 questions finales existantes, avec les règles actuelles non modifiées. Les annotations de référence n’ont pas été changées.

## Matrice de confusion

Lignes = intention attendue; colonnes = intention prédite.

| Attendue \ Prédite | relation | information simple | indéterminée | Total |
|---|---:|---:|---:|---:|
| relation | 5 | 14 | 1 | 20 |
| simple_information | 0 | 4 | 0 | 4 |
| indeterminate | 0 | 0 | 3 | 3 |

## Erreurs par langue

| Langue | Erreurs / cas | Relations manquées comme simples | Relations indéterminées | Comparaisons manquées | Simples faussement relationnelles |
|---|---:|---:|---:|---:|---:|
| EN | 6 / 13 | 3 | 1 | 2 | 0 |
| FR | 4 / 7 | 2 | 0 | 2 | 0 |
| AR | 5 / 7 | 3 | 0 | 2 | 0 |

## Détail des erreurs

### f01 (EN) — relation_missed_as_simple
- Question : What might set off a fever when someone has an infection?
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.72).
- Relation/catégorie annotée : `causal` / `explicit`.
- Vérification : no marker matched for expected type causal; détections observées : concepts=['infection', 'fever'], types=[].

### f02 (FR) — relation_missed_as_simple
- Question : Une infection est-elle susceptible de déclencher de la fièvre ?
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.72).
- Relation/catégorie annotée : `causal` / `explicit`.
- Vérification : no marker matched for expected type causal; détections observées : concepts=['infection', 'fever'], types=[].

### f03 (AR) — relation_missed_as_simple
- Question : هل يمكن أن تؤدي العدوى إلى الحمى؟
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.55).
- Relation/catégorie annotée : `causal` / `explicit`.
- Vérification : concept aliases not matched: fever, infection; détections observées : concepts=[], types=['causal'].

### f04 (EN) — relation_missed_as_simple
- Question : Could being sick push glucose upward for a short time?
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.55).
- Relation/catégorie annotée : `causal` / `explicit`.
- Vérification : concept aliases not matched: glucose, illness; no marker matched for expected type causal; détections observées : concepts=[], types=[].

### f06 (AR) — relation_missed_as_simple
- Question : هل قد يرفع المرض مستوى السكر لفترة وجيزة؟
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.55).
- Relation/catégorie annotée : `causal` / `explicit`.
- Vérification : concept aliases not matched: glucose, illness; no marker matched for expected type causal; détections observées : concepts=[], types=[].

### f07 (EN) — comparison_missed
- Question : Which clues help tell influenza apart from an ordinary cold?
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.72).
- Relation/catégorie annotée : `comparison` / `explicit`.
- Vérification : no marker matched for expected type comparison; détections observées : concepts=['flu', 'cold'], types=[].

### f08 (FR) — comparison_missed
- Question : Par quels éléments la grippe se démarque-t-elle d’un rhume banal ?
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.72).
- Relation/catégorie annotée : `comparison` / `explicit`.
- Vérification : no marker matched for expected type comparison; détections observées : concepts=['flu', 'cold'], types=[].

### f09 (AR) — comparison_missed
- Question : ما العلامات التي تميز الإنفلونزا عن الزكام العادي؟
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.55).
- Relation/catégorie annotée : `comparison` / `explicit`.
- Vérification : concept aliases not matched: cold, flu; no marker matched for expected type comparison; détections observées : concepts=[], types=[].

### f10 (EN) — relation_abstained
- Question : Is unusual thirst one of the things diabetes can cause?
- Attendu : `relation`; prédit : `indeterminate` (type=causal, profil=None, confiance=0.40).
- Relation/catégorie annotée : `association` / `explicit`.
- Vérification : no marker matched for expected type association; détections observées : concepts=['diabetes', 'thirst'], types=['causal'].

### f11 (FR) — relation_missed_as_simple
- Question : La soif inhabituelle peut-elle accompagner le diabète ?
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.72).
- Relation/catégorie annotée : `association` / `explicit`.
- Vérification : no marker matched for expected type association; détections observées : concepts=['diabetes', 'thirst'], types=[].

### f12 (AR) — relation_missed_as_simple
- Question : هل يمكن أن يكون العطش الزائد من علامات السكري؟
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.72).
- Relation/catégorie annotée : `association` / `explicit`.
- Vérification : concept aliases not matched: thirst; no marker matched for expected type association; détections observées : concepts=['diabetes'], types=[].

### f16 (EN) — relation_missed_as_simple
- Question : Might blood pressure influence someone's glucose readings?
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.72).
- Relation/catégorie annotée : `causal` / `none`.
- Vérification : concept aliases not matched: glucose; détections observées : concepts=['pressure'], types=['causal'].

### f18 (FR) — comparison_missed
- Question : La grippe et la déshydratation donnent-elles des symptômes comparables ?
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.72).
- Relation/catégorie annotée : `comparison` / `context`.
- Vérification : no marker matched for expected type comparison; détections observées : concepts=['flu', 'dehydration'], types=[].

### f19 (EN) — comparison_missed
- Question : Are the warning signs of flu interchangeable with those of dehydration?
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.72).
- Relation/catégorie annotée : `comparison` / `context`.
- Vérification : no marker matched for expected type comparison; détections observées : concepts=['flu', 'dehydration'], types=[].

### f20 (AR) — comparison_missed
- Question : هل تتشابه أعراض الإنفلونزا والجفاف؟
- Attendu : `relation`; prédit : `simple_information` (type=None, profil=None, confiance=0.55).
- Relation/catégorie annotée : `comparison` / `context`.
- Vérification : concept aliases not matched: dehydration, flu; no marker matched for expected type comparison; détections observées : concepts=[], types=[].

## Cas f10 : annotation ambiguë à conserver et comparer séparément

L’annotation originale reste `relation/association`, profil `association_diabetes_thirst`, preuve explicite, document 32. La formulation anglaise « can cause » autorise aussi une lecture causale; la fiche 32 décrit la soif comme symptôme possible, ce qui n’établit pas à elle seule un mécanisme causal.

Une annotation alternative raisonnable est `relation/causal`, avec `preuve suffisante = non établie par le corpus`, document 32 comme contexte partiel uniquement et réponse attendue : ne pas affirmer la causalité; signaler la limite des sources. Cette annotation ne signifie pas que la causalité est médicalement fausse. Sa validation nécessite une source clinique fiable établissant le lien, son sens et ses conditions (par exemple hyperglycémie/polydipsie), puis une revue par une personne qualifiée.

Le détecteur retourne `indeterminate` pour f10 car le marqueur causal produit un type sans profil diabetes-thirst correspondant. Cela constitue un désaccord entre l’annotation actuelle et la taxonomie du détecteur, pas une preuve pour l’une ou l’autre annotation.

## Portée

Le benchmark final actuel est petit, composé pendant le même travail que le détecteur et réutilise les concepts/profils de la base et du benchmark historique. Ses questions sont lexicalement distinctes du développement, mais le jeu n’a pas été aveugle. Les chiffres arabes portent sur des phrases Unicode valides; la console Windows peut afficher ces caractères de façon trompeuse.
