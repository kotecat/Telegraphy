# Telegraphy

An open-source alternative to [Telegra.ph](https://telegra.ph/) for simple and anonymous publishing. (preview [t.ikote.ru](https://t.ikote.ru/))

## Installation guide

Run the following command

clone repo:
```bash
git clone https://github.com/kotecat/Telegraphy.git
cd Telegraphy/
```

Setting .env
```bash
mv .env.ex .env
nano .env
```

#### Build & Run (Docker) (Recommended)
Build:
```bash
docker build -t telegraphy:latest .
```
Run:
```bash
docker-compose up -d
```
Restart:
```bash
docker-compose down && docker-compose up -d
```
Logs:
```bash
docker-compose logs
```

See more commands:
```bash
docker-compose --help
```

#### Run (Without Docker) (Not Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
alembic upgrade head
python3 ./main.py
```