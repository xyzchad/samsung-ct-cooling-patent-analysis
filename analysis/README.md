# 11월 18일 인계본 재현

입력: `outputs/team1_20261109/` 원본·정제 CSV·기존 S커브 계산표. 공개 청구항 캐시는 `outputs/team2_20261117/evidence/`. 출력은 `outputs/team2_20261117/`이며 폴더 날짜는 최초 추가 검토일이다.

필요 패키지: Python 3, lxml(원문 수집), pandas·openpyxl(기존 Excel 읽기), matplotlib·numpy(그림). 원본을 수정하는 코드가 아니다. `figures_20261117.py`는 macOS의 Apple SD Gothic Neo를 사용하며 다른 운영체제에서는 설치된 한글 글꼴로 바꿔야 한다.

```bash
python analysis/fetch_claims_20261117.py
python analysis/complete_analysis_20261117.py
python analysis/code_claims_20261117.py
python analysis/figures_20261117.py
python analysis/validate_20261118.py
```

수집 단계는 저장된 캐시가 있으면 네트워크를 호출하지 않는다. `claims`는 번호 기준 중복 제거한 청구항, `claims_full_text`는 원문 섹션 확인용이다. JSON의 `document_dates_metadata`는 문서 날짜 메타데이터이며 최초 우선일 필드로 쓰면 안 된다.

`complete_analysis`의 기능군 정의와 제외·경계 태그는 분석자가 정한 규칙이다. `code_claims`의 20건 기능값도 청구항 1을 읽고 부여한 코딩이며 자동 법률 판단 결과가 아니다. 코딩 근거가 달라지면 해당 줄·정의·해석을 함께 수정하고 그래프를 다시 생성한다.

`validation.json`은 계산 일치와 근거 연결을 확인한다. 전체 검색의 재현율이나 모든 수작업 판단의 정확도를 증명하지 않는다. 청구항·사업자료 확인일 이후의 변화를 반영하려면 해당 출처를 새로 확인한다.
