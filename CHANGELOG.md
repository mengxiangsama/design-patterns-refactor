# Changelog

此文件记录仓库变更；`Unreleased` 不表示已经发布版本。
This file records repository changes. `Unreleased` is not a published release.

## Unreleased

### Documentation

- Clarified the evidence-first, behavior-preserving refactoring approach on the README landing section.
- Added an English README, language-scope FAQ, and contribution guide.
- Added issue and pull request templates for focused, sanitized feedback.
- Aligned Chinese/English use cases, examples, install/update instructions, and troubleshooting.
- Added optional skills CLI installation and clarified third-party discovery/telemetry behavior.

### Skill and validation

- Clarified language-native refactoring choices and removed project-specific Java assumptions.
- Added a standard-library Python function-composition example and contract tests.
- Added isolated evaluation tasks for Python analysis/cleanup, durable event delivery, consumer idempotency, and message topology. Inputs are separated from scoring guidance.
- Added fixture baseline checks to CI; these do not establish model quality or production correctness.
- Explicitly close reopened SQLite connections in baseline tests so Windows can remove temporary databases; the original-failure assertions are unchanged.

### Installation

- Added a Git-history-based copy updater with read-only checks, local-change refusal, backups outside skill scanning, and restoration on activation failure.
- Initial Bash installation still refuses overwrites and needs no Python; the updater requires Python 3.9+.
- Added a persistent recovery journal, `--recover`, Ctrl+C restoration, and OS-managed update/recovery locks that release on process exit. Recovery validates files and refuses to overwrite manual changes; installation also refuses an unfinished update.
- Fixed Windows CRLF checkout failures with `.gitattributes`; added fresh-clone and interruption regression tests, Git Bash test discovery, and Ubuntu/macOS/Windows validation jobs.
- Limited LF enforcement to shell scripts and regression-tested existing CRLF checkout upgrades, preserving skill-file fingerprint compatibility.

No cross-client compatibility certification or production verification is claimed.
