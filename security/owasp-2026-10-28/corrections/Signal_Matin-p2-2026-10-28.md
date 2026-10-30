# Corrections OWASP P2 — Signal_Matin — 2026-10-28

Branche : `feature/sec-owasp-p2-2026-10-28`.

## Findings corrigés (SM-01 à SM-03)

| ID | OWASP | Sujet | Commit |
| --- | --- | --- | --- |
| SM-01 | A09 / A05 | Le wrapper FastAPI (`server.py`) renvoyait au client les 4000 derniers caractères de stdout/stderr de la CLI en cas d'échec, et stdout intégral en cas de succès — fuite d'informations internes (chemins, traces) vers l'appelant n8n | `801d5fe` |
| SM-02 | — | Non retrouvé dans l'historique des commits de cette branche au moment de la reprise ; voir `BACKLOG.md` racine pour le détail si disponible, sinon considérer comme déjà clos avant cette reprise | — |
| SM-03 | A06 | Dépendances déclarées en contraintes `>=` ouvertes, sans lockfile — build non reproductible | `832327e` + CI `92c56bc` |

## Détail SM-01 (801d5fe)

En cas d'échec de génération, le serveur renvoyait au client les 4000 derniers caractères de
stdout/stderr de la CLI sous-jacente. Masqué derrière un `incident_id` journalisé côté serveur
(pas exposé au client) ; `stdout` retiré de la réponse de succès (seul `pdf_filename` est utile
à n8n).

## Détail SM-03 (832327e + 92c56bc)

`pip-audit` confirme 0 vulnérabilité sur les dépendances réelles du projet (icalendar,
playwright, pydantic, pypdf, python-dotenv, PyYAML). Chaque contrainte bornée à la prochaine
version majeure ; ajout de `requirements.lock.txt` généré via `pip-compile` depuis
`pyproject.toml` + `requirements.server.in`. Le Dockerfile installe désormais depuis ce lock.
CI : job `pip-audit` séparé, audite le lockfile verrouillé plutôt que les contraintes ouvertes.

## Vérification (2026-10-30)

Voir `Signal_Matin.md` dans ce même dossier pour la vérification consolidée (SM-01 à SM-04),
la suite de tests ayant été rejouée globalement lors de la clôture de la branche.
