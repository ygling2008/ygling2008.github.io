# 学术主页 — AI 编码规范

实现或修改 `index.html` 时以本文件为准。保持现有视觉语言、HTML 结构和文案约定。未经明确要求，不要引入新的框架、CSS 库或页面架构。

## 目标

面向 **Yonggen Ling（凌永根）**、Tencent Robotics X 研究员的单文件英文学术主页。静态 GitHub Pages。仅一个带内联 CSS 的 `index.html`。无构建步骤，无 JS 框架。

## 技术栈与文件规则

- 单文件：`index.html`（HTML5，`lang="en"`）。
- CSS 写在 `<head>` 的 `<style>` 中。未经要求不要拆成独立样式表。
- 不要留未使用的 CSS class。HTML 里没用到的样式（例如招聘徽章、第一作者高亮）不要保留。
- 优先用 CSS 自定义属性，避免硬编码颜色。没有 token 时才硬编码（页面背景渐变、招聘框渐变终点 `#dbeafe`）。
- 缩进用 4 个空格。HTML 嵌套保持整齐。
- 外链：`target="_blank"` 且 `rel="noopener noreferrer"`。
- 邮箱用字符码脚本写入 `#email-display`。不要在 HTML 里放明文 `mailto:`。

## 页面结构（顺序固定）

1. 吸顶导航（`#biography`、`#publications`、`#awards`、`#experience`）
2. 页头卡片（照片、姓名、格言、单位、邮箱、社交图标）
3. Biography 区块（简介 + 研究方向 + 招聘提示框）
4. Selected Publications
5. Selected Awards
6. Work Experience
7. 页脚（版权 + 最后更新时间）

导航文案须与区块用途一致。没有独立招聘区块时，不要加 Hiring 导航项。

## 设计 token

```css
:root {
    --primary-color: #3b82f6;
    --primary-dark: #2563eb;
    --text-primary: #1f2937;
    --text-secondary: #4b5563;
    --text-muted: #6b7280;
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-accent: #eff6ff;
    --border-color: #e5e7eb;
    --border-accent: #bfdbfe;
}
```

阴影沿用已有定义：`--shadow-sm`、`--shadow-md`、`--shadow-lg`。

**颜色用途**

| 用途 | Token |
|---|---|
| 正文 | `--text-primary` |
| 次要文字 / 简介 / 作者 | `--text-secondary` |
| 弱化文字 / 会议信息 / 页脚 / 机构 | `--text-muted` |
| 默认链接 | `--primary-color`；悬停 `--primary-dark` + 下划线 |
| 作者列表中的本人姓名 | `strong` → `--primary-dark`（不要用 `--primary-color`） |
| 会议缩写标签 | `.pub-venue` 内的 `strong` → `--primary-dark` 配 `--bg-accent` |
| 角色徽章（Core Contributor） | `.pub-role` → 白字配 `--primary-color` |
| 研究方向标签 | `--primary-dark` 配 `--bg-accent` |
| 论文序号圆点 | 白字配 `--primary-color` |

不要混入青色 / 青绿 / 红色等另一套强调色，始终用这套蓝色。

## 字体

- 界面 / 正文：`'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif`
- 学术文案（简介与会议行）：`'Source Serif Pro', 'Georgia', 'Noto Sans SC', serif`
- 会议缩写标签和 `.pub-role` 仍用 Inter（无衬线），即使写在 `.pub-venue` 里
- 正文 `line-height: 1.7`；简介 `1.8` 且 `text-align: justify`
- Google Fonts：Inter 400/500/600/700，Noto Sans SC 400/500/700，Source Serif Pro 400/600 以及 italic 400

## 布局

- 页面最大宽度：`.container` 1000px，居中
- `body` 内边距：40px 20px；页面背景 `linear-gradient(160deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%)`
- 页头：白色卡片，`border-radius: 20px`，`padding: 40px`，横向 flex，间距 40px
- 照片：200×227px（`object-fit: cover`），`border-radius: 16px`；移动端 160×181px
- 区块：白色卡片，`border-radius: 16px`，`padding: 32px`，`margin-bottom: 24px`
- 区块标题：1.5rem / 700，`inline-block`，底部 3px 主色下划线
- 断点：`max-width: 768px` — 页头纵向堆叠并居中；奖项改为单列

## 组件写法

### 页头

```html
<header class="header-card">
    <div class="photo-wrapper">
        <a href="PHOTO_FULL_URL"><img src="PHOTO_URL" alt="Photo of Yonggen Ling"></a>
    </div>
    <div class="header-info">
        <h1 class="name">Yonggen Ling</h1>
        <div class="name-cn">凌永根</div>
        <p class="motto">"Do the right thing, and do the thing right"</p>
        <p class="affiliation"><strong>Researcher</strong>, <a href="...">Tencent Robotics X</a></p>
        <p class="email"><strong>Email:</strong> <span id="email-display"></span><!-- 混淆脚本 --></p>
        <div class="social-links"><!-- SVG 图标 --></div>
    </div>
</header>
```

社交图标：24×24 SVG，填充 `--text-secondary`，悬停改为 `--primary-color` 并 `translateY(-2px)`。只用真实 URL，禁止 `YOUR_ID` / `YOUR_USERNAME`。

当前链接：

- Scholar：`https://scholar.google.com/citations?user=P2HB2bsAAAAJ`
- GitHub：`https://github.com/ygling2008`

### Biography

三段。机构名为链接。段间距用 `.biography p + p { margin-top: 12px }`，不要在段落上写内联 `style`。

