# Runbook: Service Restart & Container Recovery

This runbook describes standard operational procedures for gracefully stopping, restarting, and recovering the **ML Chege Jira** container.

## Standard Graceful Restart
```bash
docker compose restart ml-chege-jira
```

## Clean Rebuild (Without Losing Models Volume)
To rebuild image layers while retaining downloaded GGUF weights:
```bash
docker compose down
docker compose build --no-cache ml-chege-jira
docker compose up -d
```

## Crash / OOM Recovery
1. Check exit code:
   ```bash
   docker inspect ml-chege-jira --format='{{.State.ExitCode}}'
   ```
2. If exit code is `137` (OOM killed):
   - Switch `.env` to `DEFAULT_MODEL=phi3-mini`.
   - Reduce `N_CTX=2048`.
   - Restart: `docker compose up -d`.
