#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""行情拉取脚本：优先调用用户自有行情 API，未配置时走腾讯公开行情兜底。

约定返回（与看板一致）：
  {"quotes": [{"code": "688301", "price": 17.35}, ...]}

用法：
  python3 fetch_quotes.py --codes 688301,300872
  python3 fetch_quotes.py --api "https://your-api.example.com/quote" --key "sk-xxx" --codes 688301
环境变量：
  QUOTE_API_URL  自有行情 API 地址
  QUOTE_API_KEY  自有行情 API Key（随 X-API-Key 头发送）
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (stock-dashboard-skill/1.0)"}


def http_get(url, headers=None, timeout=10):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read().decode("utf-8", errors="replace")


def from_own_api(api, key, codes):
    sep = "&" if "?" in api else "?"
    url = f"{api}{sep}codes={urllib.parse.quote(','.join(codes))}"
    headers = {"Accept": "application/json"}
    if key:
        headers["X-API-Key"] = key
    data = json.loads(http_get(url, headers))
    quotes = data.get("quotes") or data.get("data") or data
    out = []
    for item in quotes:
        code = str(item.get("code", "")).strip()
        price = item.get("price")
        if code and price is not None:
            out.append({"code": code, "price": float(price)})
    return out


def from_tencent(codes):
    """腾讯公开行情兜底：qt.gtimg.cn/q=sh000001,sz399001,sh688301,..."""
    def prefix(code):
        if code.startswith(("sh", "sz", "bj")):
            return code[:2]
        return "sh" if code[0] in "695" else ("bj" if code[0] in "48" else "sz")

    query = ",".join(prefix(c) + c[-6:] for c in codes)
    text = http_get(f"https://qt.gtimg.cn/q={query}")
    out = []
    for chunk in text.split(";"):
        chunk = chunk.strip()
        if "=" not in chunk:
            continue
        payload = chunk.split("=", 1)[1].strip('"')
        fields = payload.split("~")
        if len(fields) < 4:
            continue
        full = chunk.split("=", 1)[0].split("_", 1)[-1].split("v_")[-1]
        code = re.sub(r"^(sh|sz|bj)", "", full)
        price = fields[3]
        if re.fullmatch(r"\d{6}", code) and price:
            out.append({"code": code, "price": float(price)})
    return out


def main():
    parser = argparse.ArgumentParser(description="股票现价拉取")
    parser.add_argument("--codes", required=True,
                        help="代码，逗号分隔。支持 6 位股票代码（如 688301）与指数代码 sh000001,sz399001,sz399006")
    parser.add_argument("--api", default=os.environ.get("QUOTE_API_URL", ""), help="自有行情 API 地址")
    parser.add_argument("--key", default=os.environ.get("QUOTE_API_KEY", ""), help="自有行情 API Key")
    args = parser.parse_args()

    codes = [c.strip() for c in args.codes.split(",") if re.fullmatch(r"(sh|sz|bj)?\d{6}", c.strip())]
    if not codes:
        print(json.dumps({"error": "没有有效的股票或指数代码"}))
        return 1

    quotes, source = [], None
    if args.api:
        try:
            quotes = from_own_api(args.api, args.key, codes)
            source = "own-api"
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"warning": f"自有 API 调用失败：{exc}"}))
    if not quotes:
        try:
            quotes = from_tencent(codes)
            source = "tencent"
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"error": f"行情拉取失败：{exc}"}))
            return 1

    print(json.dumps({"source": source, "quotes": quotes}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
