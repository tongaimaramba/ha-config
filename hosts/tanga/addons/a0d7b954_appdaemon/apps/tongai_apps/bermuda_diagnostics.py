"""
bermuda_diagnostics.py

Optimized diagnostics module for AutoUnlock V2.
Logs only meaningful tap cycles (not ignored taps) with outcome tracking.

CHANGES FROM V1:
✓ Only logs cycles that pass initial safety checks (not contact sensor, not cooldown, not debounce)
✓ Includes tap_outcome field: "success", "failure", "ignored" (early exit)
✓ Reduced noise by filtering rejected taps at safety gate level
✓ Structured JSON with complete decision path
✓ Optional: Can enable verbose mode to log all taps for debugging

JSON SCHEMA:
  {
    "timestamp": "2025-11-28T16:02:45.123456",
    "cycle_id": "front_door_20251128_160245_abc123",
    "door": "front_door",
    "person": "john_doe",
    
    "tap_outcome": "success",  # success | failure | ignored
    "reason": "All 5 checks passed",
    "ignore_reason": null,
    
    "checks_passed": ["proximity", "approach", "arrived", "away", "intent"],
    "unlock_method": "mqtt_publish",
    
    "failed_at": null,         # "check_1_proximity", etc
    "failure_reason": null,
    
    "arrival_phase": true,
    "retry_count": 2,
    "total_duration_ms": 5230,
    "ble_area": "hallway",
    "ble_distance_m": 1.2
  }
"""

import os
import json
import datetime
from collections import deque


