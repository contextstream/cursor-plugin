#!/usr/bin/env python3
"""Opt-in, metadata-only MCP probe. Never calls tools/call or handles OAuth login.

Credentials are read from an environment variable and sent only to the fixed
ContextStream HTTPS endpoint. Raw bodies, tokens, sessions, and schemas are never
printed. This is a protocol diagnostic, NOT a Grok/authorization/workflow test.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler, ProxyHandler

ENDPOINT = "https://mcp.contextstream.io/mcp"
PROTOCOL = "2025-06-18"
SUPPORTED = {"2025-03-26", "2025-06-18"}
MAX_BYTES = 1024 * 1024
MAX_PAGES = 10
MAX_TOOLS = 1000
TIMEOUT = 10
NAME = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")
ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")

class ProbeError(ValueError):
    """Only fixed, credential-free diagnostic messages may leave the transport."""

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProbeError("Duplicate JSON keys in response")
        result[key] = value
    return result

def decode_json(raw):
    try:
        return json.loads(raw, object_pairs_hook=unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(ProbeError("Non-finite JSON value")))
    except (ValueError, UnicodeError, RecursionError):
        raise ProbeError("Invalid JSON response") from None

def rpc_result(value, expected_id):
    if not isinstance(value, dict) or value.get("jsonrpc") != "2.0":
        raise ProbeError("Invalid JSON-RPC envelope")
    if type(value.get("id")) is not int or value["id"] != expected_id:
        raise ProbeError("Response ID mismatch")
    if "error" in value:
        raise ProbeError("Server returned a JSON-RPC error; details withheld")
    if not isinstance(value.get("result"), dict):
        raise ProbeError("Missing JSON-RPC result object")
    return value["result"]

def chunks(response):
    consumed = 0
    deadline = time.monotonic() + TIMEOUT
    while True:
        if time.monotonic() > deadline:
            raise ProbeError("Response time limit exceeded")
        piece = response.read1(min(65536, MAX_BYTES - consumed + 1))
        if not piece:
            return
        consumed += len(piece)
        if consumed > MAX_BYTES:
            raise ProbeError("Response size limit exceeded")
        yield piece

def sse_lines(response):
    line, after_cr = bytearray(), False
    for piece in chunks(response):
        for byte in piece:
            if byte == 13:
                yield bytes(line)
                line.clear()
                after_cr = True
            elif byte == 10:
                if not after_cr:
                    yield bytes(line)
                    line.clear()
                after_cr = False
            else:
                line.append(byte)
                after_cr = False

def read_result(response, expected_id):
    content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
    if content_type == "application/json":
        return rpc_result(decode_json(b"".join(chunks(response))), expected_id)
    if content_type != "text/event-stream":
        raise ProbeError("Unsupported response Content-Type")
    data = []
    for line in sse_lines(response):
        if line.startswith(b"data:"):
            value = line[5:]
            data.append(value[1:] if value.startswith(b" ") else value)
        elif not line and data:
            value = decode_json(b"\n".join(data))
            data = []
            if isinstance(value, dict) and value.get("jsonrpc") == "2.0" and "id" not in value and "method" in value:
                continue
            return rpc_result(value, expected_id)
    raise ProbeError("SSE ended before a complete matching response")

class Transport:
    def __init__(self, token=None, opener=None):
        if token is not None and (not token or len(token) > 8192 or any(ord(c) < 33 or ord(c) > 126 for c in token)):
            raise ProbeError("Invalid credential format")
        self.token = token
        self.opener = opener or build_opener(ProxyHandler({}), NoRedirect())
        self.session = None
        self.protocol = None

    def request(self, method, params=None, request_id=None):
        if method not in {"initialize", "notifications/initialized", "tools/list"}:
            raise ProbeError("Probe method is not metadata-only")
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        if request_id is not None:
            payload["id"] = request_id
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        if self.protocol:
            headers["MCP-Protocol-Version"] = self.protocol
        request = Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with self.opener.open(request, timeout=TIMEOUT) as response:
                if response.geturl() != ENDPOINT:
                    raise ProbeError("Unexpected response location")
                status = response.status
                if request_id is None:
                    if status != 202:
                        raise ProbeError("Initialization notification was not accepted")
                    return None
                if status != 200:
                    raise ProbeError("Unexpected HTTP success status")
                result = read_result(response, request_id)
                session = response.headers.get("Mcp-Session-Id")
                if method == "initialize" and session is not None:
                    if not session or len(session) > 512 or any(ord(c) < 33 or ord(c) > 126 for c in session):
                        raise ProbeError("Invalid session header")
                    self.session = session
                return result
        except HTTPError as exc:
            code = exc.code
            exc.close()
            if code in (401, 403):
                raise ProbeError(f"HTTP {code}: authentication or authorization required; use the host's supported sign-in") from None
            if 300 <= code < 400:
                raise ProbeError("HTTP redirect refused; credentials were not forwarded") from None
            raise ProbeError(f"HTTP {code}: request failed; response details withheld") from None
        except (URLError, OSError, UnicodeError, TimeoutError):
            raise ProbeError("Network or transport error; details withheld") from None

def probe(transport):
    init = transport.request("initialize", {
        "protocolVersion": PROTOCOL, "capabilities": {},
        "clientInfo": {"name": "contextstream-plugin-probe", "version": "0.4.0"}}, 1)
    negotiated = init.get("protocolVersion")
    if not isinstance(negotiated, str) or negotiated not in SUPPORTED:
        raise ProbeError("Unsupported negotiated protocol version")
    capabilities = init.get("capabilities")
    if not isinstance(capabilities, dict) or not isinstance(capabilities.get("tools"), dict):
        raise ProbeError("Server did not advertise tool capability")
    transport.protocol = negotiated
    transport.request("notifications/initialized")
    names, cursors = set(), set()
    cursor = None
    for page in range(MAX_PAGES):
        result = transport.request("tools/list", {"cursor": cursor} if cursor else {}, page + 2)
        tools = result.get("tools")
        if not isinstance(tools, list):
            raise ProbeError("Tool list is not an array")
        for tool in tools:
            if not isinstance(tool, dict) or not isinstance(tool.get("name"), str) or not NAME.fullmatch(tool["name"]):
                raise ProbeError("Invalid tool entry")
            if tool["name"] in names:
                raise ProbeError("Duplicate advertised tool")
            schema = tool.get("inputSchema")
            if not isinstance(schema, dict) or schema.get("type") != "object":
                raise ProbeError("Tool input schema is missing or not an object schema")
            names.add(tool["name"])
        if len(names) > MAX_TOOLS:
            raise ProbeError("Tool-count limit exceeded")
        next_cursor = result.get("nextCursor")
        if next_cursor is None:
            break
        if not isinstance(next_cursor, str) or not next_cursor or len(next_cursor) > 4096 or next_cursor in cursors:
            raise ProbeError("Invalid or repeated pagination cursor")
        cursors.add(next_cursor)
        cursor = next_cursor
    else:
        raise ProbeError("Tool pagination limit exceeded")
    if not {"context", "search"}.issubset(names):
        raise ProbeError("Required ContextStream context/search tools not advertised")
    return {"status": "protocol_ok", "protocol_version": negotiated,
            "credential_supplied": bool(transport.token), "tool_count": len(names),
            "advertised_features": {
                "grounding": "context" in names, "code_search": "search" in names,
                "answer": "answer" in names,
                "recall": "session" in names or "session_recall" in names,
                "graph": "graph" in names or "graph_impact" in names,
                "memory": "memory" in names or "memory_search" in names,
                "diagnostics": "help" in names},
            "not_verified": ["browser_oauth", "client_skill_loading", "project_access",
                             "retrieval_quality", "writes", "revocation", "marketplace_approval"]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", action="store_true", help="Explicitly allow metadata requests to the fixed HTTPS endpoint")
    parser.add_argument("--token-env", default="CONTEXTSTREAM_MCP_TOKEN", help="Environment variable name, never the token itself")
    args = parser.parse_args()
    if not args.network:
        parser.error("No network request made. Pass --network to opt in.")
    if not ENV_NAME.fullmatch(args.token_env):
        parser.error("Invalid environment variable name")
    try:
        result = probe(Transport(os.environ.get(args.token_env)))
    except ProbeError as exc:
        print(json.dumps({"status": "not_verified", "reason": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())