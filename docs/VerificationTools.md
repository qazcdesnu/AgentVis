# 검증 도구

이 문서는 문서와 코드의 규칙 준수를 자동으로 검증하는 도구를 규정한다. 도구는 `tools/` 패키지에 있으며 [코드 작업 규칙](CodeRule.md)에 따라 표준 라이브러리만 사용한다. 검증하는 규칙은 [문서 작업 규칙](DocumentationRule.md), [포인터 규약](Traceability.md), [작업 관리 규칙](TaskRule.md), [커밋 규칙](CommitRule.md), [웹 UI 설계의 저장소에 넣은 라이브러리](design/WebUI.md#11-저장소에-넣은-라이브러리)이다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

## 1. 실행 방법

모든 명령은 저장소 루트에서 uv 환경으로 실행한다([코드 작업 규칙](CodeRule.md#3-언어와-스타일)).

```sh
uv run python -m tools.check_docs        # 문서 링크와 고아 문서 검사
uv run python -m tools.check_pointers    # 문서 ↔ 코드 포인터 검사
uv run python -m tools.check_tasks       # 작업 ID 기준 작업 관리 문서 정합성 검사
uv run python -m tools.check_commits     # 기준 커밋 이후 커밋 메시지 검사
uv run python -m tools.check_web         # 웹 화면 파일의 외부 주소와 저장소에 넣은 라이브러리 검사
uv run python -m unittest discover -s tests -t .   # 도구 자체의 테스트
```

- 문제가 없으면 종료 코드 0으로 끝나고 통과 요약을 한 줄 출력한다.
- 문제가 있으면 문제마다 `<저장소 기준 경로>:<줄>: <메시지>` 형식으로 한 줄씩 출력하고 종료 코드 1로 끝난다.
- 모든 검사기는 `--root <경로>` 옵션으로 검사할 저장소 루트를 바꿀 수 있다. 기본값은 이 저장소의 루트다.

## 2. 공통 모듈

[tools/doclib.py](../tools/doclib.py)는 검사기들이 공유하는 프로젝트 구성 상수와 마크다운 해석 기능을 제공한다.

**프로젝트 구성 상수**

| 상수 | 값 | 의미 |
| --- | --- | --- |
| [REPO_ROOT](../tools/doclib.py#REPO_ROOT) | `tools/`의 상위 디렉터리 | 기본 저장소 루트 |
| [INDEX_DOC](../tools/doclib.py#INDEX_DOC) | `docs/index.md` | 고아 문서 판정의 출발점 |
| [ENTRY_DOC](../tools/doclib.py#ENTRY_DOC) | `CLAUDE.md` | 작업자가 가장 먼저 읽는 진입 문서 |
| [README_DOC](../tools/doclib.py#README_DOC) | `README.md` | 저장소 첫 화면의 팀 동료용 안내 문서 |
| [DOCS_DIR](../tools/doclib.py#DOCS_DIR) | `docs` | 문서 디렉터리 |
| [CODE_ROOTS](../tools/doclib.py#CODE_ROOTS) | `src`, `tools`, `tests` | 커버리지 검사 대상 코드 디렉터리 |
| [CODE_SUFFIXES](../tools/doclib.py#CODE_SUFFIXES) | `.py` | 코드 포인터로 취급하는 링크 대상 확장자 |

**자료형**

- [Problem](../tools/doclib.py#Problem): 검사에서 발견된 문제 하나. 파일 경로, 줄 번호, 메시지를 가지며 [Problem.format](../tools/doclib.py#Problem.format)으로 출력 형식 문자열을 만든다.
- [Link](../tools/doclib.py#Link): 문서에서 찾은 마크다운 링크 하나. 출처 문서, 줄 번호, 표시 이름, 원본 대상 문자열을 가진다.

**함수**

- [find_doc_files](../tools/doclib.py#find_doc_files): 검사 대상 문서 목록. `ENTRY_DOC`, `README_DOC`(있으면), `docs/` 아래의 모든 `.md` 파일이다.
- [find_code_files](../tools/doclib.py#find_code_files): `CODE_ROOTS` 아래의 모든 코드 파일 목록. 없는 디렉터리는 건너뛴다.
- [extract_links](../tools/doclib.py#extract_links): 문서 본문에서 링크를 찾는다. 이미지 링크(`![...](...)`), 펜스 코드 블록(```` ``` ````, `~~~`) 안, 인라인 코드 안의 링크는 제외한다.
- [is_external](../tools/doclib.py#is_external): `http://`, `https://`, `mailto:`로 시작하는 외부 링크인지 판정한다. 외부 링크는 검사하지 않는다.
- [resolve_link](../tools/doclib.py#resolve_link): 링크 대상을 (절대 경로, 앵커)로 나눈다. `#앵커`만 있는 링크는 출처 문서 자신을 가리킨다. 앵커는 URL 디코딩한다.
- [slugify](../tools/doclib.py#slugify): 제목 문자열을 앵커로 바꾼다. 규칙은 [문서 작업 규칙](DocumentationRule.md#3-링크-규칙)에 있다.
- [display_path](../tools/doclib.py#display_path): 출력용 경로 문자열. 저장소 루트 기준 상대 경로이며, 루트 밖이면 절대 경로다. [Problem.format](../tools/doclib.py#Problem.format)과 검사기 메시지가 함께 쓴다.
- [heading_anchors](../tools/doclib.py#heading_anchors): 문서의 모든 ATX 제목(`#` ~ `######`, 코드 블록 밖)의 앵커 집합. 같은 앵커가 반복되면 두 번째부터 `-1`, `-2`를 붙인다.
- [iter_prose_lines](../tools/doclib.py#iter_prose_lines): 펜스 코드 블록 밖의 줄을 (줄 번호, 줄)로 차례로 돌려준다. 펜스 줄 자체도 제외한다.
- [use_utf8_output](../tools/doclib.py#use_utf8_output): 표준 출력·오류를 UTF-8로 바꾼다. 각 검사기의 `main`이 시작할 때 부른다([운영체제 이식성](CodeRule.md#31-운영체제-이식성)). 출력이 파이프로 갈 때 Windows가 기본 인코딩을 써서 한글 메시지를 출력하지 못하는 것을 막는다.
- [strip_inline_code](../tools/doclib.py#strip_inline_code): 줄에서 인라인 코드 구간을 지운다. 여는 백틱 수와 같은 수의 백틱으로 닫힌 구간을 지운다.

## 3. 문서 링크 검사기

[tools/check_docs.py](../tools/check_docs.py)는 [문서 작업 규칙](DocumentationRule.md)의 링크 규칙과 고아 문서 금지 규칙을 검증한다.

- [check_links](../tools/check_docs.py#check_links): 모든 문서의 링크를 검사한다.
  - 외부 링크와 코드 파일 링크는 건너뛴다. 코드 파일 링크는 [포인터 검사기](#4-포인터-검사기)가 검사한다.
  - 대상 파일이나 디렉터리가 없으면 문제다.
  - 대상이 `.md` 문서이고 앵커가 있으면, 대상 문서에 그 앵커가 있어야 한다.
- [check_entry](../tools/check_docs.py#check_entry): `ENTRY_DOC`이 존재하고 `INDEX_DOC`으로 가는 링크를 가지는지 검사한다.
- [check_readme](../tools/check_docs.py#check_readme): `README_DOC`이 존재하고 `INDEX_DOC`과 `ENTRY_DOC`으로 가는 링크를 모두 가지는지 검사한다([문서 작업 규칙의 형식](DocumentationRule.md#2-형식)). 링크 자체는 `README_DOC`도 [find_doc_files](../tools/doclib.py#find_doc_files)에 들어가므로 `check_links`가 검사한다.
- [find_orphans](../tools/check_docs.py#find_orphans): `INDEX_DOC`에서 문서 간 링크를 따라 너비 우선 탐색을 하고, 도달하지 못한 `docs/` 아래 문서를 고아 문서로 보고한다. `INDEX_DOC`이 없으면 그 자체를 문제로 보고한다.
- [main](../tools/check_docs.py#main): 네 검사를 실행하고 결과를 [1. 실행 방법](#1-실행-방법)의 형식으로 출력한다.

## 4. 포인터 검사기

[tools/check_pointers.py](../tools/check_pointers.py)는 [포인터 규약](Traceability.md)을 검증한다.

**자료형**

- [SymbolRef](../tools/check_pointers.py#SymbolRef): 코드 심볼 하나를 (파일 절대 경로, 한정 이름)으로 나타낸다. 모듈 자체는 한정 이름이 빈 문자열이다. [SymbolRef.is_related](../tools/check_pointers.py#SymbolRef.is_related)는 [상호 참조 규칙](Traceability.md#5-상호-참조-규칙)의 "관련 있다"를 판정한다.
- [CodePointer](../tools/check_pointers.py#CodePointer): 문서 → 코드 포인터. 출처 문서, 줄, 대상 심볼을 가진다.
- [DocPointer](../tools/check_pointers.py#DocPointer): 코드 → 문서 포인터. 출처 심볼, 줄, 대상 문서 절대 경로, 앵커를 가진다.
- [ModuleIndex](../tools/check_pointers.py#ModuleIndex): 코드 파일 하나를 AST로 분석한 결과. 한정 이름 → AST 노드 사전(`symbols`), 그 파일의 코드 → 문서 포인터 목록(`doc_pointers`), 분석 중 발견한 문제 목록(`problems`)을 가진다.

**함수**

- [index_module](../tools/check_pointers.py#index_module): 코드 파일을 AST로 파싱해 `ModuleIndex`를 만든다.
  - 심볼: 모듈의 클래스·함수를 중첩까지 모두 등록한다. 대입문은 모듈 수준과 클래스 수준의 것만 등록한다.
  - docstring 포인터: 모듈·클래스·함수 docstring의 `@doc:` 줄을 찾는다. 줄 번호는 docstring 시작 줄에 docstring 안의 줄 위치를 더한 값이다.
  - 주석 포인터: `tokenize`로 주석을 찾고, [포인터 규약](Traceability.md#3-코드에서-문서로-가는-포인터)에 따라 소속 심볼을 정한다. 소속 심볼이 없으면 문제다.
  - 문법 오류로 파싱할 수 없으면 그 자체를 문제로 보고한다.
- [collect_code_pointers](../tools/check_pointers.py#collect_code_pointers): 모든 문서에서 코드 포인터를 모으고 검사한다. 대상 파일이 없거나, 앵커가 줄 번호 형식(`L` 뒤에 숫자)이거나, AST에 해당 한정 이름이 없으면 문제다.
- [check_doc_pointers](../tools/check_pointers.py#check_doc_pointers): 코드 → 문서 포인터의 대상 문서와 앵커가 존재하는지 검사한다.
- [check_coverage](../tools/check_pointers.py#check_coverage): [커버리지 규칙](Traceability.md#4-커버리지-규칙)을 검사한다.
- [check_reciprocity](../tools/check_pointers.py#check_reciprocity): [상호 참조 규칙](Traceability.md#5-상호-참조-규칙)을 두 방향 모두 검사한다.
- [main](../tools/check_pointers.py#main): `CODE_ROOTS`의 코드 파일과 문서가 가리키는 코드 파일을 모두 분석하고, 위 검사를 실행해 결과를 [1. 실행 방법](#1-실행-방법)의 형식으로 출력한다.

## 5. 테스트

각 도구의 동작은 아래 테스트가 검증한다. 테스트는 임시 디렉터리에 작은 저장소를 만들어 `--root`와 같은 방식으로 검사기를 실행한다.

- [tests/support.py](../tests/support.py): 테스트 공통 기반. [RepoTestCase](../tests/support.py#RepoTestCase)는 테스트마다 임시 저장소 루트(`self.root`)를 만들고 지우며, [RepoTestCase.write](../tests/support.py#RepoTestCase.write)로 그 아래에 파일을 만든다.
- [tests/test_doclib.py](../tests/test_doclib.py): 링크 추출(코드 블록·인라인 코드·이미지 제외), 앵커 생성(한글, 중복 제목).
- [tests/test_check_docs.py](../tests/test_check_docs.py): 깨진 링크, 없는 앵커, 고아 문서, 진입 문서 누락, README 누락과 필수 링크 누락, 정상 저장소.
- [tests/test_check_pointers.py](../tests/test_check_pointers.py): 정상 양방향 포인터, 없는 심볼, 줄 번호 포인터, 주석 포인터, 소속 없는 주석 포인터, 커버리지 누락, 역방향 포인터 누락.
- [tests/test_check_tasks.py](../tests/test_check_tasks.py): 정상 저장소, 형식 오류, 번호 누락, 상태와 기록의 불일치, 연결 작업, 기록 필드·절 누락, 완료 순서, `없음` 규칙, 알 수 없는 ID 참조(한글 조사가 붙은 ID 포함).
- [tests/test_check_commits.py](../tests/test_check_commits.py): 정상 메시지(여러 ID, 트레일러, 주석 줄), 제목 형식·길이·마침표·빈 줄 오류, 없는 ID, 시작하지 않은 ID, 임시 git 저장소의 이력 검사와 기준 커밋·병합 커밋 제외, 브랜치 이름 형식과 없는 ID, PR 제목·브랜치 검사 명령.
- [tests/test_check_web.py](../tests/test_check_web.py): 정상 저장소, 외부 주소(절대·프로토콜 상대), 허용된 XML 이름공간 주소, `vendor/` 안 파일 제외, 표에 없는 `vendor/` 파일, 해시 불일치, 표에 있으나 없는 파일.

## 6. 작업 관리 검사기

[tools/check_tasks.py](../tools/check_tasks.py)는 [작업 관리 규칙](TaskRule.md)을 작업 ID 기준으로 검증한다. 해석하는 문서 형식은 [작업 관리 규칙의 문서 형식](TaskRule.md#6-문서-형식)에 있다.

**상수**

| 상수 | 값 |
| --- | --- |
| [ROADMAP_DOC](../tools/check_tasks.py#ROADMAP_DOC) | `docs/Roadmap.md` |
| [ISSUE_DOC](../tools/check_tasks.py#ISSUE_DOC) | `docs/Issue.md` |
| [ONGOING_DOC](../tools/check_tasks.py#ONGOING_DOC) | `docs/Ongoing.md` |
| [DONE_DOC](../tools/check_tasks.py#DONE_DOC) | `docs/Done.md` |

**자료형**

- [WorkItem](../tools/check_tasks.py#WorkItem): 로드맵의 태스크 또는 이슈 하나. ID, 상태 문자(` `, `~`, `x`), 출처 문서, 줄, 연결 작업 ID(없으면 `None`)를 가진다.
- [Record](../tools/check_tasks.py#Record): 진행 중·완료 문서의 기록 하나. ID, 출처 문서, 줄, 필드 사전, 절 이름 집합을 가진다.

**함수**

- [parse_roadmap](../tools/check_tasks.py#parse_roadmap): 로드맵에서 태스크를 읽는다. 형식에 맞지 않는 `- [` 줄과 `##` 제목, 마일스톤 밖이나 다른 마일스톤 아래의 태스크, 차례가 맞지 않는 마일스톤·태스크 번호를 문제로 보고한다.
- [parse_issues](../tools/check_tasks.py#parse_issues): 이슈 문서에서 이슈와 연결 작업을 읽는다. 형식 오류와 접두어별 번호 차례를 검사한다.
- [parse_records](../tools/check_tasks.py#parse_records): 진행 중 또는 완료 문서에서 기록을 읽는다. 작업 ID로 시작하지 않는 `##` 제목과 같은 문서 안의 중복 기록을 문제로 보고한다.
- [check_states](../tools/check_tasks.py#check_states): 상태와 기록의 대응을 검사한다.
  - 로드맵과 이슈 전체에서 ID는 하나뿐이어야 한다.
  - 연결 작업이 없는 항목: `[~]`이면 진행 중 기록만, `[x]`이면 완료 기록만 있어야 하고, `[ ]`이면 어느 기록도 없어야 한다.
  - 연결 작업이 있는 항목: 연결 작업이 존재하고 그 자신은 연결 작업이 없어야 하며, 상태가 연결 작업과 같고, 자체 기록이 없어야 한다.
  - 로드맵·이슈에 없는 ID의 기록은 문제다.
- [check_records](../tools/check_tasks.py#check_records): 기록의 필수 필드·절, 날짜 형식, 완료 기록의 순서(`완료일`이 늦은 것부터), 진행 중 문서의 `없음` 규칙을 검사한다.
- [check_references](../tools/check_tasks.py#check_references): 작업 관리 문서 네 개의 본문(코드 블록·인라인 코드 제외)에 나온 작업 ID가 모두 존재하는지 검사한다. ID 앞뒤가 영문자·숫자·`-`가 아니면 ID로 인식하므로 `M0-T6으로`처럼 한글 조사가 붙어도 찾는다.
- [main](../tools/check_tasks.py#main): 네 문서를 읽어 위 검사를 실행하고 결과를 [1. 실행 방법](#1-실행-방법)의 형식으로 출력한다. 문서가 없으면 그 자체를 문제로 보고한다.

## 7. 커밋 검사기

[tools/check_commits.py](../tools/check_commits.py)는 [커밋 규칙](CommitRule.md)의 메시지 형식을 검증한다. 두 가지 방식으로 실행한다.

| 방식 | 명령 | 검사 대상 | 작업 상태 확인 |
| --- | --- | --- | --- |
| 이력 검사 | `uv run python -m tools.check_commits` | `BASELINE_COMMIT` 이후의 병합이 아닌 모든 커밋 | ID 존재만 확인 |
| 커밋 시점 검사 | `uv run python -m tools.check_commits --message-file <파일>` | 작성 중인 커밋 메시지 하나 | ID가 `[~]` 또는 `[x]`인지까지 확인 |
| PR 검사 | `uv run python -m tools.check_commits --subject <PR 제목> --branch <브랜치 이름>` | PR 제목과 작업 브랜치 이름([PR 규칙](PullRequestRule.md)) | 제목은 시작 여부까지, 브랜치는 ID 존재만 확인 |

커밋 시점 검사는 `.githooks/commit-msg`가 호출한다. 이력 검사에서 작업 상태를 확인하지 않는 이유는, 지금 문서의 상태가 그 커밋 당시의 상태와 다를 수 있기 때문이다. 작업 ID는 지워지지 않으므로 존재 여부는 지금 문서로 확인할 수 있다.

**상수**

- [BASELINE_COMMIT](../tools/check_commits.py#BASELINE_COMMIT): `2a80e26`. 이 커밋과 그 이전 커밋은 검사하지 않는다([커밋 규칙의 예외](CommitRule.md#4-예외)).
- [SUBJECT_MAX_LENGTH](../tools/check_commits.py#SUBJECT_MAX_LENGTH): `72`

**함수**

- [work_statuses](../tools/check_commits.py#work_statuses): [로드맵](Roadmap.md)과 [이슈](Issue.md)를 [작업 관리 검사기](#6-작업-관리-검사기)의 해석 함수로 읽어 작업 ID → 상태 문자 사전을 만든다.
- [parse_subject](../tools/check_commits.py#parse_subject): 제목 줄을 (작업 ID 목록, 요약)으로 나눈다. 형식에 맞지 않으면 `None`.
- [check_message](../tools/check_commits.py#check_message): 메시지 하나를 검사해 문제 문장 목록을 돌려준다.
  - `#`으로 시작하는 줄(git 주석)은 지우고 검사한다.
  - 빈 메시지, 제목 형식 오류, 제목 길이 초과, 마침표로 끝나는 요약, 제목 다음 줄이 비어 있지 않음, 제목 안의 중복 ID, 로드맵·이슈에 없는 ID를 보고한다.
  - 시작 여부 확인을 켜면 상태가 `[ ]`인 ID도 보고한다.
- [commit_messages](../tools/check_commits.py#commit_messages): `git log --no-merges`로 주어진 범위의 (짧은 해시, 메시지) 목록을 읽는다. git 명령이 실패하면 예외를 낸다.
- [check_branch](../tools/check_commits.py#check_branch): 브랜치 이름이 `<작업 ID 소문자>-<설명>`(설명은 영문 소문자·숫자를 `-`로 이음)인지, 그 작업 ID가 로드맵·이슈에 있는지 검사해 문제 문장 목록을 돌려준다.
- [main](../tools/check_commits.py#main): `--message-file`이 있으면 커밋 시점 검사를, `--subject`·`--branch`가 있으면 PR 검사를(제목은 시작 여부 확인을 켠 `check_message`로), 셋 다 없으면 `BASELINE_COMMIT..HEAD` 이력 검사를 한다. 결과를 [1. 실행 방법](#1-실행-방법)의 형식으로 출력하며, 커밋 문제의 위치는 `commit <짧은 해시>:1`로 표시한다. 기준 커밋이 저장소에 없는 등 git 오류가 나면 그 자체를 문제로 보고한다.

## 8. CI

[.github/workflows/verify.yml](../.github/workflows/verify.yml)은 GitHub Actions에서 [1. 실행 방법](#1-실행-방법)의 검증 명령을 모두 실행한다. [PR 규칙](PullRequestRule.md#5-ci)이 이 CI를 쓴다.

- 실행 시점: PR이 열리거나 갱신될 때, `main`에 push될 때.
- 실행 환경: `ubuntu-latest`, `macos-latest`, `windows-latest` 세 곳에서 같은 검증을 돌린다([운영체제 이식성](CodeRule.md#31-운영체제-이식성)). 한 곳이 실패해도 나머지는 끝까지 돌려 실패한 운영체제를 모두 보인다(`fail-fast: false`). PR 제목·브랜치 검사와 PR 순서 검사는 운영체제와 무관하므로 Linux에서만 돌린다. Windows에서는 셸을 `bash`(Git for Windows)로 맞춘다.
- 커밋 이력 검사가 기준 커밋까지 볼 수 있도록 전체 이력을 받는다(`fetch-depth: 0`).
- Python은 `astral-sh/setup-uv`로 설치한 uv가 `.python-version`에 따라 준비한다.
- PR에서는 PR 제목과 브랜치 이름을 [커밋 검사기](#7-커밋-검사기)의 PR 검사로, 앞선 열린 PR 포함 여부를 [PR 순서 검사기](#9-pr-순서-검사기)로 확인한다. 열린 PR 목록은 GitHub CLI(`gh pr list`)와 워크플로의 `GITHUB_TOKEN`으로 받는다.
- CI는 Linux에서 돈다. 파일 이름의 대소문자를 구분하므로, macOS에서 통과한 대소문자가 다른 링크도 여기서 실패한다(I12).

## 9. PR 순서 검사기

[tools/check_pr_order.py](../tools/check_pr_order.py)는 [PR 규칙](PullRequestRule.md#4-병합)의 "PR 번호 순서대로 병합하면 충돌이 없다"를 지키기 위해, 검사하는 PR이 번호가 앞선 열린 PR의 커밋을 모두 포함하는지 확인한다. CI의 PR 실행에서만 쓴다.

```sh
gh pr list --state open --json number,headRefName,headRefOid > open-prs.json
uv run python -m tools.check_pr_order --pr <PR 번호> --open-prs open-prs.json
```

- [missing_earlier_prs](../tools/check_pr_order.py#missing_earlier_prs)`(root, open_prs, number) -> list[dict]`: 열린 PR 중 번호가 `number`보다 작고, 그 PR의 마지막 커밋(`headRefOid`)이 `HEAD`의 조상이 아닌 PR들을 돌려준다. 조상 여부는 `git merge-base --is-ancestor`로 판정하며, 커밋이 저장소에 없어도 포함하지 않은 것으로 본다.
- [main](../tools/check_pr_order.py#main): 빠진 PR마다 `PR #<번호> (<브랜치>)를 포함하지 않음` 문제를 [1. 실행 방법](#1-실행-방법)의 형식으로 출력한다. 위치는 `PR #<검사하는 번호>:1`이다.
- 테스트: [tests/test_check_pr_order.py](../tests/test_check_pr_order.py)가 임시 git 저장소로 쌓인 브랜치(포함)와 `main`에서 따로 만든 브랜치(빠짐), 번호가 뒤인 PR은 무시함, 저장소에 없는 커밋을 확인한다.


## 10. 웹 정적 파일 검사기

[tools/check_web.py](../tools/check_web.py)는 [웹 UI 설계의 저장소에 넣은 라이브러리](design/WebUI.md#11-저장소에-넣은-라이브러리) 규칙 중 기계적으로 확인할 수 있는 부분을 검사한다.

```sh
uv run python -m tools.check_web
```

| 상수 | 값 | 의미 |
| --- | --- | --- |
| [WEB_DIR](../tools/check_web.py#WEB_DIR) | `src/agentvis/web` | 화면 파일 디렉터리 |
| [VENDOR_DIR](../tools/check_web.py#VENDOR_DIR) | `src/agentvis/web/vendor` | 저장소에 넣은 라이브러리 디렉터리 |
| [WEB_DOC](../tools/check_web.py#WEB_DOC) | `docs/design/WebUI.md` | 라이브러리 표가 있는 문서 |
| [ALLOWED_URLS](../tools/check_web.py#ALLOWED_URLS) | SVG·XLink·XHTML의 XML 이름공간 주소 | 요청이 아니라 식별자로만 쓰는 주소 |

- [external_references](../tools/check_web.py#external_references)`(root) -> list[Problem]`: `WEB_DIR` 아래에서 `vendor/` 밖에 있는 `.html`, `.js`, `.css` 파일을 줄마다 읽어 아래 외부 주소를 찾는다. 라이브러리 파일은 내용을 고치지 않으므로(그 안의 주소 문자열은 우리가 통제하지 않는다) 검사하지 않는다.
  - `http://`·`https://` 주소. 단, `ALLOWED_URLS`로 시작하는 주소는 제외한다.
  - `src=`, `href=`, `url(`, `import`, `from` 뒤에 따옴표·괄호를 건너뛰고 `//`로 시작하는 프로토콜 상대 주소.
- [vendor_problems](../tools/check_web.py#vendor_problems)`(root) -> list[Problem]`: `WEB_DOC`의 표 줄 중 첫 칸이 `VENDOR_DIR` 안 파일로 가는 링크이고 마지막 칸이 64자리 16진수 인라인 코드인 줄을 라이브러리 항목으로 읽는다. 아래 경우를 문제로 낸다.
  - 항목 파일의 SHA-256이 표와 다르다.
  - 항목 파일이 없다.
  - `VENDOR_DIR`의 파일이 어떤 항목 줄에도 링크되지 않았다. 라이선스 파일처럼 첫 칸이 아닌 칸에 링크된 파일도 항목 줄에 있으면 된다.
- [main](../tools/check_web.py#main): 두 검사의 문제를 [1. 실행 방법](#1-실행-방법)의 형식으로 출력한다. 통과하면 검사한 화면 파일 수와 라이브러리 수를 출력한다.