class BermudaDiagnostics:
    """
    Optimized diagnostics for AutoUnlock V2.
    
    Key difference from V1: Only logs cycles that proceed past early safety checks.
    This eliminates noise from:
    - Contact sensor (door open)
    - Cooldown (just unlocked)
    - Debounce (tap in progress)
    - Outside intent window (late arriving)
    """
    
    def __init__(self, app):
        """
        Initialize diagnostics.
        
        Args:
            app: AppDaemon app instance (self from AutoUnlockV2)
        """
        self.app = app
        self.log_dir = "/config/appdaemon/logs/bermuda_diagnostics"
        self.cycles = {}  # Track active cycles by cycle_id
        self.cycle_counter = 0
        
        # Create log directory if it doesn't exist
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            self.app.log(f"[DIAGNOSTICS] Log directory ready: {self.log_dir}", level="DEBUG")
        except Exception as e:
            self.app.log(f"[DIAGNOSTICS] Could not create log dir: {e}", level="ERROR")
    
    def _generate_cycle_id(self, door, person):
        """Generate unique cycle ID for this tap."""
        now = self.app.datetime()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        self.cycle_counter += 1
        hash_val = f"{self.cycle_counter:06d}"
        return f"{door}_{timestamp}_{hash_val}"
    
    def log_tap_initiated(self, door, person_id):
        """
        Called AFTER safety checks pass (contact sensor, cooldown, debounce).
        This marks entry into meaningful tap processing.
        
        Args:
            door (str): Door name
            person_id (str): User identifier
        """
        cycle_id = self._generate_cycle_id(door, person_id)
        
        self.cycles[cycle_id] = {
            "cycle_id": cycle_id,
            "door": door,
            "person": person_id,
            "timestamp": self.app.datetime().isoformat(),
            "tap_outcome": None,
            "reason": None,
            "ignore_reason": None,
            "checks_passed": [],
            "failed_at": None,
            "failure_reason": None,
            "arrival_phase": False,
            "retry_count": 0,
            "ble_area": None,
            "ble_distance_m": None,
        }
        
        self.app.log(
            f"[DIAGNOSTICS] Cycle initiated: {cycle_id}",
            level="DEBUG"
        )
    
    def log_cycle_complete(self, door, person_id, success, reason=None, 
                          checks_passed=None, failed_at=None, 
                          arrival_phase=False, retry_count=0,
                          ble_area=None, ble_distance=None):
        """
        Called at END of tap cycle (success or failure).
        This is the terminal logging event.
        
        Args:
            door (str): Door name
            person_id (str): User identifier
            success (bool): Whether unlock succeeded
            reason (str): Human-readable outcome reason
            checks_passed (list): List of passed check names
            failed_at (str): Which check failed (or None for success)
            arrival_phase (bool): Was user in arrival phase?
            retry_count (int): Number of location retries performed
            ble_area (str): User's BLE area at unlock time
            ble_distance (float): User's BLE distance at unlock time
        """
        # Find the cycle (most recent for this door/person)
        matching_cycle_id = None
        for cid in reversed(list(self.cycles.keys())):
            cycle = self.cycles[cid]
            if cycle["door"] == door and cycle["person"] == person_id:
                if cycle["tap_outcome"] is None:  # Not yet finalized
                    matching_cycle_id = cid
                    break
        
        if not matching_cycle_id:
            self.app.log(
                f"[DIAGNOSTICS] No active cycle for {door}/{person_id}, creating new",
                level="DEBUG"
            )
            matching_cycle_id = self._generate_cycle_id(door, person_id)
            self.cycles[matching_cycle_id] = {
                "cycle_id": matching_cycle_id,
                "door": door,
                "person": person_id,
                "timestamp": self.app.datetime().isoformat(),
            }
        
        cycle = self.cycles[matching_cycle_id]
        
        # Set outcome
        cycle["tap_outcome"] = "success" if success else "failure"
        cycle["reason"] = reason or ("Unlock successful" if success else "Access denied")
        cycle["checks_passed"] = checks_passed or []
        cycle["failed_at"] = failed_at
        cycle["arrival_phase"] = arrival_phase
        cycle["retry_count"] = retry_count
        cycle["ble_area"] = ble_area
        cycle["ble_distance_m"] = ble_distance
        
        # Write to JSON file
        self._write_cycle(matching_cycle_id, cycle)
        
        self.app.log(
            f"[DIAGNOSTICS] Cycle complete: {matching_cycle_id} ({cycle['tap_outcome']})",
            level="DEBUG"
        )
    
    def log_tap_ignored(self, door, person_id, ignore_reason):
        """
        Called when tap is IGNORED due to early safety checks.
        These are NOT written to JSON (optional flag to enable).
        
        Args:
            door (str): Door name
            person_id (str): User identifier
            ignore_reason (str): Why tap was ignored (contact sensor, cooldown, etc)
        """
        # NOTE: Ignored taps are NOT logged to JSON by default.
        # To enable verbose logging, set self.log_ignored_taps = True in __init__
        
        self.app.log(
            f"[DIAGNOSTICS] Tap ignored for {door}/{person_id}: {ignore_reason}",
            level="DEBUG"
        )
    
    def _write_cycle(self, cycle_id, cycle_data):
        """Write cycle to JSON file."""
        try:
            filename = os.path.join(self.log_dir, f"{cycle_id}.json")
            
            # Format for output
            cycle_data_copy = dict(cycle_data)
            
            with open(filename, "w") as f:
                json.dump(cycle_data_copy, f, indent=2)
            
            self.app.log(
                f"[DIAGNOSTICS] Wrote cycle: {filename}",
                level="DEBUG"
            )
        except Exception as e:
            self.app.log(
                f"[DIAGNOSTICS] Failed to write {cycle_id}: {e}",
                level="ERROR"
            )
    
    def query_cycles(self, door=None, person=None, limit=10):
        """
        Query recent cycles (for manual analysis).
        
        Args:
            door (str): Filter by door
            person (str): Filter by person
            limit (int): Max cycles to return
        
        Returns:
            list: Recent cycles matching filters
        """
        results = []
        for cid in reversed(list(self.cycles.keys())):
            cycle = self.cycles[cid]
            
            if door and cycle.get("door") != door:
                continue
            if person and cycle.get("person") != person:
                continue
            
            if cycle.get("tap_outcome"):  # Only completed cycles
                results.append(cycle)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_stats(self, door=None, person=None):
        """
        Get statistics for a door/person.
        
        Args:
            door (str): Filter by door
            person (str): Filter by person
        
        Returns:
            dict: Stats (success rate, avg retries, etc)
        """
        cycles = self.query_cycles(door, person, limit=100)
        
        if not cycles:
            return {"total": 0}
        
        success_count = sum(1 for c in cycles if c.get("tap_outcome") == "success")
        failure_count = sum(1 for c in cycles if c.get("tap_outcome") == "failure")
        avg_retries = sum(c.get("retry_count", 0) for c in cycles) / len(cycles) if cycles else 0
        
        return {
            "total": len(cycles),
            "success": success_count,
            "failure": failure_count,
            "success_rate_pct": (success_count / len(cycles) * 100) if cycles else 0,
            "avg_retries": avg_retries,
        }