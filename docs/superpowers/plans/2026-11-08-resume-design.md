# Resume Design Implementation Plan

> For agentic workers: use superpowers:executing-plans for the implementation and preserve the user's authorization to create and publish this skill.

**Goal:** 공개 이력서 디자인 스킬을 근거, 도구, 합성 예제와 함께 배포한다.

**Architecture:** 설치 패키지는 `skills/resume-design/`에 둔다. 출처와 디자인 규칙은 필요할 때 읽고, DOCX 검사와 예제 생성만 작은 Python 스크립트로 구현한다. 개인 스킬 원본은 지정된 스킬 디렉터리에서 작성·검증한 뒤 공개 배포본과 대조한다.

**Tech Stack:** Markdown, Python standard library, python-docx, Poppler and the available DOCX renderer.

**Spec:** `docs/design.md`

## Global Constraints

- 제출처의 지정 양식과 사실 보존을 우선한다.
- 공개 자료에는 합성 경력만 사용한다.
- 읽기 전용 검사를 ATS 합격 판정으로 설명하지 않는다.
- 기존 스킬과 동시에 수정 중인 파일은 변경하지 않는다.

## Review Focus

- 긴 한글 회사명과 영문 제품명: 글자 깨짐과 줄바꿈을 렌더에서 확인한다.
- 회사 지정 표: 임의로 단일 열로 재작성하지 않고 읽기 순서를 별도로 확인한다.
- 겸직과 페이지 압축: 기간이나 본인 역할이 변하지 않아야 한다.
- 내용이 같은 DOCX의 run 분할: 텍스트 비교는 거짓 차이를 만들지 않아야 한다.
- 숨김 글자·변경 추적·주석: 시각 검수만으로 완료 판정하지 않는다.

## Task 1 Source-backed skill

- [x] 공식 자료와 기존 스킬의 범위·라이선스를 확인한다.
- [x] 스킬 없는 지정 양식 시나리오의 응답을 보존한다.
- [x] `SKILL.md`, 디자인·출처·양식·검수 지침을 작성한다.
- [x] 새 문맥의 적용 시나리오로 실제 사용 결과를 검토한다.

## Task 2 DOCX preflight and original examples

**Interfaces:** `audit_docx(path, baseline=None, required_text=()) -> dict`; read-only CLI returns 0 for no blocking finding, 1 for blocking findings, 2 for invalid input. `build_examples.py --output-dir DIR` creates synthetic DOCX files with explicit styles and logical order.

- [x] 내용 유실·run 분할·표·다단·숨김·변경 추적·주석을 시험하는 테스트를 먼저 실행한다.
- [x] 표준 라이브러리 검사기를 작성하고 전체 테스트를 실행한다.
- [x] 합성 DOCX 예제를 생성해 모든 페이지를 렌더하고 확인한다.
- [x] PDF의 텍스트 순서, 글꼴, 쪽수와 검수 한계를 기록한다.

## Task 3 Publish and verify

- [x] 스킬 메타데이터를 검증하고 공개 패키지와 원본을 대조한다.
- [x] README, MIT License, 사용 예, 검증 기록을 완성한다.
- [x] 공개 저장소의 최신 HEAD를 확인해 일반 커밋으로 게시한다.
- [x] 원격 파일과 공개 상태를 재확인하고 개인 스킬을 저장한다.
