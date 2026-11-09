"""在 GitHub Actions runner 上安装指定版本的 Hugo extended。

为什么不直接用 peaceiris/actions-hugo：
    它从 github.com/<owner>/<repo>/releases/download/ 下载，该链路在 2026-11-09
    整段返回 504 Gateway Time-out。这里改走 REST API 的 asset 端点，
    拿 302 的签名直链再下载，只经过 api.github.com 与 release-assets.githubusercontent.com。

用法（workflow 内）：
    GH_TOKEN=... HUGO_VERSION=0.169.0 python3 .github/scripts/install_hugo.py
脚本会把 hugo 放到 $RUNNER_TEMP/hugo-bin，并把该目录写进 $GITHUB_PATH。
"""

import json
import os
import sys
import tarfile
import urllib.error
import urllib.request
from pathlib import Path

VERSION = os.environ.get("HUGO_VERSION", "0.169.0").lstrip("v")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
NAME = f"hugo_extended_{VERSION}_linux-amd64.tar.gz"
REPO_API = "https://api.github.com/repos/gohugoio/hugo"
UA = {"User-Agent": "nyami-actions"}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        return None


def fetch_asset_id():
    url = f"{REPO_API}/releases/tags/v{VERSION}"
    headers = dict(UA, Accept="application/vnd.github+json")
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as resp:
        release = json.load(resp)
    for asset in release.get("assets", []):
        if asset.get("name") == NAME:
            return asset["id"]
    available = [a.get("name") for a in release.get("assets", [])][:5]
    raise SystemExit(f"未找到资产 {NAME}；样例：{available}")


def signed_url(asset_id):
    headers = dict(UA, Accept="application/octet-stream")
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        opener.open(
            urllib.request.Request(f"{REPO_API}/releases/assets/{asset_id}", headers=headers),
            timeout=60,
        )
        raise SystemExit("asset 端点没有返回 302，无法取到直链")
    except urllib.error.HTTPError as err:
        if err.code != 302:
            raise SystemExit(f"asset 端点返回 {err.code}：{err.read()[:200]!r}") from err
        location = err.headers.get("Location")
        if not location:
            raise SystemExit("302 响应缺少 Location 头")
        return location


def download(url, dest):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return len(data)


def main():
    runner_temp = Path(os.environ.get("RUNNER_TEMP", "/tmp"))
    dest_dir = runner_temp / "hugo-bin"
    dest_dir.mkdir(parents=True, exist_ok=True)
    tarball = runner_temp / NAME

    try:
        asset_id = fetch_asset_id()
        print(f"asset id: {asset_id}", flush=True)
        url = signed_url(asset_id)
        print("已取得签名直链（不打印内容）", flush=True)
    except (SystemExit, urllib.error.URLError) as err:
        # 兜底：release 通道若恢复，直接下载更省事
        print(f"API 路径失败（{err}），回退到 releases/download", flush=True)
        url = f"https://github.com/gohugoio/hugo/releases/download/v{VERSION}/{NAME}"

    size = download(url, tarball)
    print(f"下载完成：{tarball}（{size / 1024 / 1024:.1f} MB）", flush=True)

    with tarfile.open(tarball, "r:gz") as tar:
        member = next((m for m in tar.getmembers() if m.name == "hugo"), None)
        if member is None:
            raise SystemExit("压缩包内没有 hugo 可执行文件")
        tar.extract(member, dest_dir, filter="data")

    hugo = dest_dir / "hugo"
    hugo.chmod(0o755)
    print(f"hugo 就位：{hugo}", flush=True)

    github_path = os.environ.get("GITHUB_PATH")
    if github_path:
        with open(github_path, "a", encoding="utf-8") as fh:
            fh.write(str(dest_dir) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
