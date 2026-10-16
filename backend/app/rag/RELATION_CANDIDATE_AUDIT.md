# Revue préalable des candidats relationnels

Statut : revue documentaire avant annotation, sans modification des 23 questions. Les conclusions ci-dessous décrivent le corpus `data_enriched_v3.json` actuellement présent; elles ne constituent pas des annotations médicales. Les ID de documents sont ceux du snapshot local.

**État après diagnostic contrôlé :** l'inspection précédente avait capturé les 15 chaînes en mojibake; le module candidat contient désormais des propositions lisibles. L'historique Git n'est pas exploitable (le dossier `.git` local ne contient ni `HEAD` ni `config`) et aucune copie exacte distincte n'a été trouvée dans les sources textuelles du projet. L'artefact `relation_candidate_restorations.json` conserve pour chaque ID la chaîne brute observée, les points de code, `repr`, la proposition actuelle, la méthode et les limites de provenance. L'inversion UTF-8→ISO-8859-1 est vérifiée individuellement par aller-retour pour chaque chaîne; elle établit la réversibilité technique, pas l'intention de l'auteur ni la qualité linguistique. Toutes les propositions restent non validées et exclues des métriques officielles.

### Statut de restauration et validation humaine requise

Les 15 chaînes concernées sont d02, d03, d05, d06, i02, i03, i05, i06, i08, i09, i11, i12, i14, i15 et i17. Pour chaque entrée, l'artefact de provenance contient les formes brute et proposée complètes, les échappements Unicode, les points de code et le statut. **d03** exige un arbitrage du sens : la formulation arabe actuelle peut être comprise comme « les symptômes changent par rapport au rhume » plutôt que comme une comparaison idiomatique. **i08** exige une décision médicale sur l'adéquation entre l'intention d'association et le fait de corpus formulé en causalité. Les 13 autres sont des reconstructions techniques réversibles, à confirmer par un humain; aucune n'est validée.

| IDs | Revue linguistique | Revue médicale / preuve clinique |
|---|---|---|
| d02 | Vérifier naturel et nuance de « accompagner ». | Association diabète–soif : confirmer que la formulation ne renforce pas la relation. |
| d03 | Arbitrage arabe natif obligatoire; formulation de comparaison possiblement maladroite. | Limiter la comparaison aux faits réellement établis par le corpus. |
| d05 | Vérifier naturel de « signes accompagnent ». | Revue de l'exactitude des signes cités avant réponse clinique. |
| d06 | Vérifier l'arabe, en particulier « sucre » et la temporalité. | La question est causale; doc 36 à vérifier pour portée et direction. |
| i02–i03 | Vérifier équivalence exacte de « médicament prescrit », modalité et temporairement. | Causalité médicamenteuse; doc 36 parle de certains médicaments, sans établir que toute prescription a cet effet. |
| i05–i06 | Vérifier naturel de « contribuer » et équivalence. | Causalité déshydratation–fatigue; docs 4 et 10 séparés ne suffisent pas à la prouver. |
| i08–i09 | Vérifier équivalence de l'association, notamment du verbe arabe. | Arbitrer association vs causalité : doc 35 dit que l'hyperglycémie peut causer une vision floue. |
| i11–i12 | Vérifier « la COVID » et le terme arabe retenu. | Comparaison grippe–COVID; le corpus actuel ne contient pas COVID. |
| i14–i15 | Vérifier terminologie clinique et naturel du triplet. | Information sur l'anémie absente du corpus; une validation clinique externe est nécessaire pour toute réponse médicale. |
| i17 | Vérifier que l'arabe exprime bien des antécédents non précisés. | Pas de relation clinique déterminable sans entités; garder indéterminé, ne pas inventer. |

Le mécanisme de capture est `scripts/capture_relation_candidate_provenance.py`; il ne modifie pas `relation_independent_protocol.py`. Pour régénérer l'artefact après approbation d'une proposition, conserver l'ancien fichier en historique de versions et consigner séparément l'identité/date du validateur. La validation médicale et linguistique reste `needs_validation` tant qu'elle n'a pas été réellement effectuée.

## Comptage et indépendance

- Développement : 6 cas, 6 familles, tous non validés. Les familles infection–fièvre, diabète–soif, grippe–rhume, glucose simple, déshydratation simple et maladie–glucose recouvrent les familles des benchmarks historiques et/ou les profils/règles déjà examinés. Ce jeu calibre la procédure; il n'est pas un jeu indépendant pour sélectionner E.
- Final : 17 formulations, mais seulement 6 familles sémantiques : medication–glucose (3 traductions), déshydratation–fatigue (3), glucose–vision (3), grippe–COVID (3), anémie simple (3), entités non précisées (2). Les variantes traduites ne sont pas des observations indépendantes. L'effectif pour une inférence est donc au plus 6 familles, non 17.
- Les formulations finales reprennent des indices lexicaux transparents pour un détecteur : `contribute` (i04), `associated` (i07), `compare` (i10) et des formulations équivalentes dans les traductions. Les trois paires linguistiques sont des paraphrases parallèles. Les candidats testent ainsi en partie le rappel de marqueurs connus, plutôt qu'une généralisation lexicale aveugle. Conserver ces cas pour l'audit linguistique, mais ne pas présenter leur score comme preuve de robustesse lexicale.
- Aucun doublon exact développement/final n'est présent et les familles déclarées sont disjointes dans le code. Cela ne rend pas les familles de développement indépendantes des benchmarks historiques.

