# Dossier de revue humaine — candidats relationnels

Paquet expérimental aveugle. Les documents listés sont des pistes de vérification, pas des preuves. Aucune prédiction A/D/E n'est fournie. Les décisions et validations sont laissées vides.

## Procédure

1. Distribuer séparément les fichiers `relation_review_evaluator_1.json` et `_2.json`; chaque évaluateur soumet et fige son fichier avant tout échange.
2. Les évaluateurs vérifient compréhension, grammaire, sens, naturel et équivalence de la proposition avec le texte brut si récupérable. En l'absence d'original fiable, ils le notent au lieu de supposer l'équivalence.
3. Inspecter le contenu des documents du corpus avant de les classer. Une ID ou un titre ne prouve aucune relation.
4. Un tiers remplit `relation_review_adjudication.json` après réception des deux soumissions. Les désaccords et décisions restent traçables.
5. Aucun statut ne devient validé automatiquement. Ne pas calculer de métrique officielle avec ces formulaires.

## Fiches candidats

### d02 — fr — split development

- Brut corrompu : `La soif peut-elle accompagner le diabÃ¨te ?`
- Représentation échappée : `'La soif peut-elle accompagner le diab\xc3\xa8te ?'`
- Proposition : La soif peut-elle accompagner le diabète ?
- Type de relation du candidat : `association`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 32 — What are the common symptoms of diabetes?
- Incertitudes : Association wording: confirm it asks whether thirst can accompany diabetes, without implying diagnosis or certainty.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### d03 — ar — split development

- Brut corrompu : `ÙÙ ØªØªØºÙØ± Ø£Ø¹Ø±Ø§Ø¶ Ø§ÙØ¥ÙÙÙÙÙØ²Ø§ Ø¹Ù Ø§ÙØ²ÙØ§ÙØ`
- Représentation échappée : `'\xd9\x87\xd9\x84 \xd8\xaa\xd8\xaa\xd8\xba\xd9\x8a\xd8\xb1 \xd8\xa3\xd8\xb9\xd8\xb1\xd8\xa7\xd8\xb6 \xd8\xa7\xd9\x84\xd8\xa5\xd9\x86\xd9\x81\xd9\x84\xd9\x88\xd9\x86\xd8\xb2\xd8\xa7 \xd8\xb9\xd9\x86 \xd8\xa7\xd9\x84\xd8\xb2\xd9\x83\xd8\xa7\xd9\x85\xd8\x9f'`
- Proposition : هل تتغير أعراض الإنفلونزا عن الزكام؟
- Type de relation du candidat : `comparison`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 5 — How is the flu different from a common cold?
- Incertitudes : Arabic phrasing may read as symptoms changing relative to a cold rather than a natural comparison. Native Arabic adjudication required.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### d05 — fr — split development

- Brut corrompu : `Quels signes accompagnent la dÃ©shydratation ?`
- Représentation échappée : `'Quels signes accompagnent la d\xc3\xa9shydratation ?'`
- Proposition : Quels signes accompagnent la déshydratation ?
- Type de relation du candidat : `None`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 4 — What are the symptoms of dehydration?
- Incertitudes : Check the naturalness of the French wording and whether 'signes' is intended as symptoms/signs.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### d06 — ar — split development

- Brut corrompu : `ÙÙ ÙÙÙÙ Ø£Ù ÙØ±ÙØ¹ Ø§ÙÙØ±Ø¶ Ø§ÙØ³ÙØ± ÙØ¤ÙØªØ§Ø`
- Représentation échappée : `'\xd9\x87\xd9\x84 \xd9\x8a\xd9\x85\xd9\x83\xd9\x86 \xd8\xa3\xd9\x86 \xd9\x8a\xd8\xb1\xd9\x81\xd8\xb9 \xd8\xa7\xd9\x84\xd9\x85\xd8\xb1\xd8\xb6 \xd8\xa7\xd9\x84\xd8\xb3\xd9\x83\xd8\xb1 \xd9\x85\xd8\xa4\xd9\x82\xd8\xaa\xd8\xa7\xd8\x9f'`
- Proposition : هل يمكن أن يرفع المرض السكر مؤقتا؟
- Type de relation du candidat : `causal`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 36 — Does high blood sugar always mean diabetes?
- Incertitudes : Check Arabic wording for illness, blood sugar, and temporary duration; verify causal scope clinically.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### i02 — fr — split final

- Brut corrompu : `Un mÃ©dicament prescrit peut-il faire augmenter temporairement la glycÃ©mie ?`
- Représentation échappée : `'Un m\xc3\xa9dicament prescrit peut-il faire augmenter temporairement la glyc\xc3\xa9mie ?'`
- Proposition : Un médicament prescrit peut-il faire augmenter temporairement la glycémie ?
- Type de relation du candidat : `causal_indirect`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 36 — Does high blood sugar always mean diabetes?
- Incertitudes : Check scope of 'prescribed medicine'; possible document 36 may speak only about certain medicines.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### i03 — ar — split final

