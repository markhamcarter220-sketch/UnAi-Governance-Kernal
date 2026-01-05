"""
Audit Logger

Provides tamper-evident audit logging for all governance decisions.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


class AuditLogger:
    """
    Audit logger for governance decisions.

    Creates tamper-evident logs of all verification decisions for
    compliance, debugging, and accountability.
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize audit logger.

        Args:
            log_file: Path to log file (None = in-memory only)
        """
        self.log_file = log_file
        self.logs = []
        self.previous_hash = None

    def log_verification(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
        result: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log a verification decision.

        Args:
            context: Original context
            action: Proposed action
            result: VerificationResult
            metadata: Optional metadata

        Returns:
            Audit ID (unique identifier for this log entry)
        """
        audit_id = str(uuid.uuid4())

        log_entry = {
            'audit_id': audit_id,
            'timestamp': datetime.utcnow().isoformat(),
            'context': self._sanitize(context),
            'action': self._sanitize(action),
            'result': {
                'allowed': result.allowed,
                'violations': result.violations,
                'remediation': result.remediation,
                'latency_us': result.latency_us,
            },
            'metadata': metadata or {},
            'previous_hash': self.previous_hash,
        }

        # Calculate hash for tamper evidence
        log_entry['hash'] = self._calculate_hash(log_entry)

        # Update chain
        self.previous_hash = log_entry['hash']

        # Store log
        self.logs.append(log_entry)

        # Write to file if configured
        if self.log_file:
            self._write_to_file(log_entry)

        return audit_id

    def _sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize data for logging (remove sensitive info).
        """
        # In production, implement proper PII/secret scrubbing
        # This is a simplified version
        sanitized = {}
        for key, value in data.items():
            if 'password' in key.lower() or 'secret' in key.lower():
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        return sanitized

    def _calculate_hash(self, log_entry: Dict[str, Any]) -> str:
        """
        Calculate tamper-evident hash of log entry.
        """
        # Create canonical JSON (sorted keys)
        canonical = json.dumps(
            {k: v for k, v in log_entry.items() if k != 'hash'},
            sort_keys=True
        )

        # SHA-256 hash
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _write_to_file(self, log_entry: Dict[str, Any]) -> None:
        """
        Write log entry to file.
        """
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            # In production, handle this more gracefully
            print(f"Warning: Failed to write audit log: {e}")

    def verify_chain(self) -> bool:
        """
        Verify integrity of audit log chain.

        Returns:
            True if chain is valid, False if tampered
        """
        previous_hash = None

        for entry in self.logs:
            # Check previous hash matches
            if entry['previous_hash'] != previous_hash:
                return False

            # Verify hash is correct
            calculated_hash = self._calculate_hash(entry)
            if calculated_hash != entry['hash']:
                return False

            previous_hash = entry['hash']

        return True

    def get_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        allowed_only: bool = False,
        blocked_only: bool = False,
    ) -> list:
        """
        Retrieve audit logs with optional filtering.

        Args:
            start_time: Filter logs after this time
            end_time: Filter logs before this time
            allowed_only: Only return allowed actions
            blocked_only: Only return blocked actions

        Returns:
            List of matching log entries
        """
        filtered = self.logs

        if start_time:
            filtered = [
                log for log in filtered
                if datetime.fromisoformat(log['timestamp']) >= start_time
            ]

        if end_time:
            filtered = [
                log for log in filtered
                if datetime.fromisoformat(log['timestamp']) <= end_time
            ]

        if allowed_only:
            filtered = [
                log for log in filtered
                if log['result']['allowed']
            ]

        if blocked_only:
            filtered = [
                log for log in filtered
                if not log['result']['allowed']
            ]

        return filtered
