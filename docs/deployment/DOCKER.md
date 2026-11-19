# Deploy with Docker

## Docker (manual)
```bash
git clone https://github.com/T3rmx/T3rmx-UserBot.git
cd T3rmx-UserBot
cp .env.example .env
# edit .env with required credentials
docker build -t t3rmx-userbot .
docker run -d --name t3rmx-userbot --restart unless-stopped --env-file .env \
  -v "$(pwd)/downloads:/app/downloads" -v "$(pwd)/temp:/app/temp" \
  t3rmx-userbot
```

View logs:
```bash
docker logs -f t3rmx-userbot
```

## Docker Compose
```bash
git clone https://github.com/T3rmx/T3rmx-UserBot.git
cd T3rmx-UserBot
cp .env.example .env
# edit .env with required credentials
docker compose up -d --build
docker compose logs -f
```

`docker-compose.yml` loads variables from `.env` and mounts `downloads/` and `temp/`.

## Notes
- The image installs pinned dependencies from `requirements.txt` and runs `python3 -m JoKeRUB`.
- Do not bake secrets into images; pass them via environment variables/secret stores.
- For production, use a persistent database (`DATABASE_URL`) if you need durable state across container recreation.
