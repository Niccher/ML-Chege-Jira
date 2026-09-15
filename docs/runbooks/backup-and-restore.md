# Runbook: Backup & Restore

This runbook outlines backup and recovery procedures for model artifacts and AI audit tables.

## 1. Model Binaries Archive
Model weights reside in `models/`. To archive:
```bash
tar -czvf ml_models_backup_$(date +%Y%m%d).tar.gz models/*.gguf
```

## 2. AI Database Tables Backup
To snapshot the AI configuration and history tables:
```bash
docker exec -i mysql mysqldump -u root -p"$DB_PASSWORD" db_chege_jira \
  ai_config ai_task_enhancements ai_sprint_summaries ai_time_reports ai_qa_log \
  > ai_tables_backup_$(date +%Y%m%d).sql
```

## 3. Restoration Procedure
To restore AI tables:
```bash
docker exec -i mysql mysql -u root -p"$DB_PASSWORD" db_chege_jira < ai_tables_backup_20260915.sql
```
