---
title: "GitHub Release 下载 504 —— 用 API 直链绕过去"
date: 2026-11-09
tags: ["排障", "GitHub", "网络"]
description: "release 下载页返回 504 Gateway Time-out 时，怎么从 API 拿到可下载的签名直链。"
---

## 现象

想下载 Hugo 的 Windows 扩展版发布包，`github.com/.../releases/download/...` 这个地址无论直连还是走代理都返回：

```text
HTTP/1.1 504 Gateway Time-out
Content-Length: 92
x-github-edge-region: westus3
```

换三个不同的 tag 试都一样 —— 说明不是某一个包坏了，而是这条下载链路当前不可用。

## 原因

`releases/download/<tag>/<asset>` 由 GitHub 的边缘节点先返回 302，再跳转到 `release-assets.githubusercontent.com` 取文件。
边缘节点自身超时，请求在第一步就断了，根本走不到真正存放文件的域名。

## 解法：走 API 的 asset 端点拿直链

REST API 的 asset 端点不会经过那条出问题的下载链路，它会直接返回 302 到签名直链：

```text
GET https://api.github.com/repos/<owner>/<repo>/releases/assets/<asset_id>
Accept: application/octet-stream
```

签名直链形如 `https://release-assets.githubusercontent.com/github-production-release-asset/...?sig=...`，有效期约一小时，拿到后立刻下载即可。

三步：

1. `GET /repos/<owner>/<repo>/releases/latest` 找到目标 asset 的 `id`；
2. 用 `Accept: application/octet-stream` 请求 `/releases/assets/<id>`，**禁止自动跟随重定向**，从响应头 `Location` 取出直链；
3. 用这个直链下载。

实测 22.5 MB 的 `hugo_extended_0.169.0_windows-amd64.zip` 用这条路 15 秒下完，此前走 `releases/download` 无论直连还是代理都是 504。

## 两个注意点

- 直链是**带签名的临时地址**，会过期，不要存进文档或提交到仓库；
- 下载完要核对文件大小，HTML 错误页也可能被当成文件存下来（十几字节的"压缩包"就是典型症状）。
