# 검증 기록

실행일: 2026-11-08. 아래는 이 저장소의 초기 공개본과 한글 서체 변경본에서 실제로 수행한 검사다. 채용 성과, 실제 ATS 통과율 또는 모든 편집기의 동일한 렌더 결과를 뜻하지 않는다.

## 스킬과 검사 도구

| 항목 | 결과와 범위 |
| --- | --- |
| 스킬 메타데이터 | 정식 스킬 검증기로 `name`, `description`, YAML과 이름 형식 검증 통과 |
| 자동화 테스트 | `python3 -m unittest discover -s tests -v`: 9개 테스트 통과. 표·셀 변경 추적의 7개 변형 사례 포함 |
| 테스트가 다룬 동작 | Word run 분할에 따른 거짓 변경 방지, 수치 변경 검출, 필수 문자열 누락, 지정 표의 경고 및 원본 바이트 보존, 다단·머리말·주석·변경 추적 감지, 거짓 숨김 설정 구별, 본문 순서 변경 검출, 표 속성·셀 삽입·삭제·병합의 변경 추적 검출 |
| 구현 순서 | 도구가 없을 때 7개 테스트의 실패를 확인한 뒤 검사기를 구현하고 다시 실행. 이것은 코드 검증 과정이며 스킬 자체의 효과 비교가 아님 |
| 시나리오 적용 | 지정 양식, 장기 경력, 이력서·작품집·학술 CV 구분의 세 사례 검토. 자세한 결과와 스킬 없는 기준 응답은 [평가 기록](../evaluations/results.md) 참조 |

검사기는 ZIP 안의 Word XML을 읽을 뿐 파일을 수정하지 않는다. `structural_status: clear`는 이 도구가 발견한 차단·경고 항목이 없다는 뜻이다. `visual_review`와 `ats_test`는 항상 별도로 남겨 자동 검사 범위를 드러낸다.

독립 코드 검토에서 표 관련 변경 추적 요소가 빠진 문제를 발견했다. `tcPrChange`, `trPrChange`, `tblGridChange`, `tblPrExChange`, `cellIns`, `cellDel`, `cellMerge`를 각각 넣은 사례가 기존 검사기에서 실패하는 것을 재현한 뒤 수정했다. Microsoft의 [셀 삭제 변경 추적](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.celldeletion?view=openxml-3.0.1) 및 [표 예외 속성 변경](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.tablepropertyexceptionschange?view=openxml-2.20.0) 문서로 요소의 의미를 확인했다. 최종 9개 테스트가 모두 통과했고 공개 예제 두 건의 구조 검사 결과도 유지됐다.

## 공개 예제

| 파일 | 최종 쪽수 | 디자인·시각 확인 |
| --- | --- | --- |
| [standard-resume.docx](../examples/standard-resume.docx) · [PDF](../examples/standard-resume.pdf) | 1 | 영문 일반형. 제목·이름·연락처, 경력과 학력의 정렬, 모든 줄의 잘림·겹침 여부 확인 |
| [experienced-manager-resume.docx](../examples/experienced-manager-resume.docx) · [PDF](../examples/experienced-manager-resume.pdf) | 2 | 한글 경력자형. 최근 경력·병행 역할과 이전 경력·프로젝트의 페이지 배분, 한글·영문 제품명·숫자, 모든 줄의 잘림·겹침 여부 확인 |

두 DOCX의 최종 수정본을 PDF로 변환하고 **세 페이지 모두 PNG로 렌더해 직접 확인했다.** 중간 경력자 예제는 4쪽으로 넘쳤다. 합성 자료의 예시 항목을 줄이고 문단 흐름을 정리한 뒤 2쪽으로 다시 렌더했다. 실제 지원자의 경력을 삭제한 작업이 아니다. 기본 템플릿에서 상속된 파란 제목선을 제거했고, 본문은 11 pt·줄 간격 1.10·여백 20 mm를 유지했다.

예제는 US Letter 세로 문서다. 이는 재현을 위한 예제 규격이며, 한국어 이력서를 항상 Letter로 제출하라는 뜻이 아니다. 실제 작업은 원본 또는 제출처의 A4·Letter 요구를 따른다.

### 내용·파일 확인

