# SafeSell AI 逆向分析报告

> 分析时间: 2026-03-24
> 目标网站: https://safesellai.com/
> 分析方式: JS Bundle 静态分析 + 浏览器实时交互 + API 抓包

---

## 一、产品概述

**SafeSell AI** 是一款面向跨境电商卖家的合规排查工具，由"泽远跨境（ZEYUAN GLOBAL）"开发。核心功能是帮助卖家在上架商品前排查品牌侵权、专利侵权和 TRO（临时限制令）风险，避免店铺被冻结。

**Slogan**: 跨境合规守护

**支持平台**: Walmart / Amazon / SHEIN / Temu

---

## 二、技术栈

| 层面 | 技术 | 证据 |
|------|------|------|
| **前端框架** | React 19 + React Router 7.13.1 | JS bundle 内含 `react.production.js`、`react-router` |
| **构建工具** | Vite | 文件名 `index-CxwW0MV7.js`（content hash 格式） |
| **CSS 框架** | Tailwind CSS | body class `bg-gray-50 min-h-screen`，组件类名全部为 Tailwind |
| **后端框架** | Node.js + Express | HTTP 头 `x-powered-by: Express` |
| **CDN/安全** | Cloudflare | `server: cloudflare`，含 WAF、RUM、DDoS 防护 |
| **Excel 处理** | SheetJS (xlsx) | JS bundle 内含完整的 xlsx 库（含 ODS 格式支持） |
| **AI 模型** | DeepSeek / OpenAI / Moonshot | 可配置 API Base URL 和 Key，默认 `https://api.deepseek.com` |
| **图像搜索** | CLIP 视觉模型（本地部署） | 页面明确说明"通过本地 CLIP 视觉模型计算图片特征" |
| **数据传输** | SSE (Server-Sent Events) | 品牌排查响应以 `data: {...}` 流式逐条返回 |
| **凭证加密** | AES-256-GCM | 店铺 API 凭证加密存储（页面文案确认） |
| **UI 图标** | Lucide React | JS bundle 内含 lucide icon 组件 |
| **路由** | SPA 单页应用 | `<div id="root"></div>`，单一 JS/CSS bundle |

### HTML 结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <title>SafeSell AI - 跨境合规守护</title>
  <script type="module" crossorigin src="/assets/index-CxwW0MV7.js"></script>
  <link rel="stylesheet" crossorigin href="/assets/index-lMmwZm03.css">
</head>
<body class="bg-gray-50 min-h-screen">
  <div id="root"></div>
