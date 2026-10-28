# Observed Issues During Test Development

This log separates test-harness problems from confirmed product defects. The runs below did not confirm a Gitea product defect.

| Observation | Evidence | Classification | Resolution |
|---|---|---|---|
| Admin CLI failed when invoked as container root | Gitea log: `Gitea is not supposed to be run as root` | Test setup issue | Run local admin CLI as the image's `git` user; covered by a unit test. |
| Issue state update returned HTTP 201, while the first test expected 200 | Live response was 201; official Edit Issue API documents 201 Issue responses | Test expectation issue | Assert the documented 201 response and returned `state` for both close and reopen. |
| Browser heading had a `#1` suffix, while the first locator required an exact accessible name | Playwright accessibility snapshot showed `Browser workflow issue from automated run #1` | Test locator issue | Assert the H1 contains the intended issue title; keep issue number as normal Gitea UI text. |
| Gitea briefly closed the connection while the persistence test waited through restart | `RemoteDisconnected` escaped the readiness loop; container was healthy shortly afterward | Test readiness issue | Retry `OSError` within the existing bounded health wait; a local HTTP server unit test reproduces a real dropped connection. |
| An early Playwright trace captured the local login password | Automated scan found a credential string in the generated trace archive | Test artifact security issue | Deleted the trace. Failure traces now start after login, redact configured credentials and cookie/authorization header values, and discard the raw archive before publishing. A synthetic real-browser failure probe verified the produced ZIP. |
| The run report omitted teardown failures and could mark a test passed after artifact teardown failed | Unit regression test modeled a passing call followed by failed teardown | Test reporting defect | JSON now accounts for setup, call, and teardown outcomes and sums phase durations. |
| Local credentials in pytest failure text could reach terminal, JUnit, and HTML output | Synthetic Playwright `fill` timeout reproduced a password in long representation and captured output | Test artifact security issue | Credentials are redacted from `TestReport` before reporting hooks consume it; an intentional failure probe found no password in terminal, JSON, JUnit, or HTML. |
| An environment override could direct authenticated tests away from the local service | Resolver tests rejected external hosts, alternate ports, and URL paths | Test target-safety issue | Test fixtures accept only `http://127.0.0.1:13000`; reports always record that fixed target. |
| Initial authorization assumption expected guests to be blocked from creating an Issue on a public repository | Gitea 28.2.0 returned 201, matching its public-repository behavior | Test expectation issue | Reframed the denial case against a private repository the guest cannot access; separate tests cover anonymous public reads and regular-user allowed writes. |

The early browser-locator, permission-expectation, and restart-wait failures are retained in development run reports. Credential-bearing raw traces were removed; only sanitized diagnostic traces are retained.
