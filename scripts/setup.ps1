# One-time dev environment setup
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -e ".[dev,frontend]"
Copy-Item .env.example .env
Write-Host "Done. Edit .env with your DATABASE_URL, then run: make migrate"
