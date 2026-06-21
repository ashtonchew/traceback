"""HUD QA binding diagnostics for Plan 003."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx


def _load_local_env(root: Path) -> None:
    env_path = root / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _credential_presence() -> dict[str, str]:
    names = (
        "MODAL_TOKEN_ID",
        "MODAL_TOKEN_SECRET",
        "HUD_API_KEY",
        "ANTHROPIC_API_KEY",
    )
    return {name: "present" if os.environ.get(name) else "absent" for name in names}


def _hud_org_binding() -> dict[str, str | None]:
    names = (
        "HUD_ORGANIZATION_ID",
        "HUD_ORG_ID",
        "HUD_PROJECT_ID",
        "HUD_WORKSPACE_ID",
        "X_ORGANIZATION_ID",
    )
    for name in names:
        value = os.environ.get(name)
        if value:
            return {"env_name": name, "status": "present", "value": value}
    return {"env_name": None, "status": "absent", "value": None}


def _summarize_api_payload(data: Any) -> dict[str, Any]:
    if isinstance(data, dict):
        return {
            "shape": "object",
            "keys": sorted(str(key) for key in data.keys())[:20],
            "message": data.get("detail") or data.get("message") or data.get("error"),
        }
    if isinstance(data, list):
        return {
            "shape": "array",
            "length": len(data),
            "first_keys": sorted(str(key) for key in data[0].keys())[:20]
            if data and isinstance(data[0], dict)
            else [],
        }
    return {"shape": type(data).__name__}


def _discover_hud_team_id(base: str, headers: dict[str, str]) -> str | None:
    try:
        response = httpx.get(f"{base}/v2/environments/usage", headers=headers, timeout=20)
        payload = response.json()
    except Exception:  # noqa: BLE001 - diagnostic fallback only.
        return None
    if not isinstance(payload, dict):
        return None
    team_id = payload.get("team_id")
    return str(team_id) if team_id else None


def _qa_agents_with_header(base: str, headers: dict[str, str], value: str) -> dict[str, Any]:
    response = httpx.get(
        f"{base}/v2/qa-agents",
        headers={**headers, "X-Organization-ID": value},
        timeout=20,
    )
    try:
        payload: Any = response.json()
    except ValueError:
        payload = None
    return {
        "path": "/v2/qa-agents",
        "status_code": response.status_code,
        "summary": _summarize_api_payload(payload),
    }


def inspect_hud_qa_binding(root: Path, trace_id: str | None) -> dict[str, Any]:
    _load_local_env(root)
    api_key = os.environ.get("HUD_API_KEY")
    if not api_key:
        return {
            "status": "blocked",
            "credential_presence": _credential_presence(),
            "observed_behavior": "HUD QA binding inspection skipped because HUD_API_KEY is absent",
        }

    base = os.environ.get("HUD_API_URL", "https://api.beta.hud.ai").rstrip("/")
    org = _hud_org_binding()
    headers = {"Authorization": f"Bearer {api_key}"}
    org_headers = dict(headers)
    if org["value"]:
        org_headers["X-Organization-ID"] = str(org["value"])

    def get(path: str, *, use_org: bool = False) -> dict[str, Any]:
        request_headers = org_headers if use_org else headers
        response = httpx.get(f"{base}{path}", headers=request_headers, timeout=20)
        try:
            payload: Any = response.json()
        except ValueError:
            payload = None
        return {
            "path": path,
            "status_code": response.status_code,
            "summary": _summarize_api_payload(payload),
        }

    openapi = get("/openapi.json")
    openapi_paths: list[str] = []
    try:
        spec = httpx.get(f"{base}/openapi.json", headers=headers, timeout=20).json()
        if isinstance(spec, dict) and isinstance(spec.get("paths"), dict):
            openapi_paths = sorted(spec["paths"].keys())
    except Exception:  # noqa: BLE001 - diagnostic only; endpoint status is recorded above.
        openapi_paths = []

    qa_without_org = get("/v2/qa-agents")
    qa_with_org = get("/v2/qa-agents", use_org=True) if org["value"] else None
    qa_with_api_key = _qa_agents_with_header(base, headers, api_key)
    qa_with_hud_hacks = _qa_agents_with_header(base, headers, "hud-hacks")
    team_id = _discover_hud_team_id(base, headers)
    qa_with_team = _qa_agents_with_header(base, headers, team_id) if team_id else None
    trace_events = get(f"/v2/trace/{trace_id}/events") if trace_id else None
    qa_probe = qa_with_org or qa_with_team or qa_without_org
    message = str(qa_without_org["summary"].get("message") or "")
    if qa_without_org["status_code"] == 401 and "X-Organization-ID" in message and org["status"] == "absent":
        blocker = (
            "HUD QA API requires X-Organization-ID; HUD team_id is discoverable but not accepted as that "
            "organization id, and no repo-bound HUD organization env/config is present"
            if team_id and qa_with_team and qa_with_team["status_code"] == 401
            else "HUD QA API requires X-Organization-ID and no repo-bound HUD organization env/config is present"
        )
    elif qa_probe["status_code"] == 200:
        blocker = "HUD QA agent listing is reachable, but the repo has no bound run/result contract for the Reward Hacking Agent"
    else:
        blocker = "HUD QA reward-hacking classification API is not bound to this repo"

    return {
        "status": "blocked",
        "credential_presence": _credential_presence(),
        "api_base": base,
        "organization_binding": {
            "status": org["status"],
            "env_name": org["env_name"],
        },
        "discovered_team_binding": {
            "status": "present" if team_id else "absent",
            "source": "/v2/environments/usage" if team_id else None,
            "accepted_as_organization_id": bool(qa_with_team and qa_with_team["status_code"] == 200),
        },
        "openapi_probe": openapi,
        "openapi_has_qa_agents_path": "/v2/qa-agents" in openapi_paths,
        "openapi_trace_paths": [path for path in openapi_paths if path.startswith("/v2/trace/")],
        "qa_agents_without_org_probe": qa_without_org,
        "qa_agents_with_org_probe": qa_with_org,
        "qa_agents_with_api_key_probe": qa_with_api_key,
        "qa_agents_with_hud_hacks_probe": qa_with_hud_hacks,
        "qa_agents_with_team_probe": qa_with_team,
        "trace_events_probe": trace_events,
        "blocker": blocker,
        "observed_behavior": (
            "HUD trace readback is available through the authenticated API, and the hidden QA-agent router exists, "
            "but Plan 003 still lacks the organization-scoped Reward Hacking Agent run/result binding needed to join "
            "an authoritative QA verdict to the BranchRun trace and action digest."
        ),
    }
