#!/usr/bin/env python3
"""Download every file in a public ("anyone with the link") Google Drive folder.

    python3 -I toolkit/fetch_drive.py <folder URL or id> <out dir>

Videos and other files come down through drive.usercontent.google.com (gdown's
redirect host, *.googleusercontent.com, is blocked in the cloud environment).
Google Docs are saved as plain text (<title>.txt) from their mobilebasic view.
Needs these hosts allowed: drive.google.com, drive.usercontent.google.com, docs.google.com.
"""
import html, json, os, re, sys, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()

src, out = sys.argv[1], sys.argv[2]
fid = re.search(r"folders/([A-Za-z0-9_-]+)", src)
fid = fid.group(1) if fid else src
os.makedirs(out, exist_ok=True)
page = get(f"https://drive.google.com/embeddedfolderview?id={fid}").decode("utf8", "ignore")
entries = re.findall(r'href="([^"]+)".*?flip-entry-title">([^<]*)', page, re.S)
manifest = []
for href, title in entries:
    title = html.unescape(title).strip()
    safe = re.sub(r"[^\w.\- ]+", "_", title).strip() or "untitled"
    m = re.search(r"/file/d/([A-Za-z0-9_-]+)", href)
    if m:
        dest = os.path.join(out, safe)
        print(f"file  {title}", flush=True)
        urllib.request.urlretrieve(
            f"https://drive.usercontent.google.com/download?id={m.group(1)}&export=download&confirm=t", dest)
        manifest.append({"title": title, "id": m.group(1), "path": dest, "bytes": os.path.getsize(dest)})
        continue
    d = re.search(r"/document/d/([A-Za-z0-9_-]+)", href) or re.search(r"id=([A-Za-z0-9_-]{25,})", href)
    if d or "docs.google.com" in href:
        doc_id = d.group(1) if d else None
        if not doc_id:
            continue
        t = get(f"https://docs.google.com/document/d/{doc_id}/mobilebasic").decode("utf8", "ignore")
        t = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", t, flags=re.S)
        t = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</h\d>", "\n", t)
        t = re.sub(r"\n\s*\n+", "\n", html.unescape(re.sub(r"<[^>]+>", "", t)))
        dest = os.path.join(out, safe + ".txt")
        open(dest, "w", encoding="utf8").write(t)
        print(f"doc   {title}", flush=True)
        manifest.append({"title": title, "id": doc_id, "path": dest, "kind": "doc"})
    else:
        print(f"skip  {title} (folder or unsupported link: {href[:80]})")
json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), ensure_ascii=False, indent=1)
print(f"{len(manifest)} item(s) -> {out}")
