# Observed Issues During Test Development

This log separates test-harness problems from confirmed product defects. The runs below did not confirm a Gitea product defect.

| Observation | Evidence | Classification | Resolution |
|---|---|---|---|
| Admin CLI failed when invoked as container root | Gitea log: `Gitea is not supposed to be run as root` | Test setup issue | Run local admin CLI as the image's `git` user; covered by a unit test. |
| Issue state update returned HTTP 201, while the first test expected 200 | Live response was 201; official Edit Issue API documents 201 Issue responses | Test expectation issue | Assert the documented 201 response and returned `state` for both close and reopen. |
| Browser heading had a `#1` suffix, while the first locator required an exact accessible name | Playwright accessibility snapshot showed `Browser workflow issue from automated run #1` | Test locator issue | Assert the H1 contains the intended issue title; keep issue number as normal Gitea UI text. |
| Gitea briefly closed the connection while the persistence test waited through restart | `RemoteDisconnected` escaped the readiness loop; container was healthy shortly afterward | Test readiness issue | Retry `OSError` within the existing bounded health wait; a local HTTP server unit test reproduces a real dropped connection. |
| An early Playwright trace captured the local login password | Automated scan found a credential string in the generated trace archive | Test artifact security issue | Deleted that generated trace and changed tracing to start only after successful login. Pre-login failures keep screenshot evidence but no trace. |

The early browser-locator and restart-wait failures are retained in development run reports. The credential-bearing trace itself was removed and is not part of the deliverable.
