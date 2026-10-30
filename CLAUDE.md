# CLAUDE.md

이 프로젝트의 작업은 **코드 작업**과 **문서 작업** 두 축으로 이루어진다.

## 작업 시작 전 필수 절차

1. 모든 작업 전에 [문서 인덱스](docs/index.md)를 먼저 읽고, 현재 작업에 해당하는 문서를 찾아 읽는다.
2. 문서를 작성·수정할 때는 [문서 작업 규칙](docs/DocumentationRule.md)을 따른다.
3. 코드를 작성·수정할 때는 [코드 작업 규칙](docs/CodeRule.md)을 따른다.
4. 모든 작업은 [로드맵](docs/Roadmap.md)의 태스크(`M<n>-T<m>`) 또는 [이슈](docs/Issue.md)(`I<n>`, `H<n>`)의 ID로 시작하고 끝낸다. 시작·진행·완료 처리는 [작업 관리 규칙](docs/TaskRule.md)을 따른다. 사용자가 계획과 별도로 무언가를 지시하면 이슈로 등록한다.
5. 작업마다 작업 브랜치를 만들고, 커밋은 [커밋 규칙](docs/CommitRule.md)에 따라 작업 ID로 하며 바로 push한다. `main`에는 [PR 규칙](docs/PullRequestRule.md)에 따라 PR로만 합친다. 저장소를 새로 받으면 `git config core.hooksPath .githooks`로 커밋 메시지 검사 hook을 켠다.

## 핵심 원칙

- **문서가 우선이다.** 문서는 코드 작업의 규칙이다.
- **모든 규칙은 이 파일을 루트로 하는 프로젝트 문서에서만 관리한다.** Claude Code 메모리 같은 개인 메모리나 저장소 밖의 파일에 규칙을 두지 않는다. 상세는 [문서 작업 규칙](docs/DocumentationRule.md#1-문서-우선-원칙)에 있다.
- 기계적으로 검사할 수 있는 규칙을 새로 정하면, 그 검사기를 같은 작업 안에서 만든다.
- 코드를 변경하기 전에 관련 문서를 먼저 작성·수정하고, 그 다음 문서의 지시에 따라 코드를 작성한다.
- 코드를 먼저 변경한 뒤 문서를 코드에 맞추는 일은 하지 않는다.
- 문서에 근거가 없는 코드 변경이 필요하면, 코드를 건드리기 전에 문서부터 갱신한다.
- Python은 반드시 uv 환경에서 사용한다(`uv run`). 상세는 [코드 작업 규칙](docs/CodeRule.md#3-언어와-스타일)에 있다.

## 작업 완료 전 검증

작업을 마치기 전에 아래 명령을 저장소 루트에서 실행해 모두 통과시킨다. 상세는 [검증 도구](docs/VerificationTools.md)에 있다.

```sh
uv run python -m tools.check_docs
uv run python -m tools.check_pointers
uv run python -m tools.check_tasks
uv run python -m tools.check_commits
uv run python -m unittest discover -s tests -t .
```
