#!/bin/bash
# test_api.sh

echo "1. Probando crear renta..."
curl -X POST http://localhost:8080/rentar \
   -H "Content-Type: application/json" \
   -d '{"id": 0, "cliente": "Juan", "dvd_titulo": "Matrix", "staff_id": "S1", "costo": 50.0, "fecha_renta": "2023-01-01T12:00:00Z", "devuelto": false}'

echo -e "\n\n2. Probando reporte pendientes..."
curl http://localhost:8080/reporte/pendientes

echo -e "\n\nPruebas finalizadas."