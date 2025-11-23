## Reiniciar y destruir todo (kill'em all)
docker-compose down -v

-v elimina volúmenes para iniciar limpio

## Exec el seed después de reiniciar y regenerar todo

docker-compose exec backend python seed_data.py

