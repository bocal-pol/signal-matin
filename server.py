"""Wrapper HTTP minimal autour de la CLI signal-matin, pour déclenchement
depuis n8n (nœud HTTP Request) sans accès au socket Docker de l'hôte.

Deux endpoints : POST /generate (lance la génération, renvoie le nom du PDF
produit) et GET /pdf/{filename} (sert ce PDF en téléchargement binaire, pour
que n8n puisse l'attacher à un mail sans partager de volume). N'importe
quelle logique de génération reste dans la CLI — ce serveur ne fait
qu'exposer son appel et le résultat.

Authentification par en-tête partagé (X-Signal-Matin-Token), comparée en
temps constant. Le token est lu depuis l'environnement (injecté par Vault
via l'entrypoint du conteneur, jamais en dur ici).
"""
from __future__ import annotations

import hmac
import logging
import os
import subprocess
import uuid
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "output" / "pdf"
VALID_MODES = {"auto", "compact", "standard", "extended"}

app = FastAPI(title="signal-matin-wrapper")
logger = logging.getLogger("signal_matin.server")


def _check_token(provided: str | None) -> None:
    expected = os.environ.get("SIGNAL_MATIN_API_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="SIGNAL_MATIN_API_TOKEN non configuré côté serveur")
    if not provided or not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="token invalide ou absent")


@app.post("/generate")
def generate(
    mode: str = "standard",
    x_signal_matin_token: str | None = Header(default=None),
):
    _check_token(x_signal_matin_token)
    if mode not in VALID_MODES:
        raise HTTPException(status_code=422, detail=f"mode invalide, attendu: {sorted(VALID_MODES)}")

    result = subprocess.run(
        ["signal-matin", "generate", "--live", "--mode", mode],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        # SM-01 — ne jamais renvoyer stdout/stderr bruts au client (traces
        # d'appel, chemins absolus, réponses d'API externes). Journalisés
        # côté serveur sous un incident_id, seul cet identifiant est exposé.
        incident_id = uuid.uuid4().hex
        logger.error(
            "signal_matin.generate.failed incident_id=%s returncode=%s stdout=%r stderr=%r",
            incident_id,
            result.returncode,
            result.stdout[-4000:],
            result.stderr[-4000:],
        )
        raise HTTPException(
            status_code=500,
            detail={"error": "generation_failed", "incident_id": incident_id},
        )

    pdf_lines = [line for line in result.stdout.splitlines() if line.startswith("PDF genere:")]
    pdf_path = pdf_lines[-1].split("PDF genere:", 1)[1].strip() if pdf_lines else None
    pdf_filename = Path(pdf_path).name if pdf_path else None
    return {"ok": True, "pdf_filename": pdf_filename}


@app.get("/pdf/{filename}")
def get_pdf(filename: str, x_signal_matin_token: str | None = Header(default=None)):
    _check_token(x_signal_matin_token)
    candidate = (PDF_DIR / filename).resolve()
    if PDF_DIR.resolve() not in candidate.parents or not candidate.is_file():
        raise HTTPException(status_code=404, detail="PDF introuvable")
    return FileResponse(candidate, media_type="application/pdf", filename=filename)


@app.get("/health")
def health():
    return {"ok": True}
