# 기존 스킬·템플릿 조사

확인일: 2026-11-08. 검색으로 후보를 찾은 뒤 원 저장소의 실제 파일을 확인했다. 아래 비교는 확인한 문서와 코드의 범위에 한정한다. 설치 수·별 수를 품질이나 채용 효과의 증거로 사용하지 않았다.

## 직접 확인한 사례

| 사례 | 확인한 기능과 참고점 | 이 요청과의 차이 | 확인한 라이선스 |
| --- | --- | --- | --- |
| [ResumeSkills — resume-formatter](https://github.com/Paramchoudhary/ResumeSkills/blob/main/skills/resume-formatter/SKILL.md) | 실제 Agent Skill. 시각적 위계, 글꼴·여백, 일관성, 분량과 파일 형식에 관한 실무 체크리스트가 상세함 | 확인한 스킬 본문은 서식 조언이 중심. 한글 글꼴 슬롯, 회사 지정 표 보존, 최종 DOCX의 실행 가능한 구조 검사까지 다루지는 않음. 경력 연수별 쪽수와 특정 형식의 ATS 우위는 보편 규칙으로 가져오지 않음 | [MIT](https://github.com/Paramchoudhary/ResumeSkills/blob/main/LICENSE) |
| [Codex resume tailoring — tailor-one-page-resume](https://github.com/stevenha75/codex-resume-tailoring-skill/blob/main/skill/tailor-one-page-resume/SKILL.md) | 실제 Agent Skill. 지원 공고와 근거를 연결하고, JSON을 Chromium PDF로 렌더한 뒤 페이지·텍스트·글꼴·시각 결과를 확인하는 절차가 구체적임 | 한 쪽 US Letter PDF와 DejaVu 기반의 정해진 렌더 경로가 목표. 긴 경력의 분량 판단, 편집 가능한 회사 지정 DOCX, 한국어 서체는 별도 설계가 필요함 | [Apache-2.0](https://github.com/stevenha75/codex-resume-tailoring-skill/blob/main/LICENSE). 프로젝트에 별도 제3자 고지가 있어 재사용 시 함께 확인해야 함 |
| [Awesome-CV](https://github.com/posquit0/Awesome-CV) | Agent Skill이 아닌 LaTeX 템플릿. CV·이력서·커버레터의 일관된 조판과 예제, 빌드·PDF 검사 절차가 참고할 만함 | 확인일의 README는 LuaLaTeX/HarfBuzz와 latexmk를 사용하며 XeLaTeX를 지원하지 않는다고 명시함. 기존 Word 양식을 편집하는 도구가 아님. 이 저장소를 실행하거나 모든 예제를 검증하지는 않았음 | [LPPL-1.3c](https://github.com/posquit0/Awesome-CV/blob/master/LICENCE). MIT로 오인하지 말 것. 외부 글꼴·아이콘의 조건은 별도 |
| [JSON Resume resume-cli](https://github.com/jsonresume/resume-cli) | Agent Skill이 아닌 구조화된 이력서 데이터·테마 도구. 내용과 표현을 분리하는 방식과 입력 검증을 참고함 | 이 구 저장소의 현행 README는 보관 상태이며 개발이 [jsonresume.org](https://github.com/jsonresume/jsonresume.org)의 `packages/cli`로 이동했다고 안내함. 구 저장소를 현행 추천 도구로 소개하지 않음. 테마별 한글·읽기 순서·DOCX 지원은 별도 확인 필요 | 구 저장소의 [MIT](https://github.com/jsonresume/resume-cli/blob/master/LICENSE) 확인. 개별 테마와 이전 대상의 전체 라이선스를 일괄 판정하지 않음 |

라이선스 이름은 해당 파일에서 확인한 사실이다. 위 프로젝트의 소스·템플릿·이력서 예문을 이 저장소에 복사하지 않았으며, 자체 작성 파일만 MIT로 배포한다.

## 새 스킬로 만든 이유

재사용할 수 있는 기존 스킬은 있다. 다만 이번 목적에는 아래 네 가지를 함께 다루는 작은 패키지가 필요했다.

1. **서식 변경과 사실 변경의 경계:** 경력·기간·학력·성과 수치를 보존하고, 서식만 수정한 경우 본문을 대조한다.
2. **한국어 문서와 지정 양식:** 한글·영문 글꼴 설정, 회사 표의 필수 항목·병합·행열 구조, 긴 문서의 페이지 흐름을 다룬다.
3. **반복 가능한 파일 검수:** 읽기 전용 DOCX 사전 검사와 최종 전 페이지 렌더를 함께 사용한다.
4. **검증 범위의 정확한 표현:** 구조 검사, 시각 검사, PDF 읽기 순서, 실제 ATS·보조 기술 검증을 구분한다.

따라서 기존 사례를 참고해 독립적인 `resume-design`을 작성했다. 단일 열은 자유 형식의 기본 선택이며 회사의 필수 표를 지우는 규칙이 아니다. 본문 11 pt와 여백 18~22 mm도 시작값이지 채용 성과가 검증된 최적값은 아니다.

## ContextualWisdomLab의 기존 스킬과 결합

| 기존 저장소 | 함께 사용할 역할 |
| --- | --- |
| [team-lead-resume-skills](https://github.com/ContextualWisdomLab/team-lead-resume-skills) | 지원 직무에 맞는 경력 선택, 리더 역할과 근거의 연결 |
| [career-description-skills](https://github.com/ContextualWisdomLab/career-description-skills) | 상세 경력의 역할·행동·결과와 증거 정리 |
| [korean-writing-skills](https://github.com/ContextualWisdomLab/korean-writing-skills) | 자연스러운 한국어, 의미·수치·역할 보존 |
| `resume-design` | 정보 배치, 타이포그래피, 페이지 구성과 제출 파일 검수 |

디자인 스킬은 내용 작성 스킬의 모든 지침을 복제하지 않는다. 다른 스킬이 설치되지 않은 환경에서도 기본 디자인·검수 작업은 실행할 수 있다.

## 조사 한계

이 조사는 모든 공개 이력서 스킬을 망라하지 않는다. 비교 대상의 실제 ATS 통과율, 채용 성과, 모든 운영체제의 렌더 결과는 측정하지 않았다. 검색 사이트의 요약과 보안 점수는 검증된 품질 판정으로 인용하지 않았다. 구체적인 설계 근거는 [1차 자료 장부](../skills/resume-design/references/sources.md), 국내 회사별 제출 방식과 작성 사례는 [한국 테크 기업 사례](../skills/resume-design/references/korean-tech-cases.md)에 따로 기록했다.
