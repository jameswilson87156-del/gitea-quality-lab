# Test Matrix

All cases use synthetic local data in a Gitea 28.2.0 SQLite instance. Case execution outcome and product behavior are taken from the JSON report for the named run.

Accepted evidence run: `20261028T125224Z-80e1fd0e`; see [reports/evidence.md](../reports/evidence.md) and its machine-readable report.

| ID | Category | Scenario and expected behavior | Actual result in accepted run |
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

The final counts are 16 collected, 16 passed, 0 failed, 0 skipped, and 0 errors. This is one local run of these 16 cases, not a coverage percentage or a claim about all Gitea behavior.
