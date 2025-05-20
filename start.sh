#!/bin/bash
echo "✅ Instalando dependências..."
pip install --no-cache-dir --upgrade google-generativeai==0.3.2 google-adk==0.3.0 flask

echo "🚀 Iniciando app.py..."
python app.py
