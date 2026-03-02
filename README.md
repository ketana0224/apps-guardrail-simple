# apps-guardrail-simple

AIガードレール API の最小実装です。

- UI なし
- API 呼び出しあり
- ガードレールロジックはプレースホルダ
- Azure App Service へデプロイ可能

## エンドポイント

- `GET /health`
- `POST /guardrail/check`
- `POST /guardrail/invoke`

## ローカル起動

### 1. セットアップ

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 環境変数

```powershell
$env:AI_API_URL="https://example.com/ai"
$env:AI_API_KEY="your-key"
$env:AI_API_TIMEOUT="20"
```

### 3. 実行

```powershell
python app.py
```

## Azure App Service へデプロイ（azd）

### 1. 前提

- Azure CLI インストール済み
- Azure Developer CLI (`azd`) インストール済み
- `az login` 済み

### 2. デプロイ

```powershell
azd init -t .
azd up
```

### 3. App Settings 設定

App Service の構成で以下を設定してください。

- `AI_API_URL`
- `AI_API_KEY`
- `AI_API_TIMEOUT`
