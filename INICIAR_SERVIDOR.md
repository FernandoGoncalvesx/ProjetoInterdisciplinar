
cd "C:\Users\gcfer\Desktop\ProjetoInterdisciplinar"
.\venv\Scripts\waitress-serve.exe --host=127.0.0.1 --port=8081 backend.app:app

cloudflared tunnel --protocol http2 --url http://127.0.0.1:8082
