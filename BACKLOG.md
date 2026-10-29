# Backlog — Signal_Matin

## Sécurité — findings (audit OWASP 2026-10-28)

Les 4 findings du rapport (SM-01 à SM-04, 2 P2 + 2 P3) sont corrigés.
Voir `security/owasp-2026-10-28/corrections/Signal_Matin.md` pour le
détail complet de cette reprise de session, et
`security/owasp-2026-10-28/corrections/Signal_Matin-p2-2026-10-28.md`
pour SM-01 à SM-03 (session précédente).

## Durcissement non traité (hors périmètre, pas un finding)

| ID | Sujet | Raison du report |
| --- | --- | --- |
| SM-ADV-01 | `xml.etree` sur flux RSS — entités internes récursives étendues (billion laughs) | Classé **conforme** par l'audit avancé, pas un finding exploitable (entités externes déjà bloquées, source = `config.yaml` géré par l'exploitant). Suggestion de durcissement à coût nul (`defusedxml.ElementTree`, API identique) non appliquée : ajouter une dépendance sans nécessité confirmée va à l'encontre de la discipline de code minimal du projet. À reconsidérer si le projet accepte un jour des flux RSS non maîtrisés par l'exploitant. |
