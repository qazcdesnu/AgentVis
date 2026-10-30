<!-- PR 제목: <작업 ID>[, <작업 ID>…]: <요약>  (docs/PullRequestRule.md) -->

## 작업

- 작업 ID:
- 설명(로드맵·이슈의 한 줄):

## 요약

<!-- 무엇을 왜 바꿨는지 몇 줄. 상세는 docs/Done.md 기록에 있다. -->

## 근거 문서

-

## 검증

```text
uv run python -m tools.check_docs
uv run python -m tools.check_pointers
uv run python -m tools.check_tasks
uv run python -m tools.check_commits
uv run python -m unittest discover -s tests -t .
```

<!-- 결과를 적는다. -->

## 확인 필요

<!-- 사용자가 결정하거나 직접 확인해야 할 것. 없으면 "없음". -->
