# Example: Another Houm Project Summary

This is a real-world example of a portfolio-ready project summary for a maternity care platform.

---

## The Document

```markdown
# Project Another Houm

버전: v1.14.0
설명: Project for creating web ERP/CRM tool for specific usage with AI Agent
업무 속성: 개발, 기획, 엔지니어링

# Background

- 현재 협업하고 있는 병원에 외국인 고객이 많은데, 병원에서 사용 중인 ERP / CRM 은 국내 환자 워크플로우(언어/서류/보험/커뮤니케이션에)에 최적화되어 있어 외국인 고객 응대에 한계가 있음
    - ERP: Enterprise Resource Planning
    - CRM: Customer Relationship Management
- 외국인 입장에서는, 한국 내에서 신뢰를 가지고 출산 및 산전/산후 서비스에 대한 정보를 얻을 수 있는 창구가 부족

# Objective

- 산모와 헬스케어 제공자가 공존하는 플랫폼을 구상해본다.
    - 병원 및 헬스케어 제공자 입장에서 외국인 고객을 유치할 수 있고 관리할 수 있는 플랫폼
    - 외국인 고객 관점에서는 한국에서 믿을 수 있고 신뢰할 수 있는 헬스케어 제공자를 찾을 수 있는 플랫폼

# Design

- Houmlike Design을 기본 디자인 스킬로 지정해서 사용
    - anthropic의 skill repository를 fork 해와서 개인 스킬들 업데이트
        - 개인 github repo: https://github.com/dabsdamoon/anthropic-skills
        - Houmlike design skill: https://github.com/dabsdamoon/anthropic-skills/tree/main/skills/houmlike-design

# Database

- Supabase 사용
    - 데이터베이스들 중 바이브 코딩에 그나마 친화적인 데이터베이스로 판단
        - Lovable과의 connection, SSO authentication 간소화, tabular view 등

# Code Management

- Vercel을 이용해 배포 파이프라인 관리
    - GitHub Actions을 이용한 CI/CD 파이프라인 관리
- Claude Code의 sub-agent 들을 이용해 코드 리뷰 병렬적으로 진행
    - frontend, backend, data engineering, and QA review

# Contents

### Login and Registration

- Login
    - email verification 혹은 Google SSO 기능으로 회원가입 및 로그인 가능
    - screenshots
        - [Login screen screenshot]

- Registration
    - 환자 혹은 헬스케어 제공자를 선택 가능
    - 환자 사이드
        - 개인정보 및 보험사를 입력하게 해서 나중에 보험사별 맞춤형 추천이 가능하도록 유도
        - screenshots
            - [Patient registration form]

    - 헬스케어 제공자 사이드
        - organization의 개념을 정의하고, 하나의 organization 안에 여러 사람이 속해서 일할 수 있도록 플로우 작성
        - screenshots
            - [Provider registration form]

### Maternity Dashboard

- Overview (개요): 환자 관점에서 전반적인 기능을 볼 수 있는 대시보드
    - screenshots
        - [Maternity dashboard overview]

- 임신 여정 알리미
    - 현재 임신 주수에서 어떤 검진 및 검사를 받아야 하는지 알려주는 대시보드
    - screenshots
        - [Pregnancy journey tracker]

- 외국 보험 필요 서류 작성
    - 외국 보험에 청구하기 위한 서류를 작성할 수 있는 기능
    - 작성 후에 병원 및 헬스케어 제공자 측에 제출을 할 수 있고, 헬스케어 제공자는 해당 서류를 확인한 후 신청자에게 완성된 서류 이메일 발송
    - screenshots
        - [Insurance document form - step 1]
        - [Insurance document form - step 2]
        - [Insurance document submission]

- 산전/산후 교육 관련 클래스 검색 및 수강신청 기능
    - 관리자(admin) 차원에서 제공하는 클래스 검색 및 수강 기능
    - screenshots
        - [Class search and registration]

### Healthcare Provider Dashboard

- Overview (개요): 헬스케어 제공자 입장에서 전반적인 기능을 볼 수 있는 대시보드
    - screenshots
        - [Provider dashboard overview]

- 병원 인보이스 생성
    - 수가 시스템 개편 및 개편된 수가 시스템을 반영한 새로운 인보이스 생성 기능 구현
    - 기존 청구 코드별 수가를 수정할 수 있도록 청구 코드 관리 기능 구현
    - screenshots
        - [Invoice builder demo video]
        - [Billing code management]

- 외국 보험 필요 서류 보완
    - Maternity Dashboard에서 외국 보험 필요 서류 작성 후 신청 시, 확인 및 서류를 보완하는 기능 구현
    - screenshots
        - [Insurance document review workflow]

- 재고 관리
    - 병원 내 판매하는 물품 및 영양제 재고 관리를 위한 툴 구축
    - screenshots
        - [Inventory management demo]

- 환자 관계 관리(Patient Relationship Management)
    - 기존 CRM 툴이랑 조금 다른 성향인 PRM 툴을 만드는 작업 진행
        - PRM(Patient Relationship Management): about building positive relationships between healthcare providers and patients.
    - 이메일 송부, 예약 고객 확인 및 분석 기능 구현
    - screenshots
        - [PRM dashboard]
        - [Email and analytics demo]

### Admin Dashboard

- 관리자 기능을 정리한 대시보드
    - 관리자 주관 클래스 관리 기능, 헬스케어 제공자 관리 기능, Houmy Reference 도메인 노출 관리 기능 등
    - screenshots
        - [Admin dashboard]
        - [Class management]
        - [Provider management]

### Houmy (AI Assistant)

- Reference tag 기반 RAG 를 적용한 대화시스템 구축
    - source 별 태그 생성 및 해당 태그 내 데이터 chunking 진행
    - text-embedding-3-small 모델을 이용해 embedding 생성
        - 질문 쿼리에 맞게 해당 데이터 가져오는 RAG 파이프라인 구축
    - 이외, 유저 정보를 반영할 수 있도록 데이터 스키마를 연결해서 종합적으로 답장을 줄 수 있도록 context engineering 파이프라인 구축
    - screenshots
        - [Houmy chat interface]
        - [Chat interaction demo]

- ACOG (American College of Obstetricians and Gynecologists) 문서에 기반한 산전/산후관리 Knowledge Graph 구축
    - screenshots
        - [Knowledge graph visualization]

# TODOS

- 기능 수정 및 보완
- 기능별 Proof-of-Concept 계속해서 진행
```