## Décision humaine à prendre avant gel

| IDs | Risque / recouvrement vérifiable | Information corpus et preuve manquante | Recommandation préalable |
|---|---|---|---|
| d01 | Recouvre la famille infection–fièvre historique. | Docs 0 et 6 sont les références historiques; à contrôler dans le snapshot avant usage. | Garder pour calibration, exclure de toute affirmation d'indépendance. |
| d02 | Recouvre diabète–soif et la famille f10 historique. | La formulation pose une association; faire relire la nuance FR. | Calibration seulement; annotation médicale et linguistique requise. |
| d03 | Recouvre la famille grippe–rhume historique; arabe à vérifier, notamment le registre. | La comparaison attendue doit rester limitée à ce que dit la source. | Calibration seulement; revue linguistique native. |
| d04 | Simple, mais recouvre les questions glucose/hyperglycémie déjà évaluées. | Plusieurs documents de glycémie existent. | Calibration de l'intention, pas preuve indépendante. |
| d05 | Simple déshydratation, proche des questions simples historiques. | Doc 4 contient symptômes et urgences. | Calibration; contrôler que la réponse conserve le routage urgence. |
| d06 | Recouvre directement maladie–glucose et le profil causal existant. | Doc 36 documente une hausse temporaire liée à la maladie. | Calibration seulement; marqueur causal explicite. |
| i01–i03 | Triplet de traduction; `make ... rise` est un indice causal lexicalement transparent. | Doc 36 dit que certains médicaments peuvent faire temporairement monter la glycémie. Il ne distingue pas nécessairement les médicaments prescrits; la portée « prescribed » demande une validation. | Garder comme famille candidate, annoter la portée exacte et ne compter qu'une famille. |
| i04–i06 | Triplet traduit; `contribute` est un marqueur causal très explicite. | Doc 4 liste fatigue parmi signes de déshydratation; doc 10 décrit fatigue séparément. Aucun ne prouve que la déshydratation cause la fatigue. Fait réel clinique à valider indépendamment. | Peut tester preuve insuffisante du corpus, après validation médicale; ne pas étiqueter la relation réelle comme fausse. |
| i07–i09 | Triplet traduit; `associated` est un marqueur d'association explicite. | Doc 35 énonce que l'hyperglycémie peut causer une vision floue : preuve directe de symptôme/causalité dans ce corpus, mais vérifier si l'annotation attendue « association » accepte cette direction et ce niveau de preuve. | Garder si les critères distinguent causalité d'association; sinon reformuler après décision humaine, avant test final. |
| i10–i12 | Triplet traduit; `compare`/équivalents sont des marqueurs littéraux de comparaison. Recouvre la famille grippe déjà présente dans les données. | Le corpus identifié décrit grippe et rhume (doc 5), mais aucune occurrence de COVID; il ne fournit donc pas la comparaison demandée. | Cas de couverture insuffisante possible; valider l'arabe et ne pas inférer une différence réelle. |
| i13–i15 | Triplet traduit, mais hors des concepts médicaux documentés trouvés. | Recherche dans les questions/réponses du snapshot : aucun document sur anemia/anémie. Réponse attendue exige une source externe. | Exclure des métriques de retrieval de ce corpus ou garder comme contrôle simple explicitement sans preuve; validation médicale nécessaire pour toute réponse clinique. |
| i16–i17 | Deux traductions seulement; « these/them » n'a pas d'antécédent. | Les concepts à relier sont absents par construction. | Garder comme contrôle d'intention indéterminée, exclure du retrieval médical et vérifier la qualité idiomatique arabe. |

### Marqueurs de E et familles antérieures

Les familles finales ne répètent pas les paires de concepts de l'inventaire déclaré, mais plusieurs formulations réutilisent exactement des marqueurs relationnels évidents (`contribute`, `associated`, `compare`) et des patrons causaux similaires. Les concepts glucose, grippe et déshydratation recoupent abondamment le corpus et les cas historiques. « Non présent comme paire de profil » n'équivaut donc ni à indépendance sémantique ni à indépendance lexicale. La décision d'accepter, reformuler ou exclure appartient aux responsables de l'étude avant toute révélation de prédictions; ce rapport ne remplace aucun item.

## Sources et validation nécessaires

Recontrôler les docs 4, 10, 35 et 36 dans le snapshot exact utilisé au gel. Pour une vérité clinique, citer une source médicale appropriée, préciser population, contexte et direction de l'effet, puis obtenir une validation qualifiée. Les faits absents du corpus (COVID, anémie) ne peuvent recevoir de preuve de retrieval inventée. Utiliser le formulaire `relation_annotation_template.json`; à défaut de validation clinique ou linguistique nécessaire, garder `needs_validation` et omettre l'exemple des métriques officielles.
