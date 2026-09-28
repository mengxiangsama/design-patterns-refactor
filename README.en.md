# Design Patterns Refactor · Cross-language AI Refactoring Skill

[中文](README.md) | [English](README.en.md)

[![CI](https://github.com/mengxiangsama/design-patterns-refactor/actions/workflows/ci.yml/badge.svg)](https://github.com/mengxiangsama/design-patterns-refactor/actions/workflows/ci.yml) · [MIT License](LICENSE)

**Help AI choose refactorings from real code—not force design patterns onto it.**

A cross-language Codex skill for legacy code refactoring, design pattern selection, dead code cleanup, microservice boundaries, and eventual consistency. Apply it to Java/Spring Boot, Go, Python, TypeScript, and other projects using each language's own functions, interfaces, and composition.

- **Evidence first:** trace call paths, cite code, and explain trade-offs.
- **Keep simple code simple:** stable branches may need no pattern; analysis stays read-only.
- **Preserve behavior:** protect errors, money, transactions, ordering, and external side effects; report verification limits.

Runnable before/after examples currently cover **Java and Python**, not every language, pattern, or model. This is guidance for a coding agent, not a standalone refactoring engine.

[Quick start](#quick-start) · [Use cases](#use-cases) · [Examples](#examples) · [Install and update](#install-and-update) · [FAQ](#faq)

## Quick start

Run in a terminal. The default destination is `~/.agents/skills/design-patterns-refactor`:

```bash
git clone https://github.com/mengxiangsama/design-patterns-refactor.git
cd design-patterns-refactor
bash scripts/install.sh
```

Requires Git, Bash, and tar. Using the skill does not require Java, Maven, or Python. On Windows, use Git Bash or WSL in the same environment as your coding agent.

Then open **the project you want to analyze** in Codex and send:

```text
$design-patterns-refactor
Find high-value refactoring opportunities in the current module.
Compare direct simplification with design patterns, cite code, and explain trade-offs.
Use the project's language idioms. Do not edit code yet.
```

## Use cases

**Python / Go / TypeScript: native abstractions, not Java class hierarchies**

```text
$design-patterns-refactor
Analyze this Python export module, preferring functions and composition.
Preserve iteration timing, error propagation, and output format.
Propose a plan without editing code.
```

**Dead code: include redundancy inside active methods**

```text
$design-patterns-refactor
Clean up confirmed dead code in the current order module, including dead stores
and redundant conditions. Preserve effectful calls, dynamic entry points, and
public contracts. Implement the scoped cleanup and run relevant tests.
```

**Adapters: unify integrations while preserving contracts**

```text
$design-patterns-refactor
Refactor the shipping integration behind a common internal interface.
Preserve error mapping, units, and call counts. Make the changes and run regression tests.
```

**Microservices: boundaries, distributed transactions, and reliable messaging**

```text
$design-patterns-refactor
Review the order and inventory services' boundaries and message consistency.
Inspect commits, delivery, idempotency, retries, and compensation. Compare local
transactions, Outbox, or Saga using the provided repositories.
Give a design and verification plan. Do not edit or deploy yet.
```

Relevant tasks can cover service splits/merges, data ownership, Outbox/Saga/TCC, reconciliation, consumer groups, ordering, dead letters, and replay. Specify accessible repositories, participating services, and business constraints. Kubernetes, gateway or monitoring operations, and guessing hidden repositories are outside scope.

## Examples

An export pipeline supports plain text, compression, encoding, or compression followed by encoding. The repository demonstrates both Java decorators and Python function composition, not one structure imposed on every language.

| Example | Refactoring choice | Included tests |
| --- | --- | --- |
| [Java pricing](skills/design-patterns-refactor/assets/java-examples/src/main/java/examples/PricingCase.java) | Independently changing rules → strategies and registry | Precision, boundary inputs, duplicate registration |
| [Java shipping](skills/design-patterns-refactor/assets/java-examples/src/main/java/examples/ShippingCase.java) | Vendor interface → adapter | Units, errors, side-effect call counts |
| [Java export](skills/design-patterns-refactor/assets/java-examples/src/main/java/examples/ExportCase.java) | Optional processing → decorators | Order, byte equality, decoding |
| [Python export](skills/design-patterns-refactor/assets/python-examples/README.md) | Optional processing → plain function sequence | Four combinations, single-pass iteration, exceptions, order |

The Python `after` implementation preserves GZIP-before-Base64 ordering. Tests compare before/after bytes and independently decode the result. Keeping the original branches remains reasonable when the feature set is stable. Examples ship with the skill and do not connect to real business services.

The [selection guide](skills/design-patterns-refactor/references/pattern-selection.md) covers the 23 GoF patterns and selected architectural approaches; **it does not provide 23 implementations**. Separate [behavioral evaluation scenarios](evals/scenarios.md) include fixed Python cleanup, transaction recovery, and message-topology inputs. Passing example tests is not evidence of general model quality.

## Install and update

### Choose another location

From the cloned repository, pass the **parent skills directory**:

```bash
bash scripts/install.sh /path/to/your-project/.agents/skills
```

If your host uses `~/.codex/skills`, pass `"$HOME/.codex/skills"`. Avoid duplicate installations in scanned locations. See [official OpenAI discovery documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

### Optional skills CLI installation

With Node.js/npm installed, use the third-party [skills CLI](https://github.com/vercel-labs/skills) and select your agent and scope:

```bash
npx skills add mengxiangsama/design-patterns-refactor --skill design-patterns-refactor
```

The default is project scope; add `--global` for a user-wide installation. Choose either this method or the Bash installer, not duplicate copies. Installation paths, telemetry, and privacy controls belong to that CLI. Its support for multiple agents is not a compatibility certification for this skill. [skills.sh discovery](https://skills.sh/docs/faq) uses CLI installation telemetry, not GitHub stars; inclusion timing and ranking are not guaranteed.

### Update a Bash-installed copy

**`git pull` updates the repository, not an already copied skill installation.** From the repository, run:

```bash
git pull --ff-only
python3 scripts/update.py --check
python3 scripts/update.py
```

The updater requires Python 3.9+ and Git, with no third-party Python packages. For a custom destination, append the same skills parent directory to both update commands, such as `"$HOME/.codex/skills"`. On Windows, use `py -3` if `python3` is unavailable.

- `--check` identifies versions without writing files; an actual update compares installed files against repository history.
- Only recognized, unmodified copies can be updated. Added, edited, missing files or symlinks block updates; there is no force-overwrite option. Comparisons ignore generated `target`, `__pycache__`, and `.DS_Store` entries, but the original copy is backed up in full.
- The old directory is backed up under `skill-backups/` alongside the skills directory, outside skill scanning. Directory-switch failures and Ctrl+C trigger recovery attempts. After a hard process exit, check, update, and install commands detect the unfinished journal and request recovery.
- The default search covers the latest 100 commits touching the skill. Use `--from-ref <commit-or-tag>` for an older baseline; contents must still match exactly. Unknown versions require manual comparison.

**Update interrupted or installation directory missing?** Keep the backup and hidden update journal. From the repository, run:

```bash
python3 scripts/update.py --recover
python3 scripts/update.py --check
python3 scripts/update.py
```

Append the same skills parent directory to all three commands for a custom installation. On Windows, substitute `py -3` for `python3` if needed. Recovery validates the journal and file fingerprints: it restores the old copy if it was moved away, or finishes cleanup if the new copy is already fully active without rolling it back. Then check and update again. Manually changed files or invalid records are not overwritten and require inspection; backups from older updaters without a journal also require manual handling. A retained `.update.lock` file is normal: the OS releases the lock when the process exits, so do not delete the file.

For CLI-managed installations, use `npx skills update design-patterns-refactor`, not this repository's copy updater. Preserve customizations before using third-party update tools; their safety behavior is separate from this updater's guarantees.

## FAQ

**Installed but not visible?** Check that the installation contains `design-patterns-refactor/SKILL.md` and that your client scans its parent directory. Open the matching project for project-local installs. Windows and WSL home directories differ. Refresh the skill list or start a new session; restart the client if needed.

**Directory already exists?** The installer intentionally refuses to overwrite it. Do not delete it just to reinstall. Run the update check above or determine whether another installer manages it.

**I customized the skill. How do I update?** The updater stops instead of overwriting. Compare and merge your changes, or preserve your copy outside scanned paths before deciding to reinstall. The repository's skill source must also match its Git commit; uncommitted source is not treated as a released version.

**Will analysis edit my code?** Instructions require read-only analysis unless implementation is requested. A skill is not a security boundary; configure your host permissions appropriately.

**Does it upload my code?** The skill has no built-in external API or project-code upload logic. Code access, model processing, and third-party installer behavior depend on the respective client or service.

**Does it guarantee speed or safety?** No. Patterns are not performance optimizations by themselves. Review generated changes and run project-specific tests. Runnable Go/TypeScript examples are not yet bundled.

## Development and verification

From the repository root (macOS/Linux/WSL):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python -B -m unittest discover -s skills/design-patterns-refactor/assets/python-examples -v
.venv/bin/python -B -m unittest discover -s evals/fixtures/python_cleanup -v
.venv/bin/python -B -m unittest discover -s evals/fixtures/order_delivery -v
mvn -B -f skills/design-patterns-refactor/assets/java-examples/pom.xml verify
```

On native Windows, the virtual environment Python is `.venv\Scripts\python.exe`. Java examples target Java 8 bytecode; JDK 17+ and Maven 3.8+ are recommended for building. These are not skill-usage dependencies.

CI checks metadata/local links, install/update behavior, Python examples, and evaluation fixture baselines on Ubuntu, macOS, and Windows. Java examples run separately on Ubuntu with JDK 17/21. Installation tests cover Ctrl+C, hard exits at three directory-switch stages, and a fresh `core.autocrlf=true` clone; `.gitattributes` pins text files and shell scripts to LF. Windows tests use Git Bash and skip only the relevant symlink cases if the account lacks symlink privileges. Order-delivery baseline tests deliberately **reproduce original failures**, not a completed fix. Model behavior needs separate evaluation; these tests do not validate a real MQ cluster or production environment.

## Contributing and license

Sanitized feedback, language-native examples, and meaningful regression tests are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) and discuss substantial changes in [Issues](https://github.com/mengxiangsama/design-patterns-refactor/issues). Never submit confidential code, customer information, or credentials.

[Changelog](CHANGELOG.md) · [Skill instructions](skills/design-patterns-refactor/SKILL.md) · [MIT License](LICENSE)