</body>
</html>
```

- JS bundle: 1.8 MB（包含 React、Router、SheetJS、Lucide 等全部依赖）
- CSS bundle: 49 KB（Tailwind 生成）

---

## 三、数据库规模（实测）

| 数据集 | 数量 | 来源 | 更新时间 |
|--------|------|------|----------|
| 品牌词库 | **7,587,662** 条 | USPTO + 自建 | 2026-03-23 |
| 专利库总量 | **17,672,495** 条 | USPTO | 2026-03-23 |
| └ 外观专利 | 852,433 | USPTO | 2026-03-19 |
| └ 实用专利 | 15,994,943 | USPTO | 2026-03-19 |
| TRO 品牌 | **1,269** 个 | CourtListener | 2020-2026 |
| TRO 案件 | **6,567** 起 | CourtListener | 2020-2026 |

---

## 四、功能模块与 API 接口

### 4.1 品牌排查（核心功能）

**入口**: 首页"排查工具"标签

**使用方式**:
- 单个/多个品牌名输入（支持每行一个，最多10个）
- Excel 文件上传批量排查（.xlsx/.xls）

**API**: `POST /api/check-trademarks`

**传输方式**: SSE (Server-Sent Events) 流式返回

**响应数据结构**:
```json
{
  "brand": "Adidas",                    // 品牌名
  "risk": "禁止使用",                    // 风险等级: 禁止使用/中危(疑似)/安全(无风险)
  "score": 120,                          // 风险评分
  "isTro": true,                         // 是否有 TRO 记录
  "troInfo": {
    "lastTroDate": "2025-08-29",         // 最近 TRO 时间
    "lawFirm": "Arnold & Porter, GBC",   // 涉及律所
    "troCount": 2                         // TRO 次数
  },
  "details": "⚠️ TRO 高危品牌！...",     // 详细说明
  "advice": "立即下架所有相关商品...",     // 处置建议
  "usptoUrl": "https://tsdr...",          // USPTO 搜索链接
  "niceClasses": "第9类(电子/电器)...",   // 商标类别
  "ownerName": "HarbisonWalker...",       // 持有人
  "trademarkCount": 8,                   // 商标注册数
  "statusSummary": "...",                // 状态摘要
  "completed": 1,                        // 当前完成数
  "total": 1                             // 总查询数
}
```

**风险评分算法推断**:
- 基础分 = 品牌库匹配权重
- TRO 加权 = TRO 次数 × 律所危险度
- 时间衰减 = 最近 TRO 时间距今越近分越高
- score > 100 → "禁止使用"（红色）
- score 50-100 → "中危(疑似)"（黄色）
- score < 50 → "安全(无风险)"（绿色）

**智能过滤**: 标题中的通用词会被自动过滤，避免误报

---

### 4.2 专利排查

**入口**: "专利排查"标签

**三种模式**:

#### (a) 关键词搜索
- **API**: `POST /api/patents/search`
- **传输方式**: JSON 直接返回（非 SSE）
- **筛选**: 全部类型/外观/实用 + 全部状态/有效/过期
- **响应结构**:
```json
{
  "results": [...],
  "total": 18,
  "query": "LED desk lamp"
}
```
- **专利字段**:
```
patent_id: string          // 内部ID
patent_number: string      // 专利号（如 11204461）
patent_type: string        // "实用" / "外观" / "植物"
title: string              // 专利标题
abstract: string           // 摘要
assignee: string           // 受让人/权利人
filing_date: string        // 申请日
grant_date: string         // 授权日
expiration_date: string    // 到期日
status: string             // "有效" / "过期"
cpc_codes: string          // CPC 分类号
claims_count: number       // 权利要求数
rank: number               // 相关度排名
riskLevel: string          // "低风险" 等
riskReason: string         // 风险原因说明
```

#### (b) Excel 批量扫描
- **API**: `POST /api/patents/scan-batch`
- 上传 Excel 需包含 "title"/"名称" 或 "brand"/"品牌" 列
- 逐行扫描专利库匹配

#### (c) AI 图片搜索
- **API**: `POST /api/patents/ai-image-search`
- **余额查询**: `GET /api/patents/image-search-balance`
- **状态查询**: `GET /api/patents/image-search-status`
- 支持 JPG, PNG, WebP
- **技术原理**: 上传产品图片 → 本地 CLIP 模型提取特征向量 → 在预计算的专利图片特征库中做余弦相似度搜索
- 完全本地运行，不依赖外部 API
- 按次计费，本月额度 50 次

---

### 4.3 TRO 案件排查

**入口**: "TRO 排查"标签

**数据规模**: 1,269 个品牌、6,567 起案件、2020-2026 年

**数据来源**: CourtListener（美国法院公开数据）

**三种搜索模式**: 品牌搜索 / 案件号搜索 / 律所搜索

**API 接口**:
- `GET /api/tro/stats` → 统计数据
- `GET /api/tro/balance` → 剩余查询次数
- `GET /api/tro/packs` → 次数包价格

**TRO 统计响应**:
```json
{
  "brandCount": 1269,
  "caseCount": 6567,
  "yearRange": "2020-2026",
  "topFirms": [
    {"name": "GBC", "count": 1550},
    {"name": "Keith", "count": 861},
    {"name": "GBC (推测)", "count": 694},
    {"name": "HSP", "count": 558},
    {"name": "SMG", "count": 283}
  ]
}
```

**查询结果包含**:
- 被诉次数（如 Nike: 100 次）
- 时间跨度（2022-05-08 ~ 2026-02-04）
- 涉及律所（Arnold & Porter, GBC 等）
- 和解金参考（$2,000-$20,000）
- 风险提示与应对建议
- 案件时间线（每条案件的日期、案件号、律所、法院文件链接）

**计费**: 按次收费，购买次数包，永久有效不清零

---

### 4.4 多平台店铺体检

**入口**: "店铺体检"标签

**支持平台与 API 凭证**:

| 平台 | 凭证字段 | 开发者平台 |
|------|----------|-----------|
| **Walmart** | Client ID + Client Secret | developer.walmart.com |
| **Amazon** | Seller ID + SP-API LWA Refresh Token + Marketplace ID | developer-docs.amazon.com/sp-api/ |
| **SHEIN** | API 凭证 | openplatform.sheincorp.com |
| **Temu** | API 凭证 | seller.temu.com |

**API 接口**:
- `POST /api/stores/bind` → 绑定店铺
- `GET /api/stores` → 已绑定店铺列表
- `POST /api/store-audit` → 执行体检

**体检流程**:
1. 绑定平台 API 凭证 → AES-256-GCM 加密存储
2. 后端调用平台 API 拉取全部在售商品
3. 提取商品标题中的品牌关键词（智能过滤通用词）
4. 批量匹配品牌库 + 专利库 + TRO 案件库
5. 生成风险报告（高危/中危/安全分类）

**体检频率**: 每日体检 / 每周体检（可选）

---

### 4.5 AI 智能报告

**API**:
- `POST /api/ai-report/generate` → 生成报告（流式）
- `GET /api/ai-report/download-pdf` → 下载 PDF
- `GET /api/ai-report/balance` → 余额查询

**AI 后端**: DeepSeek / OpenAI / Moonshot（管理员可配置）
- 默认 API Base: `https://api.deepseek.com`
- 默认 Model: `deepseek-chat`
- 备选: `https://api.openai.com`, `https://api.moonshot.cn`

