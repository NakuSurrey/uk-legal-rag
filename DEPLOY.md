# DEPLOYMENT GUIDE (PRIVATE — DO NOT PUSH TO GITHUB)

⚠️ This file contains sensitive server information. Keep it local only.

## Server Details

- **Provider:** DigitalOcean Droplet
- **Region:** London
- **Specs:** 2GB RAM, 1 CPU, 50GB SSD ($12/month)
- **Credits:** $200 via GitHub Student Developer Pack
- **IP:** 167.71.142.107
- **Domain:** uklegalrag.me (Namecheap, A record → 167.71.142.107)

## SSH Access

```bash
ssh root@167.71.142.107
```

## Deploy / Update

```bash
# SSH into server
ssh root@167.71.142.107

# Navigate to project
cd ~/uk-legal-rag

# Pull latest code
git stash          # discard any local server edits
git pull origin master

# Verify requirements.txt has correct huggingface-hub version (==0.33.4, NOT 1.5.0)
grep huggingface requirements.txt

# If wrong version:
# sed -i 's/huggingface_hub==1.5.0/huggingface-hub==0.33.4/' requirements.txt

# Rebuild and restart
docker stop $(docker ps -q)
docker build -t uk-legal-rag .
docker run -d -p 80:8501 -p 8000:8000 --env-file .env --restart always uk-legal-rag

# Verify
docker logs $(docker ps -q)
```

## Environment File (.env on server)

```
HUGGINGFACE_API_KEY=hf_your_actual_key_here
```

Created with: `nano .env` on the Droplet.

## Useful Docker Commands

```bash
docker logs $(docker ps -q)           # View logs
docker logs -f $(docker ps -q)        # Follow logs live
docker exec -it $(docker ps -q) bash  # Shell into container
docker stop $(docker ps -q)           # Stop container
docker rm $(docker ps -aq)            # Remove stopped containers
docker ps                             # List running containers
```

## Domain DNS Setup (already done)

- Registrar: Namecheap (free via GitHub Student Pack)
- Domain: uklegalrag.me
- DNS: A record, Host: @, Value: 167.71.142.107, TTL: Automatic

## Known Deployment Issues

1. **sys.path.insert must be in api.py** — without it, FastAPI crash-loops with ModuleNotFoundError
2. **requirements.txt huggingface_hub version** — must be ==0.33.4, not 1.5.0
3. **git stash before git pull** — server may have local edits from nano
4. **Supervisord root warning** — harmless, can ignore
