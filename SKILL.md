---
name: "stock-dashboard"
display_name: "我的股票持仓看板"
display_name_en: "My Stock Portfolio Dashboard"
description: "为用户搭建个人 A 股持仓数据看板：大盘指数（上证指数、深证成指、创业板指）+ 持仓市值、持仓盈亏、收益率、今日盈亏一屏呈现，支持多账户切换、持仓占比分布、CSV 导入、单只/全部刷新现价、行情失败手动兜底、建议反馈入口。数据仅保存在用户本机。当用户提到股票看板、持仓看板、持仓收益、盈亏统计、A股看板、炒股记账等需求时使用本技能。"
description_zh: "一分钟搭好个人 A 股持仓数据看板：三大指数 + 市值、盈亏、收益率一目了然，数据仅存本机。"
description_en: "Build a personal A-share holdings dashboard in one minute, showing major indexes plus market value, P/L and return rate at a glance, with local-only data."
examples_zh:
  - "帮我做一个股票持仓看板，我有两个账户"
  - "把我的持仓表导进来看看盈亏"
  - "看板上加个大盘指数和提建议入口"
examples_en:
  - "Build me a stock portfolio dashboard with two accounts"
  - "Import my holdings CSV and show my P/L"
  - "Add major indexes and a feedback entry to the dashboard"
version: "1.0.4"
author: "WorkBuddy 用户自研"
---

# 我的股票持仓看板（My Stock Portfolio Dashboard）

为用户搭建一个单文件、免部署的个人 A 股持仓数据看板。核心能力：三大指数栏（上证指数、深证成指、创业板指，含涨跌幅与昨收）；持仓市值、持仓盈亏、收益率、今日盈亏四卡 KPI；多账户切换；持仓占比堆叠条；逐股盈亏表；现价刷新（腾讯财经 / 东方财富免费公开接口，或用户自有 API）；手动改价兜底；CSV 导入；建议反馈入口（弹出作者微信二维码）。数据仅存本机浏览器，主打"我的A股持仓数据，仅自己本地可看"。

## 资源清单

- `templates/stock-dashboard.html`：看板成品模板（单文件 HTML，内联样式与脚本，无第三方依赖；作者微信二维码已以 base64 内嵌）。默认内置 6 条**虚构演示数据**，打开即可看到完整效果。
- `references/csv-schema.md`：持仓 CSV 的字段规范（列名、类型、示例）。
- `references/api-setup.md`：行情数据源选择与配置指引（腾讯财经 / 东方财富免费源，或用户自有 API）。
- `references/design-spec.md`：版式、配色与计算公式规范，二次修改时遵循。
- `scripts/fetch_quotes.py`：行情拉取脚本。优先调用用户配置的自有行情 API；未配置时可选用腾讯公开行情接口兜底（无需密钥，支持股票与指数代码）。

## 执行流程

当用户需要股票持仓看板时，按以下步骤执行：

1. **确认数据来源**，三选一：
   - 用户已有持仓 CSV → 按 `references/csv-schema.md` 校验列名，指导用户打开看板后点「导入持仓 CSV」；
   - 用户在 WorkBuddy 资料库有持仓数据表 → 指导用户从数据表导出 CSV 后导入；
   - 用户无数据 → 直接使用模板内置演示数据，先看效果再补数据。
2. **交付看板**：把 `templates/stock-dashboard.html` 复制到用户工作目录（文件名建议「我的股票持仓看板.html」），告知用户双击即可在浏览器打开，数据保存在本机浏览器 localStorage，不上传、仅自己可见。
3. **引导选择行情数据源**（安装后首次打开看板会自动弹出「行情设置」，见 `references/api-setup.md`）：
   - 弹窗内置 3 个数据源：**腾讯财经**（默认，免费公开接口，免注册、无需 Key）、**东方财富**（免费公开接口，可作备用）、**自有 API / 自建服务**（需填接口地址和用户自己的 Key）；用户也可先点「稍后设置」看演示数据；
   - 前两个源开箱即用、零配置；引导重点放在让用户知道数据来自公开接口、Key 永远只在用户自己手里（自有 API 场景）；
   - 自有 API 的接口约定：`GET {接口地址}?codes=688301,300872`（指数用 `sh000001,sz399001,sz399006`），返回 `{"quotes":[{"code":"688301","price":17.35}]}`；
   - 用户若需要服务端拉取行情，可用 `scripts/fetch_quotes.py`（支持 `--api`/`--key` 参数或 `QUOTE_API_URL`/`QUOTE_API_KEY` 环境变量；不带参数时走腾讯公开行情兜底）。
4. **按需定制**：用户提出增删 KPI、改配色、加字段时，按 `references/design-spec.md` 修改模板（涨跌配色遵循 A 股习惯：涨红跌绿）。
5. **建议反馈入口**（内置）：右上角「建议」按钮弹出作者微信二维码（已内嵌模板），用户扫码添加好友提交修改意见。二维码图片由技能作者维护：替换模板中 `fbQr` 区域的 base64 图片即可。

## 注意事项

- 所有持仓数据与配置仅保存在用户本机浏览器，不上传、不联网同步；不得在任何产物中输出用户的持仓明细。
- 演示数据（持仓与指数）均为虚构模拟，必须向用户说明，不得当作真实行情或投资建议。
- 现价刷新失败时引导用户使用表格内「现价」单元格的手动填写兜底，不要让功能卡死。
