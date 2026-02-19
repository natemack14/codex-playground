@echo off
cd /d "%~dp0"
start "" http://localhost:8507
python -m streamlit run app.py --server.port 8507 --server.headless true