**功能**: 对排查结果生成风险报告 + 修改建议，支持 PDF 下载

**实现**: 使用 ReadableStream 流式输出，前端逐字显示

---

### 4.6 AI 客服聊天

**API**:
- `POST /api/chat/message` → 发送消息
- `POST /api/chat/upload` → 上传文件
- `GET /api/chat/admin/config` → 管理员配置
- `POST /api/chat/admin/default-prompt` → 设置系统提示词
- `POST /api/chat/admin/test` → 测试

**功能**: 右下角浮窗聊天，支持上传图片/文件辅助咨询

**预设快捷问题**: 怎么支付？/ 价格多少？/ 怎么使用？/ 联系客服

**联系方式**: 微信 yuzeyuan8 | 邮箱 a365785149@qq.com

---

### 4.7 本地词库

**API**:
- `GET /api/dictionary` → 词库列表
- `POST /api/dictionary/batch` → 批量导入

**功能**: 查询过的品牌自动缓存到本地词库，支持模板下载和批量导入导出

---

## 五、用户系统与认证

**自建认证（JWT）**:
- `POST /api/auth/register` → 注册
- `POST /api/auth/login` → 登录
- `GET /api/auth/me` → 获取当前用户（每次操作都调用）
- `POST /api/auth/refresh` → Token 刷新
- `POST /api/auth/logout` → 登出
- `POST /api/auth/change-password` → 修改密码

**管理后台**: `/admin` 路由
- `GET /api/admin/users` → 用户管理
- 管理员密钥认证

---

## 六、支付系统

**API**:
- `POST /api/payment/create-order` → 创建订单
- `GET /api/payment/orders` → 订单列表
- `GET /api/payment/qrcode/{id}` → 收款码图片
- `POST /api/payment/admin/amount-match` → 金额匹配确认
- `GET /api/payment/admin/orders?status=pending` → 待确认订单

**支付方式**: 微信支付 / 支付宝（上传收款码）

**确认机制**: 精确金额匹配
1. 用户下单 → 系统生成唯一金额（如 ¥99.37）
2. 用户扫码转账该精确金额
3. 系统实时监听到账 → 自动匹配订单确认（3秒内）

**特点**: 不会自动续费

---

## 七、商业模式与定价

| 功能 | 免费版 | 专业版 ¥299/月 | 企业版 |
|------|--------|----------------|--------|
| 品牌排查 | 30次/天 | 300次/天 | 不限次 |
| 专利排查 | 10次（总共） | 20次/天 | 不限次 |
| 图片排查 | - | 50次/月 | 更多 |
| TRO 排查 | - | 50次/月 | 更多 |
| 店铺体检 | 1店/月 | 1店/月 | 无限 |
| 历史记录 | 7天 | 90天 | 永久 |
| AI 报告 | - | 有 | 有 |
| 专属客服 | - | - | 有 |

**TRO/图搜次数包**: 单独购买，永久有效不清零

---

## 八、安全与防护

- **Cloudflare WAF**: 全站 WAF 防护 + DDoS
- **HSTS**: `max-age=31536000; includeSubDomains`
- **X-Frame-Options**: DENY（禁止 iframe 嵌入）
- **X-Content-Type-Options**: nosniff
- **X-XSS-Protection**: 1; mode=block
- **Referrer-Policy**: strict-origin-when-cross-origin
- **robots.txt**: 禁止所有 AI 爬虫（ClaudeBot, GPTBot, Bytespider 等），允许搜索引擎
- **凭证加密**: AES-256-GCM 加密存储店铺 API 凭证

---

## 九、架构图

```
┌──────────────────────────────────────────────────┐
│                 Cloudflare CDN/WAF                │
├──────────────────────────────────────────────────┤
│        React 19 SPA (Vite + Tailwind)            │
│   SheetJS 前端解析 Excel → 调用后端 API           │
│   SSE 流式接收品牌排查结果                         │
├──────────────────────────────────────────────────┤
│              Express.js Backend API               │
│  ┌─────────────┬─────────────┬─────────────────┐ │
│  │ 品牌库查询   │ 专利库查询   │ TRO 案件库查询  │ │
│  │ 758万品牌    │ 1767万专利   │ 6567 案件       │ │
│  │ (USPTO+自建) │ (USPTO)     │ (CourtListener) │ │
│  └─────────────┴─────────────┴─────────────────┘ │
│  ┌─────────────┬─────────────┬─────────────────┐ │
│  │ CLIP 模型    │ DeepSeek    │ 平台 API 对接   │ │
│  │ 图片相似度   │ AI报告/客服  │ AMZ/WMT/SHEIN  │ │
│  └─────────────┴─────────────┴─────────────────┘ │
│  ┌─────────────┬─────────────┐                   │
│  │ JWT 认证     │ 微信/支付宝  │                   │
│  │ 用户管理     │ 金额匹配支付 │                   │
│  └─────────────┴─────────────┘                   │
├──────────────────────────────────────────────────┤
│          数据库 (品牌/专利/TRO/用户/订单)          │
└──────────────────────────────────────────────────┘
```

