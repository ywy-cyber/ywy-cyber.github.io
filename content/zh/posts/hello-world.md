---
title: "这个站是怎么搭起来的"
date: 2026-11-09
tags: ["建站", "Hugo", "GitHub Pages"]
description: "Hugo + PaperMod + GitHub Actions，整个站点就是一堆 Markdown。"
---

## 技术栈

- **Hugo**（extended v0.169）：把 Markdown 编译成静态页面，构建一次不到一秒。
- **PaperMod** 主题：布局、暗色模式、全文搜索、标签、归档都由它提供。
- **GitHub Actions**：每次 push 到 `main` 后自动构建并发布到 GitHub Pages。

没有任何服务端，没有数据库，也没有要续费的服务器。

## 写一篇文章要做什么

在 `content/zh/posts/` 下新建一个 Markdown 文件，推上去就发布：

```markdown
---
title: "标题"
date: 2026-11-09
tags: ["标签"]
description: "一句话摘要"
---

正文写在这里。
```

英文版放在 `content/en/posts/`，文件同名即可，右上角可以随时切换语言。

## 为什么不用现成的博客平台

三个理由：内容是我自己的纯 Markdown、改样式不受平台限制、站点永远属于我。
