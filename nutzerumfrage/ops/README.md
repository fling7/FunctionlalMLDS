# Container deployment

The production host uses `/srv/interactive-study` as its deployment root:

```text
/srv/interactive-study/
  compose.yaml
  .env                         # RELEASE_TAG and LEGACY_TAG only
  config/npc-config.json       # sanitized, no API key
  secrets/openai_api_key       # mode 0600
  secrets/survey_admin_pin     # mode 0600
  data/survey/
  data/npc/projects/
  data/npc/output/
  releases/<release>/study/
  releases/<release>/functionalmlds/
  releases/<legacy>/legacy/
```

Release directories are immutable snapshots. Persistent data and secrets stay
outside them. To update, upload a new timestamped release directory, build its
tag, set `RELEASE_TAG` in `.env`, run `docker compose up -d`, and verify the
health checks. Rollback only requires restoring the previous tag and running
the same command. Keep `LEGACY_TAG` pinned unless the preserved legacy snapshot
is intentionally replaced.

Before first start, seed `data/npc/projects` and `data/npc/output` from the
matching FunctionalMLDS working tree and make all `data/` directories writable
by UID/GID 1002. Never build with the real backend `config.json`; copy a
sanitized version into `config/npc-config.json` and store its former
`openai_api_key` value only in `secrets/openai_api_key`.

For a parallel preflight while host Nginx still owns ports 80/443, set
`EDGE_BIND=127.0.0.1`, `EDGE_HTTP_PORT=18080`, and `EDGE_HTTPS_PORT=18443`.
