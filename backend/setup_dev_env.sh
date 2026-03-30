#!/usr/bin/env bash
# Entorno de desarrollo local: no requiere permisos de escritura en site-packages del sistema.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
echo ""
echo "Listo. Activa el entorno con:"
echo "  source .venv/bin/activate"
echo "O ejecuta sin activar:"
echo "  backend/.venv/bin/pytest"
echo "  backend/.venv/bin/uvicorn main:app --reload"
