# Test Matrix

All cases use synthetic local data in a Gitea 28.2.0 SQLite instance. Case execution outcome and product behavior are taken from the JSON report for the named run.

Baseline evidence run: `20261028T125224Z-80e1fd0e`. Latest accepted run: `20261029T150955Z-4437d857`; see [reports/evidence.md](../reports/evidence.md) and the run-scoped machine-readable reports.

| ID | Category | Scenario and expected behavior | Actual result in recorded evidence |
|---|---|---|---|
| AUTH-001 | Authentication | Public version endpoint responds and reports pinned version 28.2.0 | PASS |
| AUTH-002 | Authentication | Valid local admin credentials return the matching identity | PASS |
| AUTH-003 | Authentication | Invalid API token cannot read the authenticated-user endpoint | PASS |
| PERM-001 | Authorization | Regular user is denied the admin user-list endpoint | PASS |
| PERM-002 | Authorization | Admin can list the two regular test accounts | PASS |
| PERM-004 | Authorization | Anonymous user can read a public repository | PASS |
| PERM-005 | Authorization | Anonymous user cannot read a private repository | PASS |
| PERM-006 | Authorization | Guest cannot create an Issue in another user's private repository | PASS |
| REPO-001 | Repository | Admin creates a private repository and reads its metadata | PASS |
| PERM-003 | Authorization | Unrelated guest cannot read a private repository | PASS |
| REPO-002 | Authorization | Regular user creates an owned repository and Issue | PASS |
| ISSUE-001 | Issue lifecycle | Create Issue, comment, create/assign label, close, and reopen | PASS |
| ISSUE-002 | Input validation | Missing required Issue title returns a client validation error | PASS |
| INPUT-001 | Input validation | Malformed JSON is rejected as a client error | PASS |
| UI-001 | Browser workflow | Admin logs in, creates a repository and Issue, submits a comment, and closes the Issue | PASS |
| DATA-001 | Persistence | Repository and Issue remain readable after restarting the Gitea container | PASS |
| ISSUE-003 | Issue query | `state=closed` includes the closed Issue and `state=open` excludes it | PASS — `20261029T114725Z-15c81899`, `20261029T144534Z-ec54abd9`, `20261029T150955Z-4437d857` |
| ISSUE-004 | Issue query | Two pages with `limit=2` return three created Issues without duplicates or omissions | PASS — `20261029T114725Z-15c81899`, `20261029T144534Z-ec54abd9`, `20261029T150955Z-4437d857` |

The initial accepted run collected 16 cases. Run `20261029T114725Z-15c81899`, `20261029T144534Z-ec54abd9`, and the latest `20261029T150955Z-4437d857` each collected all 18 cases: 18 passed, 0 failed, 0 skipped, and 0 errors. These are local runs, not a coverage percentage or a claim about all Gitea behavior. The runner now rejects duplicate case IDs and verifies that the JSON summary and JUnit XML agree with the individual outcomes.