研究方向：`.interest-tag` 胶囊。术语统一为 **multimodal**（一个词），不要写成 `multi-modal`。

招聘提示只用 Biography 内的 `.highlight-box`。不要改成红色徽章。

### 论文条目（固定三行）

```html
<li>
    <div class="pub-authors">A, B and C</div>
    <div class="pub-title">Paper Title</div>
    <div class="pub-venue">in <em>Full Venue Name</em> <strong>ABBR</strong>, YEAR</div>
</li>
```

有链接和/或角色时，会议信息仍只占 **一行**：

```html
<div class="pub-venue has-links">
    Technical Report, YEAR · <span class="pub-role">Core Contributor</span>
    <span class="pub-links">
        <a href="..." target="_blank" rel="noopener noreferrer">arXiv</a>
        <a href="..." target="_blank" rel="noopener noreferrer">Code</a>
        <a href="..." target="_blank" rel="noopener noreferrer">Model</a>
    </span>
</div>
```

- 本人姓名：`<strong>Yonggen Ling</strong>`
- 共同一作：姓名后紧跟 `*`
- 通讯作者：姓名后紧跟 `&#9993;`（若同时有 `*`，写在 `*` 后面）
- Core Contributor 这类角色用 `.pub-role`，不要用 `<strong>`（该样式留给会议缩写）
- 链接胶囊：`.pub-links a` — 白底、圆角胶囊（`border-radius: 999px`）、`--border-accent` 边框；悬停填充 `--primary-color`
- 标题下的图例：`(*equal contribution, &#9993; corresponding author)`

序号用 `.publication-list` 的 CSS counter，不要写 HTML 数字。

### 奖项

```html
<div class="award-item">
    <div class="award-name">Award name</div>
    <div class="award-org"><a href="...">Org</a>, year(s)</div>
</div>
```

网格：`repeat(auto-fill, minmax(280px, 1fr))`。左侧 3px 主色边框。

### 经历

```html
<li class="experience-item">
    <div class="exp-title">Role, <a href="...">Org</a></div>
    <div class="exp-detail">Mon. YYYY - Mon. YYYY · optional mentors</div>
</li>
```

左侧 4px 主色边框。HTML 里的 `&` 写成 `&amp;`。

## 文案与一致性

**语言：** 美式学术英语。论文标题里已有的英式拼写（如 Miniaturised）保持发表原文。

**用词**

- `immediately after graduation`（不要用 `upon graduation`）
- `groundbreaking`（不要用 `ground-breaking`）
- `Master's` 用 ASCII 撇号
- 各处（meta、schema、简介、标签）统一用 `multimodal`

**作者列表**

- 不用 Oxford comma：`A, B and C`（不是 `A, B, and C`）
- 两名及以上作者时，最后一名前必须有 `and`
- 前面的名字之间只用逗号
- 团队论文：`Tencent Robotics X and Futian Laboratory`（用 `and`，不用 `&`）。更多团队：`Tencent Robotics X, Hy Vision Team and Futian Laboratory`

**会议 / 期刊**

- 会议：`in <em>Full Name</em> <strong>ABBR</strong>, YEAR`
- 期刊 / Transactions：`<em>Full Name</em> <strong>ABBR</strong>, YEAR`（不要加开头的 `in`）
- 技术报告：`Technical Report, YEAR`
- CVPR 全称一律为 `Computer Vision and Pattern Recognition`（不要加 `IEEE International Conference on` 前缀）
- 保留现有缩写标签：ECCV、RSS、CVPR、ICRA、TPAMI、AAAI、ICML、TASE、RAL、IROS、TIP、JFR

**SEO / meta**

- Title、description、OG、Twitter card、JSON-LD `Person` 必须与页面可见身份一致（姓名、中文名、职务、单位、照片 URL、含 multimodal 的研究方向）。
- Favicon：沿用现有的内联 SVG 机器人 emoji。

**页脚**

- 不要硬编码版权年份或 “Last updated”。
- 标记：`© <span id="copyright-year"></span> Yonggen Ling. All rights reserved.` 以及 `Last updated: <span id="last-updated"></span>`。
- 页面加载时用 `document.lastModified` 填写（解析失败则回退到当天）。
- 版权年份：该日期的四位年份。
- Last updated：`en-US` 的长月份 + 日 + 年，例如 `September 4, 2026`。

## 无障碍与交互

- 照片 `alt` 描述人物。
- 社交图标带 `title`。
- 悬停过渡约 0.2s；论文行悬停 `translateX(4px)`。
- 吸顶导航：半透明白底 + `backdrop-filter: blur(10px)`。

## 不要做

- 未经要求不要加 React/Vue、Tailwind 或额外页面。
- 不要把论文链接单独放到第二行会议信息里。
- 不要把 `.pub-venue strong` 拿去标角色或备注。
- 不要留下占位社交 URL。
- 不要引入第二套强调色。
- 不要为了“纠正拼写”改动论文官方标题。

## 新增论文检查清单

1. 按年份插入新 `<li>`（最新在前）。
2. 只用三行结构。
3. 高亮本人姓名；按正确顺序附加 `*` / `&#9993;`。
4. 会议行遵循会议 / 期刊 / 技术报告格式。
5. 若有 arXiv/code/model，在同一会议行加 `.has-links` + `.pub-links`。
6. 若需非作者角色，在同一行用 `.pub-role`。
7. 作者列表标点符合本规范。
8. 不要手改页脚日期；保存 HTML 后由 `document.lastModified` 更新。
