---
title: "GitHub release downloads return 504 — go through the API asset endpoint"
date: 2026-11-09
tags: ["troubleshooting", "GitHub", "network"]
description: "What to do when a release download page answers 504 Gateway Time-out: fetch the signed direct URL from the REST API instead."
---

## Symptom

Downloading Hugo's extended Windows build from `github.com/.../releases/download/...` returned, both directly and through a proxy:

```text
HTTP/1.1 504 Gateway Time-out
Content-Length: 92
x-github-edge-region: westus3
```

Three different tags behaved identically — so a single broken asset was ruled out; the whole download path was unavailable.

## Cause

The `releases/download/<tag>/<asset>` URL is answered by a GitHub edge node, which returns a 302 to `release-assets.githubusercontent.com` before the file is served. The edge node itself timed out, so the request died before reaching the domain that actually holds the bytes.

## Fix: get the direct link from the API asset endpoint

The REST API asset endpoint does not go through that failing path — it answers 302 with a signed direct URL:

```text
GET https://api.github.com/repos/<owner>/<repo>/releases/assets/<asset_id>
Accept: application/octet-stream
```

The signed URL looks like `https://release-assets.githubusercontent.com/github-production-release-asset/...?sig=...` and is valid for roughly an hour.

Three steps:

1. `GET /repos/<owner>/<repo>/releases/latest` and find the target asset `id`;
2. request `/releases/assets/<id>` with `Accept: application/octet-stream`, **without following redirects**, and read `Location` from the response headers;
3. download from that URL.

Measured: the 22.5 MB `hugo_extended_0.169.0_windows-amd64.zip` came down in 15 seconds this way, while `releases/download` returned 504 both directly and via proxy.

## Two caveats

- The direct URL is **signed and temporary** — never store it in docs or commit it;
- verify the file size afterwards: error pages can be saved as if they were files (a "zip" of a few dozen bytes is the classic tell).
