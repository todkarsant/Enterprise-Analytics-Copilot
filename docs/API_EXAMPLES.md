# API Examples

## Health

```bash
curl http://localhost:8000/api/health
```

## Query

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Show sales by region"}'
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/api/query `
  -ContentType 'application/json' `
  -Body '{"question":"Show sales by region"}'
```
