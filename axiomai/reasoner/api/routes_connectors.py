"""Connector API routes — ingest evidence via webhook and file payloads."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from axiomai.connectors import FileConnector, WebhookConnector

router = APIRouter()
_webhook = WebhookConnector(source="api-webhook")


class WebhookFactsRequest(BaseModel):
    facts: list[str] = Field(default_factory=list)


class FileIngestRequest(BaseModel):
    path: str
    format: str = "auto"  # auto, json, csv


@router.post("/webhook/facts", tags=["Connectors"])
def ingest_webhook_facts(payload: WebhookFactsRequest | dict[str, Any] | list[Any]):
    """Receive facts via webhook (JSON body with ``facts`` list or raw list)."""
    if isinstance(payload, WebhookFactsRequest):
        data: dict[str, Any] | list[Any] = {"facts": payload.facts}
    else:
        data = payload
    facts = _webhook.ingest(data)
    return {
        "received": len(facts),
        "facts": [str(f.predicate) for f in facts],
        "total_buffered": len(_webhook.fetch_evidence()),
    }


@router.get("/webhook/facts", tags=["Connectors"])
def list_webhook_facts():
    """List facts buffered by the webhook connector."""
    facts = _webhook.fetch_evidence()
    return {
        "count": len(facts),
        "facts": [f.to_dict() for f in facts],
    }


@router.delete("/webhook/facts", tags=["Connectors"])
def clear_webhook_facts():
    """Clear the webhook connector buffer."""
    _webhook.clear()
    return {"status": "cleared"}


@router.post("/file/ingest", tags=["Connectors"])
def ingest_file(req: FileIngestRequest):
    """Ingest facts from a JSON or CSV file on the server filesystem."""
    try:
        connector = FileConnector(req.path)
        if not connector.health():
            raise HTTPException(status_code=400, detail=f"Cannot read file: {req.path}")
        facts = connector.fetch_evidence()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {req.path}")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "path": req.path,
        "count": len(facts),
        "facts": [str(f.predicate) for f in facts],
    }


@router.get("/health", tags=["Connectors"])
def connectors_health():
    """Connector subsystem health."""
    return {
        "webhook_buffered": len(_webhook.fetch_evidence()),
        "status": "healthy",
    }
