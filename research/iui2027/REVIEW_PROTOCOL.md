# Stanford Agentic Reviewer protocol

Service: <https://paperreview.ai/>  
Live upload client: <https://paperreview.ai/static/upload.js>
Live review client: <https://paperreview.ai/static/review.js>

The local secret-safe API client is in `reviewer/paperreview_client.py`. It
refuses an upload unless the strict paper check succeeds.

## Privacy boundary

The service does not publish a dedicated privacy, retention, deletion, or
zero-data-retention policy. It processes the PDF through third-party services.
Only an anonymized draft without confidential, personal, contractual, or
embargo-sensitive material may be uploaded.

The review token is a secret capability:

- never commit it;
- never print it in a tracked log;
- store it only under `reviewer/private/` or as an environment variable;
- do not place it in issues, commit messages, or public URLs.

## Submission

1. Build an English anonymous PDF.
2. Verify that it is at most 10 MB and that all essential content, including
   the Conclusion, is within the first 15 pages. The service accepts a longer
   IUI manuscript but analyzes only those first 15 pages.
3. Select `Other` as target venue and enter `ACM IUI 2027`.
4. Use the email address explicitly authorized by the user.
5. Submit once and immediately save the returned token privately.
6. Poll no more frequently than every five minutes.

The public service currently uses a three-step upload: request a presigned
object-store form, upload the PDF directly, then confirm the submission. The
review endpoint returns HTTP 202 while processing and the completed JSON
review otherwise. The local client mirrors this current browser flow.

## Review-to-task conversion

For each review, record a redacted, non-secret summary containing:

- timestamp and paper commit;
- overall assessment;
- strengths;
- each weakness classified as critical, major, moderate, or minor;
- action taken;
- evidence or section changed;
- resolution status.

Do not blindly accept reviewer suggestions. Correct factual errors in the review
and document why an inapplicable suggestion was not followed.

## Pass condition

Because the service exposes an ICLR-specific numerical score but no
IUI-calibrated accept/reject prediction, the pass condition is:

1. the textual overall assessment recommends acceptance, describes the paper as
   submission-ready, or contains an equivalently positive judgment;
2. no unresolved issue is classified by the reviewer or the authors as critical
   or major;
3. all factual, methodological, reproducibility, clarity, and scope concerns
   that could change the verdict are resolved in the current PDF.

Only after all three conditions pass may the master task be completed and the
heartbeat paused.
