# PR 규칙

이 문서는 작업 브랜치, push, PR(pull request), 병합, CI 검증 규칙을 정한다. 모든 변경은 작업 ID별 브랜치에서 만들어 PR로 `main`에 합친다. 커밋 메시지 형식은 [커밋 규칙](CommitRule.md)에, 작업 ID와 상태는 [작업 관리 규칙](TaskRule.md)에 있다. 이 규칙의 기계적으로 검사할 수 있는 부분은 [커밋 검사기](VerificationTools.md#7-커밋-검사기), [PR 순서 검사기](VerificationTools.md#9-pr-순서-검사기), [CI](VerificationTools.md#8-ci)가 검증한다. 전체 문서 목록은 [문서 인덱스](index.md)에서 확인한다.

원격 저장소는 `git@github-qazcdesnu:qazcdesnu/AgentVis.git`(`origin`)이다.

## 1. 브랜치

- `main`은 합쳐진 결과만 두는 브랜치다. `main`에 직접 커밋하지 않는다.
- 작업(로드맵 태스크 또는 이슈)을 시작하면 작업 브랜치를 만든다. 출발점은 **아직 병합되지 않은 가장 최근 작업 브랜치**이고, 그런 브랜치가 없으면 최신 `main`이다. 이렇게 브랜치를 쌓으면 각 PR이 앞선 PR의 커밋을 모두 포함하므로, [4. 병합](#4-병합)의 순서대로 합칠 때 충돌이 생기지 않는다.
  - 브랜치를 쌓는 이유: 모든 작업이 작업 관리 문서(로드맵, 이슈, 진행 중, 완료)를 고치고, 특히 [완료](Done.md)는 항상 맨 위에 기록을 넣는다. 각 브랜치를 `main`에서 따로 만들면 앞 PR이 병합되는 순간 뒤 PR이 같은 자리에서 충돌한다.
- 브랜치 이름은 `<작업 ID 소문자>-<설명>`이다. 설명은 영문 소문자·숫자를 `-`로 이은 짧은 말이다.
  - 예: `m3-t2-analysis-model`, `i18-attachment-records`, `h3-collector-crash`
  - 여러 작업을 함께 처리하면 대표 작업 ID 하나를 쓴다.
- 브랜치 이름의 작업 ID는 로드맵이나 이슈에 있어야 한다.

## 2. 커밋과 push

- 작업 브랜치의 커밋도 [커밋 규칙](CommitRule.md)을 따른다.
- 커밋하면 바로 원격에 push한다(`git push`, 처음에는 `git push -u origin <브랜치>`). 작업이 이 컴퓨터에만 남지 않게 하기 위해서다.

## 3. PR

**단위와 시점**

- PR 하나는 작업 브랜치 하나, 즉 작업 하나(또는 함께 처리한 몇 개의 작업)다.
- PR의 대상(base)은 항상 `main`이다. 앞 PR이 병합되기 전까지는 뒤 PR의 변경 목록에 앞 PR의 커밋도 함께 보인다.
- 작업을 [완료 처리](TaskRule.md#43-완료)하고 검증을 통과한 뒤 PR을 연다. 진행 중에 보여 줄 것이 있으면 초안(draft) PR로 연다.

**제목**: 커밋 제목과 같은 형식 `<작업 ID>[, <작업 ID>…]: <요약>`이다([커밋 규칙의 메시지 형식](CommitRule.md#3-메시지-형식)). GitHub가 병합 커밋 제목 끝에 붙이는 ` (#번호)`까지 72자 안에 들도록 요약을 짧게 쓴다.

**본문**: [PR 템플릿](../.github/pull_request_template.md)을 채운다.

| 항목 | 내용 |
| --- | --- |
| 작업 | 작업 ID와 [로드맵](Roadmap.md)·[이슈](Issue.md)의 한 줄 설명 |
| 요약 | 무엇을 왜 바꿨는지 몇 줄. 상세는 [완료](Done.md) 기록에 있으므로 반복하지 않는다. |
| 근거 문서 | 이 변경을 규정한 문서 |
| 검증 | 실행한 검증 명령과 결과 |
| 확인 필요 | 사용자가 결정하거나 직접 확인해야 할 것 |

**만들기**: GitHub CLI로 만든다(`gh pr create --base main --title "<제목>" --body-file <본문 파일>`). GitHub CLI 로그인은 사용자가 `gh auth login`으로 한다. 로그인되어 있지 않으면 작업 브랜치를 push할 때 GitHub가 출력하는 PR 생성 링크로 사용자가 연다.

## 4. 병합

- **merge commit**("Create a merge commit")으로 합친다. squash merge나 rebase merge는 커밋을 새로 만들어, 그 커밋을 이미 포함한 뒤 PR과 내용이 겹쳐 충돌할 수 있으므로 쓰지 않는다. `main`의 병합 커밋(`Merge pull request #…`)은 [커밋 이력 검사](VerificationTools.md#7-커밋-검사기)에서 제외되고, 작업 커밋들은 커밋 규칙을 따른다.
- **PR 번호 순서대로** 병합한다. 앞 PR을 건너뛰고 뒤 PR을 병합하지 않는다.
- 병합은 사용자가 한다. Claude는 사용자가 요청할 때만 병합한다.
- CI가 통과하지 않은 PR은 병합하지 않는다.
- 병합한 뒤 작업 브랜치는 지우고, 로컬 `main`을 원격과 맞춘다(`git switch main && git pull`).

**앞 PR을 고쳐야 할 때**: 뒤 브랜치가 쌓여 있는 상태에서 앞 PR을 고치면, 앞 브랜치에 고친 커밋을 올린 뒤 뒤 브랜치들에 차례로 앞 브랜치를 병합(`git merge`)하고 push한다. rebase로 이력을 바꾸지 않는다. 이미 push된 커밋을 바꾸면 쌓인 브랜치들이 서로 어긋나기 때문이다.

## 5. CI

PR과 `main` push마다 GitHub Actions의 [CI](VerificationTools.md#8-ci)가 [검증 도구](VerificationTools.md#1-실행-방법) 전체를 실행한다. PR에서는 PR 제목과 브랜치 이름, 그리고 그 PR이 번호가 앞선 열린 PR을 모두 포함하는지([PR 순서 검사기](VerificationTools.md#9-pr-순서-검사기))도 검사한다.

GitHub 저장소 설정에서 `main` 보호 규칙(PR 필수, CI 통과 필수)을 켜 두면 이 규칙이 저장소 차원에서 강제된다. 이 설정은 사용자가 GitHub에서 한다.