- 합성 JSON의 모든 표시 문단과 DOCX 본문을 순서대로 대조했다.
- `pdftotext` 기본 모드와 `-layout` 모드에서 모든 표시 문단이 원래 순서로 추출됨을 확인했다. 줄바꿈으로 생기는 공백을 정규화했으므로 띄어쓰기·보조 기술 검증의 대체물은 아니다.
- 두 DOCX에서 표·텍스트 상자·도형·다단·주석·변경 추적·숨김·고정 행 높이의 검사 결과는 모두 0이었다. 필수 이름과 도구명 문자열도 유지됐다.
- `pdfinfo`로 각각 1쪽·2쪽, Letter, PDF 1.7, `Tagged: yes`를 확인했다. 태그가 존재한다는 사실만으로 태그 품질이나 PDF/UA 적합성을 판정하지 않았다.
- `pdffonts`의 모든 글꼴 행에서 포함·부분 포함·Unicode 매핑을 확인했다. 영문은 Noto Sans Regular·Bold, 한글은 Pretendard Regular·SemiBold·Bold다.
- 연락처와 URL은 `example.org`를 사용하는 표시용 텍스트다. PDF의 활성 URI 링크는 0개이며, 클릭 목적지 검증은 해당하지 않는다. 실제 지원서에 링크를 추가하면 별도로 검수해야 한다.
- 최종 DOCX·PDF의 SHA-256과 자동 검사 결과는 [기계 판독 기록](example-checks.json)에 남겼다. 그 파일의 `visual_review: not_performed`는 구조 검사기 자체의 범위이며, 이 문서에 기록한 별도의 시각 검수와 구분한다.

### 한글 서체 변경 검증

한글 예제와 자유 형식 한글 문서의 기본값을 Noto Sans CJK KR에서 Pretendard로 바꿨다. 본문은 Regular 11 pt, 소제목은 SemiBold 11~12 pt, 이름은 Bold 22 pt다. 정적 OTF 1.3.9의 세 굵기를 공식 저장소 파일의 Git blob 해시와 대조한 뒤 설치했고, SemiBold는 별도 패밀리 이름을 사용해 합성 굵기를 피했다.

변경 전 공개 커밋 `a8ac06651242fb7248ba84902312e0e324b0ccb4`의 예제와 비교해 **모든 DOCX 문단의 문자열이 정확히 같음**을 확인했다. 합성 JSON의 표시 문단, PDF 기본·배치 모드의 추출 순서도 다시 대조했다. 두 예제를 다시 생성하고 세 페이지를 모두 시각 검수했다. 한글 예제는 2쪽이며 세 굵기가 모두 실제 PDF 글꼴 목록에 나타나고 포함·부분 포함·Unicode 매핑을 갖는다. 영문 DOCX의 ZIP 내부 파일은 변경 전과 같았고 영문 공개 산출물은 그대로 유지했다.

본문의 내용·수치·기간과 11 pt·줄 간격 1.10·여백 20 mm·용지 규격은 바꾸지 않았다. 위 9개 자동화 테스트는 초기 공개 검사기의 검증 기록이며, 이번 서체 수정에서는 검사기 코드를 변경하지 않았다.

### 재현 환경

- Python 3.12.14, `python-docx` 1.2.0.
- DOCX 변환: 제공된 문서 렌더러와 LibreOfficeDev 26.8.0.0.alpha0 (X86_64).
- PDF 확인: Poppler의 `pdfinfo`, `pdffonts`, `pdftotext`와 페이지 이미지.
- 글꼴 파일은 배포하지 않는다. DOCX를 다른 환경에서 열 때에는 설치 글꼴과 편집기 차이로 페이지 흐름이 달라질 수 있다.

## 수행하지 않은 검사

실제 회사의 원본 Word 양식을 사용한 회귀 검증, Microsoft Word 네이티브 화면 비교, 실제 채용 사이트 업로드·파싱, 스크린리더·키보드 사용성, PDF/UA·WCAG 전체 적합성, 인쇄물 검수, 채용 성과 비교는 수행하지 않았다. 지정 양식의 구조 보존은 지침·시나리오와 소규모 XML 테스트로만 확인했다. 이 구분을 실제 작업의 납품 기록에도 유지해야 한다.
