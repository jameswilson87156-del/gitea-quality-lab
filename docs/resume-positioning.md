# 简历表述与证据边界

## 项目名称

**Gitea Quality Lab｜开源系统测试与自动化验收**

## 简历项目描述草稿

- 基于 Python、pytest、HTTPX、Playwright 与 Docker Compose，为固定版本 Gitea 28.2.0 构建黑盒系统测试 Harness，覆盖认证、角色权限、公开/私有仓库边界、Issue 生命周期、筛选/分页、浏览器工作流和 SQLite 持久化。
- 实现每次运行唯一 Run ID、隔离命名的测试数据、case ID 映射、JSON/JUnit 结果交叉校验、失败 Trace 脱敏和自包含 HTML 报告；报告按运行 JSON 展示逐条结果、类别统计、搜索/筛选及可展开失败详情。
- 最近本地验收运行 18/18 passed、0 failed、0 skipped、0 errors；Harness 单元测试 27 passed。结果只适用于本地合成数据和上游 Gitea 固定版本。

## 面试时说明

这是个人本地开源系统测试项目，不是公司的生产系统。可以说明 API/UI/持久化测试如何设计、如何隔离运行数据、如何校验 JSON 与 JUnit 的一致性，以及遇到 Docker 未启动、Issue 列表筛选/分页边界时如何定位和复测。

不要将此项目描述为生产监控、线上告警值班或大规模生产压测经验。它没有代表公司业务的用户流量、生产数据、生产容量或真实 SLO。

## 可核验证据

- [测试矩阵](test-matrix.md)
- [验收与截图记录](../reports/evidence.md)
- 最新本地 HTML 报告、JSON、JUnit 和 API/UI 持久化截图：`reports/runs/20261029T150955Z-4437d857/`；专用报告页面桌面/移动截图：`reports/runs/20261029T144534Z-ec54abd9/`