---

## Analysis: Why This Structure Works

### 1. Problem-First Narrative
The document immediately establishes:
- **The pain point**: Existing ERP/CRM doesn't support foreign patients well
- **The gap**: Foreigners lack trustworthy maternity care information in Korea

This shows problem-solving ability before any technical details.

### 2. Clear User Personas
Features are organized by three user types:
- **Maternity** (산모) - End customers/patients
- **Provider** (헬스케어 제공자) - Hospitals/clinics
- **Admin** (관리자) - Platform operators

This demonstrates product thinking and user-centric design.

### 3. Technical Decisions with Rationale
Not just "used Supabase" but:
- "Supabase - 바이브 코딩에 친화적 + Lovable connection + SSO 간소화"

Shows decision-making ability, not just tool familiarity.

### 4. Development Practice Highlights
- "Claude Code sub-agents for parallel code review"
- Shows familiarity with modern AI-assisted development

### 5. Feature Depth
Each feature includes:
- What it does
- Why it exists (solving what problem)
- Implementation detail (where relevant)
- Visual proof (screenshot placeholders)

---

## How to Extract This From a Codebase

### Step 1: Identify the Domain
Look for clues in:
- `package.json` description
- `CLAUDE.md` or `README.md`
- i18n translation files (domain-specific terms)
- Database table names

### Step 2: Find User Types
Search for:
- Routes with role prefixes (`/admin/`, `/provider/`, `/patient/`)
- Auth context or user type enums
- Dashboard components per role

### Step 3: Map Features to Code
For each feature, trace:
```
Component → Service/Hook → API/Database → User Story
```

Example:
```
ProviderInvoiceBuilder.tsx
  → invoiceService.ts
    → billing_invoices table
      → "Providers can generate itemized invoices for patients"
```

### Step 4: Document Technical Decisions
Check:
- `CLAUDE.md` for project conventions
- Config files for technology choices
- Commit history for evolution of decisions

### Step 5: Generate the Summary
Use the template from SKILL.md, filling in:
- Background from domain analysis
- Objective from user persona mapping
- Features from component/service mapping
- Technical stack from package.json + configs