- Brut corrompu : `ÙÙ ÙÙÙÙ ÙØ¯ÙØ§Ø¡ ÙÙØµÙÙ Ø£Ù ÙØ±ÙØ¹ Ø³ÙØ± Ø§ÙØ¯Ù ÙØ¤ÙØªØ§Ø`
- Représentation échappée : `'\xd9\x87\xd9\x84 \xd9\x8a\xd9\x85\xd9\x83\xd9\x86 \xd9\x84\xd8\xaf\xd9\x88\xd8\xa7\xd8\xa1 \xd9\x85\xd9\x88\xd8\xb5\xd9\x88\xd9\x81 \xd8\xa3\xd9\x86 \xd9\x8a\xd8\xb1\xd9\x81\xd8\xb9 \xd8\xb3\xd9\x83\xd8\xb1 \xd8\xa7\xd9\x84\xd8\xaf\xd9\x85 \xd9\x85\xd8\xa4\xd9\x82\xd8\xaa\xd8\xa7\xd8\x9f'`
- Proposition : هل يمكن لدواء موصوف أن يرفع سكر الدم مؤقتا؟
- Type de relation du candidat : `causal_indirect`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 36 — Does high blood sugar always mean diabetes?
- Incertitudes : Check Arabic equivalence for prescribed medicine and temporary effect.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### i05 — fr — split final

- Brut corrompu : `La dÃ©shydratation pourrait-elle contribuer Ã  une fatigue inhabituelle ?`
- Représentation échappée : `'La d\xc3\xa9shydratation pourrait-elle contribuer \xc3\xa0 une fatigue inhabituelle ?'`
- Proposition : La déshydratation pourrait-elle contribuer à une fatigue inhabituelle ?
- Type de relation du candidat : `causal_indirect`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 4 — What are the symptoms of dehydration?; 10 — What is fatigue and what can cause it?
- Incertitudes : Causal dehydration–fatigue claim requires clinical review; separate mentions do not prove causality.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### i06 — ar — split final

- Brut corrompu : `ÙÙ ÙØ¯ ÙØ³Ø§ÙÙ Ø§ÙØ¬ÙØ§Ù ÙÙ Ø§ÙØ´Ø¹ÙØ± Ø¨Ø§ÙØªØ¹Ø¨Ø`
- Représentation échappée : `'\xd9\x87\xd9\x84 \xd9\x82\xd8\xaf \xd9\x8a\xd8\xb3\xd8\xa7\xd9\x87\xd9\x85 \xd8\xa7\xd9\x84\xd8\xac\xd9\x81\xd8\xa7\xd9\x81 \xd9\x81\xd9\x8a \xd8\xa7\xd9\x84\xd8\xb4\xd8\xb9\xd9\x88\xd8\xb1 \xd8\xa8\xd8\xa7\xd9\x84\xd8\xaa\xd8\xb9\xd8\xa8\xd8\x9f'`
- Proposition : هل قد يساهم الجفاف في الشعور بالتعب؟
- Type de relation du candidat : `causal_indirect`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 4 — What are the symptoms of dehydration?; 10 — What is fatigue and what can cause it?
- Incertitudes : Check Arabic modality and causal strength; clinical relation needs qualified review.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### i08 — fr — split final

- Brut corrompu : `La vision floue est-elle associÃ©e Ã  une glycÃ©mie Ã©levÃ©e ?`
- Représentation échappée : `'La vision floue est-elle associ\xc3\xa9e \xc3\xa0 une glyc\xc3\xa9mie \xc3\xa9lev\xc3\xa9e ?'`
- Proposition : La vision floue est-elle associée à une glycémie élevée ?
- Type de relation du candidat : `association`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 35 — What are the signs of high blood sugar?
- Incertitudes : The expected label says association, while candidate corpus wording may express causality; decide which relation is asked and what evidence qualifies.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### i09 — ar — split final

- Brut corrompu : `ÙÙ ÙØ±ØªØ¨Ø· ØªØ´ÙØ´ Ø§ÙØ±Ø¤ÙØ© Ø¨Ø§Ø±ØªÙØ§Ø¹ Ø³ÙØ± Ø§ÙØ¯ÙØ`
- Représentation échappée : `'\xd9\x87\xd9\x84 \xd9\x8a\xd8\xb1\xd8\xaa\xd8\xa8\xd8\xb7 \xd8\xaa\xd8\xb4\xd9\x88\xd8\xb4 \xd8\xa7\xd9\x84\xd8\xb1\xd8\xa4\xd9\x8a\xd8\xa9 \xd8\xa8\xd8\xa7\xd8\xb1\xd8\xaa\xd9\x81\xd8\xa7\xd8\xb9 \xd8\xb3\xd9\x83\xd8\xb1 \xd8\xa7\xd9\x84\xd8\xaf\xd9\x85\xd8\x9f'`
- Proposition : هل يرتبط تشوش الرؤية بارتفاع سكر الدم؟
- Type de relation du candidat : `association`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 35 — What are the signs of high blood sugar?
- Incertitudes : Check Arabic verb for association; distinguish association from causal direction.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### i11 — fr — split final

