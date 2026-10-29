# Backlog — Signal_Matin

## Sécurité — findings non corrigés (audit OWASP 2026-10-28, session P2/P3)

| ID | Priorité | Sujet | Raison du report |
| --- | --- | --- | --- |
| SM-04 | P3 (A10) | `urlopen` sans contrainte de schéma sur les sources configurées (`connectors/rss.py`, `calendar_ics.py`, `weather.py`) | Hors périmètre explicitement demandé pour cette session (seuls SM-01, SM-02, SM-03 étaient visés). Non atteignable à distance (nécessite déjà un accès en écriture à `config.yaml`, monté en lecture seule dans le conteneur) — impact faible mais correction simple (`urlparse(url).scheme in {"http", "https"}`) à faire dans une session dédiée A10. |

Voir `security/owasp-2026-10-28/corrections/Signal_Matin-p2-2026-10-28.md` pour le détail
des 3 findings traités dans cette session (SM-01 à SM-03).
