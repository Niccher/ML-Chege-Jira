# Release Train & Compatibility Matrix

This document tracks versioning rules, polyrepo compatibility, and deprecation policies between **ML Chege Jira** and the **CodeIgniter 4 WebApp**.

## Compatibility Matrix

| ML Chege Jira Version | WebApp Version | Minimum API Version | Default Model | Supported Python |
|-----------------------|----------------|---------------------|---------------|------------------|
| `v0.1.0` | `v1.2.0` | `/api/v1` | `phi3-mini` | `3.11`, `3.12` |

## Semantic Versioning Policy

- **Major (`X.0.0`)**: Breaking changes to `/api/v1/*` contracts, schema alterations removing `ai_*` tables, or incompatible model file format changes.
- **Minor (`0.X.0`)**: New domain endpoints, new model additions, performance tuning.
- **Patch (`0.0.X`)**: Bugfixes, prompt enhancements, dependency security patches.
