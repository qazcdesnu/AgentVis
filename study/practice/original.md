`total([100.0], "save10")`가 90.0이 아니라 100.0을 돌려줍니다. 할인 코드는 대소문자를 가리지 않아야 하는데 `discount.py`의 `apply_discount`가 코드를 그대로 조회하는 것 같으니 고쳐 주세요. 테스트는 `python3 -m unittest discover -s tests -t .`로 돌립니다.
