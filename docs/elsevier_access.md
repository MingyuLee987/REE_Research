# Elsevier 원문 API 진단 및 해결 절차

2026-10-15 실제 요청 8개로 진단했습니다. API 키 값은 문서나 로그에 포함하지 않았습니다.

| 점검 | 결과 |
| --- | --- |
| .env 키 형식 | 32자리 16진수 형식 정상, 앞뒤 공백 없음 |
| 프로세스의 오래된 키가 .env를 가림 | 없음 |
| X-ELS-APIKey 헤더, Bearer 오사용 여부 | 올바른 헤더 사용, Bearer 미사용 |
| 같은 키로 Scopus 검색 | HTTP 200 |
| 같은 키로 ScienceDirect 검색 | HTTP 200; 검색 일치 수와 원문 권한은 별개 |
| Article Retrieval DOI FULL XML | HTTP 403 |
| Article Retrieval DOI 기본 view | HTTP 403 |
| Article Retrieval DOI META JSON | HTTP 403 |
| Article Retrieval PII FULL XML | HTTP 403 |
| 공식 apiKey 쿼리 파라미터로 대체 | HTTP 403 |
| 구독 논문 Article Retrieval | HTTP 403 |
| 기관 토큰 | 아직 미설정 |

원문 서비스의 공통 응답은 다음과 같습니다.

```text
AUTHENTICATION_ERROR
Requestor configuration settings insufficient for access to this resource.
```

검색 서비스가 같은 키를 받아들이므로 키 전체가 무효하거나 누락됐다고 단정할 근거는 없습니다. 엔드포인트별 접근 설정이 원인일 가능성이 높습니다. 특정 기관 계약·키 설정 중 어느 항목이 부족한지는 개발자 계정 또는 Elsevier 지원팀의 확인이 필요합니다.

[Elsevier 공식 Article Retrieval 문서](https://dev.elsevier.com/documentation/ArticleRetrievalAPI.wadl)는 검증된 ScienceDirect/API 권한 또는 approved-integration 권한을 요구하고, API 키만으로 retrieval 권한을 부여하지 않는다고 명시합니다. 같은 문서에서 `X-ELS-APIKey`, `X-ELS-Insttoken`, `apiKey`, `FULL`/`META`를 확인했습니다. OA DOI도 이 Article Retrieval 경로로 요청합니다. 별도의 OA 전용 주소로 바꾸면 해결된다는 근거는 찾지 못했습니다.

## 코드에서 완료한 조치

- 검색과 원문 요청에서 공통 인증 헤더 생성 함수를 사용합니다.
- 키·기관 토큰의 앞뒤 공백을 제거합니다.
- 선택 설정 `ELSEVIER_INST_TOKEN`이 실제로 발급돼 있으면 `X-ELS-Insttoken` 헤더에 전달합니다. 빈 값이나 예제 토큰은 보내지 않습니다.
- 원문 오류에 출판사 상세 오류를 표시하며 키·토큰은 제거합니다.
- 응답을 파일로 저장할 때 키와 기관 토큰을 제거합니다.
- `.env`에 빈 `ELSEVIER_INST_TOKEN=` 항목을 준비했습니다. 토큰을 임의로 생성하지 않았습니다.

## 남은 외부 설정

1. [Developer Portal](https://dev.elsevier.com/)에 본인 계정으로 로그인해 이 키의 **ScienceDirect Article Retrieval API 접근 활성화/승인** 상태를 확인합니다. Scopus 검색 성공만으로 원문 접근 승인을 대신하지 않습니다.
2. 학교 도서관 전자자료 담당자 또는 Elsevier API 지원팀에 아래 재현 내용을 전달해 키의 requestor configuration과 API entitlement 확인을 요청합니다.
3. 기관 토큰이 필요한 환경인지 함께 확인하고, 발급되면 `.env`의 `ELSEVIER_INST_TOKEN`에 넣습니다. 기관 토큰이 모든 외부망·OA 요청에 무조건 필요한 것은 아니며, 토큰만으로 API 서비스 승인이 대체된다고 보장할 수 없습니다.
4. 교내망/VPN 환경이 바뀌거나 권한이 승인되면 동일 진단 명령을 재실행합니다.

포털 설정을 바꾸거나 지원 요청을 전송하지는 않았습니다. 현재 세션에서는 개발자 계정 관리 화면에 접근하지 않았고, 권한을 로컬 코드로 부여할 수는 없습니다.

## 지원 요청용 문안

```text
Subject: ScienceDirect Article Retrieval returns 403 requestor configuration error; searches return 200

I am conducting non-commercial academic research at POSTECH.
Using the same API key and execution environment:
- Scopus Search: HTTP 200
- ScienceDirect Search: HTTP 200
- Article Retrieval, DOI/PII, FULL/default/META, XML/JSON: HTTP 403
- Both X-ELS-APIKey header and the documented apiKey parameter give the same error.

Error:
AUTHENTICATION_ERROR
Requestor configuration settings insufficient for access to this resource.

Example OA article DOI: 10.1016/j.corcom.2022.06.004
PII: S2667266923000063
FULL DOI request ID: c7b4f0aa-09b6-40d1-b34b-668ddff9aa45
Scopus success request ID: af3c0083-2be3-4952-8635-e5861ecd53a8

Please check or enable the ScienceDirect Article Retrieval/API entitlement
and requestor configuration for my developer application.
Please also advise whether an institutional token is required for my environment.
I can identify my application securely through your authenticated support channel.
```

## 재시험

```powershell
uv run --no-sync python scripts/diagnose_elsevier.py
uv run --no-sync ree fetch-elsevier --doi 10.1016/j.corcom.2022.06.004 --output-dir data/raw/elsevier_retry
```

CLI 원문 명령의 상세 옵션은 `ree fetch-elsevier --help`로 확인합니다. [진단 JSON](../data/raw/elsevier_diagnostics/report.json)에 각 요청 ID와 상세 결과가 있습니다. 진단 스크립트는 `.env` 값을 우선 사용하고 기존 수집기는 일반적인 환경 변수 우선 규칙을 유지합니다.
