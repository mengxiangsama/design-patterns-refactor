# Design Patterns Refactor

[中文](README.md) | [English](README.en.md)

**Help AI choose refactorings from real code—not force design patterns onto it.**

A Codex skill for tracing responsibilities and change points, comparing direct simplification with pattern-based alternatives, and planning or implementing scoped refactorings with compatibility checks.

- Evidence first: cite code locations and explain costs and benefits.
- No unnecessary abstractions: “no pattern needed” is a valid conclusion.
- Preserve behavior: distinguish structural changes from bug fixes, and report verification limits.

## Quick start

```bash
git clone https://github.com/mengxiangsama/design-patterns-refactor.git
cd design-patterns-refactor
bash scripts/install.sh
```

The installer needs Bash and tar. It defaults to `~/.agents/skills/design-patterns-refactor` and refuses to overwrite an existing installation. On Windows, use Git Bash or WSL. You do not need Java, Maven, or Python just to use the skill.

For a project-local installation:

```bash
bash scripts/install.sh /path/to/your-project/.agents/skills
```

If your host uses `~/.codex/skills`, pass that directory instead. Avoid duplicate installations in scanned locations. Check the skill list after installation and restart the client if it is not visible.

## Usage

Analyze without editing:

```text
$design-patterns-refactor
Find high-value refactoring opportunities in this project.
Compare direct simplification with design-pattern alternatives.
Cite code evidence, explain trade-offs, and prioritize recommendations. Do not edit code yet.
```

Implement a scoped change:

```text
$design-patterns-refactor
Refactor the shipping integration behind a common internal interface.
Preserve error handling, units, and external side effects. Run relevant regression tests.
```

Use language-native abstractions:

```text
$design-patterns-refactor
Analyze this Go module using idiomatic Go interfaces, functions, and composition.
Preserve context cancellation, errors, and concurrency behavior.
Do not copy Java-style class hierarchies. Propose a plan before editing.
```

## Scope and limits

The workflow is language-agnostic. The bundled executable examples currently use Java; Go, Python, and TypeScript examples are not yet included.

The [selection guide](skills/design-patterns-refactor/references/pattern-selection.md) covers the 23 GoF patterns and selected architectural approaches. This is guidance, not a claim that all patterns have executable examples. Three examples are provided: pricing strategies, shipping adapters, and export decorators. See [example documentation](skills/design-patterns-refactor/assets/java-examples/README.md).

Analysis requests should remain read-only. Implementation requires a request to make changes. These are agent instructions, not a security boundary. The skill has no built-in external API calls or automatic project-code upload; code access and model processing depend on your host environment.

Patterns do not guarantee performance, correctness, or security. Review changes and validate behavior with relevant tests and measurements.

## Development and verification

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
mvn -B -f skills/design-patterns-refactor/assets/java-examples/pom.xml verify
```

Java examples target Java 8 syntax/bytecode; building them requires JDK 17+ and Maven 3.8+. These dependencies are for example tests, not skill usage.

CI checks package metadata, local links, installation behavior, and Java examples. Passing these checks does not establish model behavior quality. [Evaluation scenarios](evals/scenarios.md) support manual behavioral evaluation.

## Contributing

Documentation fixes, sanitized usage feedback, regression tests, and language-native examples are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md), discuss substantial changes in [Issues](https://github.com/mengxiangsama/design-patterns-refactor/issues), and submit a focused PR.

[Changelog](CHANGELOG.md) · [MIT License](LICENSE)
