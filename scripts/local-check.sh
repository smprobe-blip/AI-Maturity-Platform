#!/bin/bash
# Быстрая локальная проверка frontend перед push
echo "🔨 Пересборка frontend..."
cd infrastructure
docker compose up -d --build frontend
sleep 12

echo "🌐 Открываю http://localhost:3000 ..."
open http://localhost:3000

echo ""
echo "✅ Проверьте изменение локально."
echo "   Если всё ОК — git add / commit / push."
