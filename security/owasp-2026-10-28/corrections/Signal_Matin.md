# Corrections OWASP — Signal_Matin — reprise de session

Branche : `feature/sec-owasp-p2-2026-10-28`. Complète les findings SM-01 à SM-03
(`Signal_Matin-p2-2026-10-28.md`) avec SM-04.

## Finding corrigé

| ID | OWASP | Sujet | Commit |
| --- | --- | --- | --- |
| SM-04 | A10 / A08 | `_payload()` appelait `urlopen()` directement sur l'URL configurée pour un flux RSS, acceptant implicitement `file://` et `ftp://` en plus de `http(s)` | `b39e859` |

## Détail SM-04 (b39e859)

Les URLs de flux RSS viennent de `config.yaml` (liste d'abonnements gérée par l'exploitant, pas
une entrée distante) : non exploitable à distance en pratique, mais le contrôle est une défense
en profondeur à coût nul. Rejette tout schéma hors `{http, https}` avant l'appel réseau.

## Non-finding documenté (SM-ADV-01)

`xml.etree` sur les flux RSS (entités internes récursives étendues, type "billion laughs") a été
classé **conforme** par l'audit avancé : les entités externes sont déjà bloquées par défaut, et
la source (`config.yaml`) est gérée par l'exploitant. Suggestion de durcissement à coût nul
(`defusedxml.ElementTree`, API identique) **non appliquée** par discipline de code minimal —
ajouter une dépendance sans nécessité confirmée. À reconsidérer si le projet accepte un jour des
flux RSS non maîtrisés par l'exploitant.

## Vérification (2026-10-30)

- Conteneur `signal-matin` : `requirements.lock.txt` et `pyproject.toml` synchronisés entre
  disque et conteneur (empreintes identiques).
- pytest absent de l'image runtime par design (dépendance `dev` uniquement, cf. `Dockerfile`) —
  installé temporairement dans le conteneur pour la vérification, sans modification de l'image.
- Le dossier `tests/` n'est pas copié dans l'image runtime (non nécessaire en production) : copié
  temporairement dans le conteneur pour l'exécution.
- Deux échecs initiaux (`test_large_daily_variation_creates_balanced_continuation_pages`,
  `test_delayed_print_reuses_real_task_action`) causés par l'absence de `web/` et `scripts/`
  dans ce même conteneur minimal — confirmés non liés au code en comparant avec le disque hôte
  où ces fichiers existent réellement, puis copiés dans le conteneur à leur tour.
- Résultat final : `python -m pytest tests/ -v` → **24 passed**.
