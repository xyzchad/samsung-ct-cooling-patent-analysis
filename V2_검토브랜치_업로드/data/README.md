# 데이터·근거 자료

발표용 파일은 [deliverables/](../deliverables/)에 있습니다. 이 폴더는 원자료에서 최종 수치까지 추적할 때 사용합니다.

| 폴더 | 내용 | 사용 기준 |
|---|---|---|
| [raw/lens_us/](raw/lens_us/) | 미국 Lens 원본 export 5개 | 검색일 2026-11-09, 미국 Filed 2000–2024 |
| [raw/kipris/](raw/kipris/) | 국내 건설사·계열사 후보 전사 TSV | 검색일 2026-11-08. 화면에서 전사한 자료 |
| [raw/patent_claims/](raw/patent_claims/) | 미국 20건·보완 사례·국내 2건 청구항 JSON | URL·확인일·원문 해시 포함 |
| [searches/](searches/) | 실제 검색식·국내 보완 검색 기록 | 미국 입력식과 국내 실행식을 구별 |
| [processed/us_baseline/](processed/us_baseline/) | 팀원1의 정제·표본·제외 기록 | 최초 분석 기준 DLC 451·액침 163 |
| [processed/us_reviewed/](processed/us_reviewed/) | 추가 관련성 검토를 반영한 패밀리 | 키워드(V1) 기준 DLC 447·액침 163, 중복 21 |
| [v2/](v2/) | V2: 키워드 + CPC 검색 판정·결과표 ([README](v2/README.md)) | **V2 기준 DLC 1,874·액침 658**, 중복 37 |
| [raw/lens_us/v2/](raw/lens_us/v2/) | V2 CPC 검색 원자료 10개 (2026-11-20, 압축) | 패밀리 5 · 등록 5 |
| [results/final/](results/final/) | 최신 추이·HHI·CPC·청구항·민감도 계산표 | 발표 수치는 이 버전을 사용 |
| [results/baseline/](results/baseline/) | 팀원1의 보조 계산 결과 | 과거 기준과 비교할 때 사용 |
| [reference/](reference/) | 근거 Excel·미국 핵심특허 선정 목록 | 원본 계산·선정 근거 보존 |

## 자주 찾는 파일

- [20건 청구항 기능 코딩](results/final/US_claim1_review_20.csv)
- [원본·추가 검토·경계 제외 민감도](results/final/metrics_comparison.csv)
- [기능별 CPC 계산](results/final/cpc_corrected.csv)와 [정의](results/final/cpc_definitions.csv)
- [추가 제외·경계 판정](results/final/screening_rechecks.csv)
- [미국 선정 20건 Excel](reference/us_core_patents.xlsx)
- [국내 KIPRIS 근거 Excel](reference/kr_patent_evidence.xlsx)
- [팀원1 원래 정량 계산 Excel](reference/us_baseline_analysis.xlsx)
- [시설 보완 검색 Excel](reference/us_facility_analysis.xlsx)

두 미국 검색군은 상호 배타적 분류가 아닙니다. 원자료·기준본·최종 검토본의 분모를 섞지 마세요. 잘못된 공개일 필터로 받았던 첫 export는 [별도 보관](../archive/2026-11-08_wrong_date_filter/)했습니다.