- Brut corrompu : `Comment comparer les symptÃ´mes de la grippe et de la COVID ?`
- Représentation échappée : `'Comment comparer les sympt\xc3\xb4mes de la grippe et de la COVID ?'`
- Proposition : Comment comparer les symptômes de la grippe et de la COVID ?
- Type de relation du candidat : `comparison`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 1 — What are the symptoms of flu?; 5 — How is the flu different from a common cold?
- Incertitudes : Check French COVID terminology and note corpus coverage may include flu but not COVID.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### i12 — ar — split final

- Brut corrompu : `ÙÙÙ ØªØ®ØªÙÙ Ø£Ø¹Ø±Ø§Ø¶ Ø§ÙØ¥ÙÙÙÙÙØ²Ø§ Ø¹Ù Ø£Ø¹Ø±Ø§Ø¶ ÙÙÙÙØ¯Ø`
- Représentation échappée : `'\xd9\x83\xd9\x8a\xd9\x81 \xd8\xaa\xd8\xae\xd8\xaa\xd9\x84\xd9\x81 \xd8\xa3\xd8\xb9\xd8\xb1\xd8\xa7\xd8\xb6 \xd8\xa7\xd9\x84\xd8\xa5\xd9\x86\xd9\x81\xd9\x84\xd9\x88\xd9\x86\xd8\xb2\xd8\xa7 \xd8\xb9\xd9\x86 \xd8\xa3\xd8\xb9\xd8\xb1\xd8\xa7\xd8\xb6 \xd9\x83\xd9\x88\xd9\x81\xd9\x8a\xd8\xaf\xd8\x9f'`
- Proposition : كيف تختلف أعراض الإنفلونزا عن أعراض كوفيد؟
- Type de relation du candidat : `comparison`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : 1 — What are the symptoms of flu?; 5 — How is the flu different from a common cold?
- Incertitudes : Check Arabic disease names and comparison wording; do not infer a clinical comparison from flu-only documents.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### i14 — fr — split final

- Brut corrompu : `Quels symptÃ´mes peuvent accompagner une anÃ©mie ?`
- Représentation échappée : `'Quels sympt\xc3\xb4mes peuvent accompagner une an\xc3\xa9mie ?'`
- Proposition : Quels symptômes peuvent accompagner une anémie ?
- Type de relation du candidat : `None`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : aucun identifié
- Incertitudes : Anemia content may be outside the current corpus; any clinical answer requires an appropriate medical reviewer/source.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### i15 — ar — split final

- Brut corrompu : `ÙØ§ Ø§ÙØ£Ø¹Ø±Ø§Ø¶ Ø§ÙØªÙ ÙØ¯ ØªØ±Ø§ÙÙ ÙÙØ± Ø§ÙØ¯ÙØ`
- Représentation échappée : `'\xd9\x85\xd8\xa7 \xd8\xa7\xd9\x84\xd8\xa3\xd8\xb9\xd8\xb1\xd8\xa7\xd8\xb6 \xd8\xa7\xd9\x84\xd8\xaa\xd9\x8a \xd9\x82\xd8\xaf \xd8\xaa\xd8\xb1\xd8\xa7\xd9\x81\xd9\x82 \xd9\x81\xd9\x82\xd8\xb1 \xd8\xa7\xd9\x84\xd8\xaf\xd9\x85\xd8\x9f'`
- Proposition : ما الأعراض التي قد ترافق فقر الدم؟
- Type de relation du candidat : `None`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : aucun identifié
- Incertitudes : Check Arabic terminology for anemia and clinical answer requirements; corpus may not cover it.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.

### i17 — ar — split final

- Brut corrompu : `ÙÙ ØªÙØ¬Ø¯ Ø¹ÙØ§ÙØ© Ø¨ÙÙÙÙØ§Ø`
- Représentation échappée : `'\xd9\x87\xd9\x84 \xd8\xaa\xd9\x88\xd8\xac\xd8\xaf \xd8\xb9\xd9\x84\xd8\xa7\xd9\x82\xd8\xa9 \xd8\xa8\xd9\x8a\xd9\x86\xd9\x87\xd9\x85\xd8\xa7\xd8\x9f'`
- Proposition : هل توجد علاقة بينهما؟
- Type de relation du candidat : `None`
- Provenance : {'raw_source': 'previous captured workspace inspection; exact original is not present in the current candidate module', 'proposal_source': 'current relation_independent_protocol.py candidate value', 'local_exact_source_matches': [], 'git_history_available': False, 'restoration_method': 'reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string', 'limitations': 'No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.'}
- Reconstruction : reversible inverse of UTF-8 bytes decoded as ISO-8859-1; round-trip verified per string
- Documents à examiner (non probants par défaut) : aucun identifié
- Incertitudes : No antecedent for 'them' is present in the candidate. Do not add context; decide whether to exclude or reformulate.
- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.
- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.
