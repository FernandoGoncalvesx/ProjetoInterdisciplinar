
Start-Process -FilePath "C:\xampp\apache\bin\httpd.exe" -WorkingDirectory "C:\xampp\apache" -WindowStyle Hidden



cd "C:\Users\gcfer\Desktop\ProjetoInterdisciplinar"
.\venv\Scripts\waitress-serve.exe --host=127.0.0.1 --port=8081 back_end.Servidor:app



cloudflared tunnel --protocol http2 --url http://127.0.0.1:8082
