# Stanford Agentic Reviewer client

The client mirrors the service's current public browser flow:
`/api/get-upload-url`, direct upload through the returned presigned form,
`/api/confirm-upload`, and `/api/review/{token}`. A review request returns HTTP
202 while processing. The client never embeds or prints the authorized email
address or access token.

From the paper directory, after the strict submission check passes:

```powershell
$env:PAPERREVIEW_EMAIL = "<authorized address>"
python ..\reviewer\paperreview_client.py upload
python ..\reviewer\paperreview_client.py status
python ..\reviewer\paperreview_client.py fetch
```

Use `upload --dry-run` to run all local submission gates without contacting the
service.

The token and raw review are stored under ignored paths. Convert the raw review
into a redacted issue summary following `../REVIEW_PROTOCOL.md`; never commit
the token, email address, or a private raw response.
