# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

高岸ERP — an Enterprise Resource Planning system. This repository is in early development with no source code or build system established yet.

## Engineering Standards (from .clauderules)

This project follows a structured engineering methodology documented in `.clauderules`. Key principles:

- **First Principles**: Start from business requirements and top-level financial logic, then derive business logic. Write requirements docs, then define object/interaction models.
- **Methodology Compliance**: Follow the methodology strictly — write development documents and code according to software engineering standards. Do not skip customer requirements.
- **Archiving**: After completing each logical cycle, prompt the user to run Git commit and push to GitHub for rollback safety.

### Deliverable Standards

- **PRD Requirements**: Every PRD must include: business scenarios, affected accounts/subjects (科目), Error Code definitions, and data-closed-loop verification.
- **Full File Delivery**: When updating source files, always provide the complete file content — never code snippets.
- **Development Logs**: Auto-generate development logs.

## Current State

This repository is in **documentation phase** — requirements under review, architecture design in draft. Source code is yet to be created.

## Document Management

All project documents are stored in `docs/` directory, organized by software engineering lifecycle phase:

```
docs/
├── 01-需求/         Requirements (PRD, 需求说明书, 用户故事)
├── 02-设计/         Design (技术架构, 数据库设计, API设计, IoT清单, 交互原型)
├── 03-开发/         Development (编码规范, 开发指南)
├── 04-测试/         Testing (测试计划, 测试用例, 测试报告)
├── 05-部署运维/     Deployment & Operations (部署手册, 运维手册)
└── README.md        Document registry (中央索引, 所有文档须在此注册)
```

### Document Management Rules

1. **Naming convention**: `高岸ERP系统-文档名称（V版本号，日期）.md`
2. **Registry**: Every document MUST be registered in `docs/README.md` (the document registry) with its ID, version, status, and traceability links
3. **Document IDs**: Each document gets a unique ID (e.g., REQ-01, ARC-01, IOT-01, UI-01, DBA-01, API-01, TST-01)
4. **Lifecycle states**: 草稿 → 评审中 → 已批准 → 已更新/已废弃
5. **Versioning**: V主版本.次版本 (major.minor). Update version in both filename and document header
6. **Traceability**: Document registry maintains relationship mapping (e.g., REQ-01 Chapter 6.8 → IOT-01)
7. **Archiving**: Old versions go to `docs/_history/` — never overwrite or delete
8. **Sync updates**: When requirements change, update ALL affected documents consistently (architecture, IoT list, prototypes, test cases, etc.)
