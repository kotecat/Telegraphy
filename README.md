# Telegraphy

An open-source alternative to [Telegra.ph](https://telegra.ph/) for simple and anonymous publishing. (preview [t.ikote.ru](https://t.ikote.ru/))

## Installation guide
*(See AdminToken in logs, after run)*

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

#### Run (Docker) (Recommended)
🛠 <u> Build & Run</u>:
```bash
docker-compose up --build -d
```
▶️ <u>Run</u>:
```bash
docker-compose up -d
```
🔄 <u>Restart</u>:
```bash
docker-compose down && docker-compose up -d
```
⬇️* <u>UPDATE</u> (req manually rm old image):
```bash
git pull && \
docker-compose build && \
docker-compose down && \
docker-compose up -d
```
Logs:
*(See AdminToken in logs)*
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
