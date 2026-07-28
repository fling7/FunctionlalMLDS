# Stanford Agentic Reviewer client

The client uses the service's documented `/api/upload`, `/api/status/{token}`,
and `/api/review/{token}` endpoints. It never embeds or prints the authorized
email address or access token.

From the paper directory, after the strict submission check passes:

```powershell
$env:PAPERREVIEW_EMAIL = "<authorized address>"
python ..\reviewer\paperreview_client.py upload
python ..\reviewer\paperreview_client.py status
python ..\reviewer\paperreview_client.py fetch
```

The token and raw review are stored under ignored paths. Convert the raw review
into a redacted issue summary following `../REVIEW_PROTOCOL.md`; never commit
the token, email address, or a private raw response.