---

## 十、完整 API 接口清单

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录 |
| GET | /api/auth/me | 获取当前用户 |
| POST | /api/auth/refresh | 刷新 Token |
| POST | /api/auth/logout | 登出 |
| POST | /api/auth/change-password | 修改密码 |

### 品牌排查
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/check-trademarks | 品牌排查（SSE 流式） |
| GET | /api/brand-db-info | 品牌库统计信息 |
| GET | /api/dictionary | 本地词库列表 |
| POST | /api/dictionary/batch | 批量导入词库 |
| GET | /api/history?page=1&limit=30 | 查询历史 |
| GET | /api/audit-history | 审计历史 |

### 专利排查
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/patents/search | 关键词搜索 |
| POST | /api/patents/scan-batch | Excel 批量扫描 |
| POST | /api/patents/scan-image | 单图扫描 |
| POST | /api/patents/ai-image-search | AI 图搜 |
| GET | /api/patents/info | 专利库统计 |
| GET | /api/patents/image-search-balance | 图搜余额 |
| GET | /api/patents/image-search-status | 图搜状态 |

### TRO 排查
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tro/stats | TRO 统计 |
| GET | /api/tro/balance | 查询余额 |
| GET | /api/tro/packs | 次数包价格 |

### 店铺体检
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/stores | 已绑定店铺 |
| POST | /api/stores/bind | 绑定新店铺 |
| POST | /api/store-audit | 执行体检 |

### AI 功能
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/ai-report/generate | 生成 AI 报告 |
| GET | /api/ai-report/download-pdf | 下载报告 PDF |
| GET | /api/ai-report/balance | 报告余额 |
| POST | /api/chat/message | AI 客服消息 |
| POST | /api/chat/upload | 上传文件 |

### 支付
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/payment/create-order | 创建订单 |
| GET | /api/payment/orders | 订单列表 |
| GET | /api/payment/qrcode/{id} | 收款码 |
| POST | /api/payment/admin/amount-match | 金额匹配 |

### 管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/admin/users | 用户列表 |
| GET | /api/chat/admin/config | AI 配置 |
| POST | /api/chat/admin/default-prompt | 设置提示词 |
| POST | /api/chat/admin/test | 测试 AI |

---

## 十一、核心壁垒分析

**技术壁垒**: 低
- 标准的 React + Express + SQLite/PostgreSQL 架构
- CLIP 模型开源免费（OpenAI clip-vit-base-patch32）
- AI 报告使用第三方 API（DeepSeek）
- 代码复杂度不高，一个全栈工程师可以复现

**数据壁垒**: 高
- 758 万品牌数据库 → 来源 USPTO 商标全量数据，需要下载+解析+索引
- 1767 万专利数据库 → 来源 USPTO 专利全量数据
- 6567 TRO 案件库 → 来源 CourtListener，需要结构化整理
- 85 万外观专利图片的 CLIP 特征向量 → 需要预计算

**运营壁垒**: 中
- 数据需要持续更新（每周/每月同步 USPTO 增量）
- TRO 案件需要持续监控法院新案件
- 多平台 API 对接需要维护（平台 API 变更）

---

## 十二、复现路线图

### Phase 1: 数据库构建（1-2周）
1. 下载 USPTO 商标全量 XML → 解析入库 → 建全文索引
2. 爬取 CourtListener TRO 案件 → 结构化存储
3. 下载 USPTO 专利数据 → 解析入库

### Phase 2: 核心功能（1-2周）
4. 品牌排查 API（品牌库匹配 + TRO 关联 + 风险评分）
5. 专利搜索 API（全文检索 + 筛选）
6. TRO 排查 API

### Phase 3: 高级功能（1-2周）
7. CLIP 图搜（下载专利图片 + 预计算特征 + 相似度搜索）
8. 多平台店铺体检（对接 Amazon SP-API / Walmart API 等）
9. AI 报告生成（DeepSeek API + PDF 导出）

### Phase 4: 前端与运营（1周）
10. React 前端界面
11. 用户系统 + 支付
12. 数据增量更新定时任务
