from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


class AndroidEnterpriseManager:
    def __init__(self) -> None:
        self._devices = [
            {
                "id": "dev-101",
                "name": "Pixel 8 Sales-01",
                "status": "Compliant",
                "owner": "North Region",
                "last_sync": "2026-03-13 09:00",
            },
            {
                "id": "dev-102",
                "name": "Samsung A54 Support-14",
                "status": "Pending Update",
                "owner": "Service Desk",
                "last_sync": "2026-03-13 08:42",
            },
            {
                "id": "dev-103",
                "name": "Moto G Ops-07",
                "status": "Needs Attention",
                "owner": "Operations",
                "last_sync": "2026-03-13 08:10",
            },
        ]
        self._policies = [
            {
                "id": "policy-default",
                "name": "Default Compliance",
                "scope": "All managed devices",
                "version": "v3.4",
                "updated_at": "2026-03-12 18:25",
            },
            {
                "id": "policy-lockdown",
                "name": "Kiosk Lockdown",
                "scope": "Field agents",
                "version": "v1.9",
                "updated_at": "2026-03-11 16:40",
            },
        ]
        self._activity = [
            self._entry("Policy deployment queued for 42 devices", "success"),
            self._entry("Device inventory sync completed", "info"),
            self._entry("One device reported outdated security patch", "warning"),
        ]

    def summary(self) -> dict[str, Any]:
        compliant = sum(1 for device in self._devices if device["status"] == "Compliant")
        return {
            "managed_devices": len(self._devices),
            "active_policies": len(self._policies),
            "compliant_devices": compliant,
            "pending_alerts": sum(1 for device in self._devices if device["status"] != "Compliant"),
        }

    def available_actions(self) -> list[dict[str, str]]:
        return [
            {
                "id": "apply_policy",
                "label": "Apply Policy",
                "description": "Push the selected enterprise policy with one click.",
            },
            {
                "id": "sync_devices",
                "label": "Sync Devices",
                "description": "Refresh device state from Android Enterprise.",
            },
            {
                "id": "lock_device",
                "label": "Lock Device",
                "description": "Trigger an immediate lock for a selected device.",
            },
            {
                "id": "wipe_device",
                "label": "Wipe Device",
                "description": "Run a secure enterprise wipe command.",
            },
        ]

    def devices(self) -> list[dict[str, Any]]:
        return deepcopy(self._devices)

    def policies(self) -> list[dict[str, Any]]:
        return deepcopy(self._policies)

    def activity(self) -> list[dict[str, str]]:
        return deepcopy(self._activity[:8])

    def run_action(self, action_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        handlers = {
            "apply_policy": self._apply_policy,
            "sync_devices": self._sync_devices,
            "lock_device": self._lock_device,
            "wipe_device": self._wipe_device,
        }
        handler = handlers.get(action_name)
        if not handler:
            return {"ok": False, "message": f"Unknown action: {action_name}"}
        return handler(payload)

    def _apply_policy(self, payload: dict[str, Any]) -> dict[str, Any]:
        policy_id = payload.get("policy_id") or self._policies[0]["id"]
        policy = next((item for item in self._policies if item["id"] == policy_id), None)
        if not policy:
            return {"ok": False, "message": "Policy not found."}

        message = self._run_python_job(
            "apply_policy",
            {
                "policy_id": policy["id"],
                "policy_name": policy["name"],
                "target_devices": len(self._devices),
            },
        )
        self._activity.insert(0, self._entry(message, "success"))
        return {"ok": True, "message": message, "summary": self.summary(), "activity": self.activity()}

    def _sync_devices(self, payload: dict[str, Any]) -> dict[str, Any]:
        del payload
        for device in self._devices:
            device["last_sync"] = self._timestamp()
        message = self._run_python_job("sync_devices", {"devices": len(self._devices)})
        self._activity.insert(0, self._entry(message, "info"))
        return {
            "ok": True,
            "message": message,
            "devices": self.devices(),
            "summary": self.summary(),
            "activity": self.activity(),
        }

    def _lock_device(self, payload: dict[str, Any]) -> dict[str, Any]:
        device = self._find_device(payload.get("device_id"))
        if not device:
            return {"ok": False, "message": "Select a valid device to lock."}
        message = self._run_python_job("lock_device", {"device_id": device["id"], "device_name": device["name"]})
        self._activity.insert(0, self._entry(message, "warning"))
        return {"ok": True, "message": message, "activity": self.activity()}

    def _wipe_device(self, payload: dict[str, Any]) -> dict[str, Any]:
        device = self._find_device(payload.get("device_id"))
        if not device:
            return {"ok": False, "message": "Select a valid device to wipe."}
        message = self._run_python_job("wipe_device", {"device_id": device["id"], "device_name": device["name"]})
        self._activity.insert(0, self._entry(message, "warning"))
        return {"ok": True, "message": message, "activity": self.activity()}

    def _find_device(self, device_id: str | None) -> dict[str, Any] | None:
        if not device_id:
            return None
        return next((item for item in self._devices if item["id"] == device_id), None)

    def _run_python_job(self, job_name: str, context: dict[str, Any]) -> str:
        """
        Replace this method with real Android Enterprise API logic or a subprocess
        call to your existing Python automation scripts.
        """
        if job_name == "apply_policy":
            return f"{context['policy_name']} deployed to {context['target_devices']} devices."
        if job_name == "sync_devices":
            return f"Device inventory synced for {context['devices']} managed devices."
        if job_name == "lock_device":
            return f"Lock command sent to {context['device_name']}."
        if job_name == "wipe_device":
            return f"Wipe command queued for {context['device_name']}."
        return f"Job {job_name} completed."

    def _entry(self, message: str, level: str) -> dict[str, str]:
        return {"message": message, "level": level, "timestamp": self._timestamp()}

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M")
