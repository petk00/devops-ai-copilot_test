# Pravila za Deployment u Našoj Firmi

Sve Node.js aplikacije u našoj organizaciji moraju koristiti port `8080` unutar Docker kontejnera radi usklađenosti s Kubernetes clusterom.
Zabranjeno je korištenje `root` korisnika unutar Dockerfile-a iz sigurnosnih razloga. Uvijek koristiti `USER node`.
Baza podataka se u lokalnom razvoju uvijek podiže preko slike `postgres:16-alpine`.