"""
Struggle Detection - Identifies When Students Need Help

Detects struggle triggers:
1. Same error 3+ times (REPEATED_ERROR)
2. Stuck >10 minutes on exercise (STUCK_TOO_LONG)
3. Quiz score <50% (LOW_QUIZ_SCORE)
4. Explicit statements like "I don't understand" (EXPLICIT_STATEMENT)
5. 5+ failed code executions in a row (FAILED_EXECUTIONS)

Publishes alerts to Kafka within 30 seconds of detection.
"""

import re
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4
from collections import defaultdict

from .config import settings
from .logging_config import get_logger
from .models import StruggleAlert, StruggleTrigger
from .dapr_client import get_dapr_client

logger = get_logger(__name__)

# Detection thresholds
REPEATED_ERROR_THRESHOLD = 3
STUCK_TIME_MINUTES = 10
LOW_QUIZ_THRESHOLD = 50
FAILED_EXECUTION_THRESHOLD = 5

# Explicit struggle phrases
STRUGGLE_PHRASES = [
    "i don't understand",
    "i dont understand",
    "i'm stuck",
    "im stuck",
    "i am stuck",
    "help me",
    "confused",
    "i'm lost",
    "im lost",
    "i am lost",
    "this is hard",
    "too difficult",
    "can't figure",
    "cant figure",
    "don't get it",
    "dont get it",
    "makes no sense",
    "what am i doing wrong",
    "why doesn't this work",
    "why doesnt this work",
    "frustrated",
    "give up",
]


class StruggleDetector:
    """Detects when students are struggling and publishes alerts."""
    
    def __init__(self):
        self.dapr = get_dapr_client()
        
        # In-memory tracking (would use Redis/Dapr state in production)
        self._error_history: dict[str, list[dict]] = defaultdict(list)
        self._exercise_start_times: dict[str, datetime] = {}
        self._execution_failures: dict[str, int] = defaultdict(int)
        self._recent_alerts: dict[str, datetime] = {}
    
    async def check_error(
        self,
        user_id: str,
        error_type: str,
        topic: str,
        exercise_id: Optional[str] = None,
    ) -> Optional[StruggleAlert]:
        """
        Check for repeated error pattern.
        
        Triggers if same error type occurs 3+ times.
        """
        # Add to error history
        self._error_history[user_id].append({
            "error_type": error_type,
            "timestamp": datetime.utcnow(),
            "topic": topic,
            "exercise_id": exercise_id,
        })
        
        # Keep only last 10 errors
        self._error_history[user_id] = self._error_history[user_id][-10:]
        
        # Count recent occurrences of this error type (last 30 minutes)
        cutoff = datetime.utcnow() - timedelta(minutes=30)
        recent_same_errors = [
            e for e in self._error_history[user_id]
            if e["error_type"] == error_type and e["timestamp"] > cutoff
        ]
        
        if len(recent_same_errors) >= REPEATED_ERROR_THRESHOLD:
            return await self._create_alert(
                user_id=user_id,
                trigger=StruggleTrigger.REPEATED_ERROR,
                topic=topic,
                exercise_id=exercise_id,
                details={
                    "error_type": error_type,
                    "occurrence_count": len(recent_same_errors),
                },
                severity=3,
            )
        
        return None
    
    async def check_time_on_exercise(
        self,
        user_id: str,
        exercise_id: str,
        topic: str,
    ) -> Optional[StruggleAlert]:
        """
        Check if student is stuck on an exercise too long.
        
        Triggers if >10 minutes on same exercise.
        """
        key = f"{user_id}:{exercise_id}"
        
        if key not in self._exercise_start_times:
            self._exercise_start_times[key] = datetime.utcnow()
            return None
        
        start_time = self._exercise_start_times[key]
        elapsed = datetime.utcnow() - start_time
        
        if elapsed > timedelta(minutes=STUCK_TIME_MINUTES):
            # Only alert once per exercise
            alert_key = f"stuck:{key}"
            if alert_key not in self._recent_alerts:
                self._recent_alerts[alert_key] = datetime.utcnow()
                return await self._create_alert(
                    user_id=user_id,
                    trigger=StruggleTrigger.STUCK_TOO_LONG,
                    topic=topic,
                    exercise_id=exercise_id,
                    details={
                        "elapsed_minutes": int(elapsed.total_seconds() / 60),
                    },
                    severity=2,
                )
        
        return None
    
    async def check_quiz_score(
        self,
        user_id: str,
        score: float,
        topic: str,
        quiz_id: Optional[str] = None,
    ) -> Optional[StruggleAlert]:
        """
        Check for low quiz score.
        
        Triggers if score <50%.
        """
        if score < LOW_QUIZ_THRESHOLD:
            return await self._create_alert(
                user_id=user_id,
                trigger=StruggleTrigger.LOW_QUIZ_SCORE,
                topic=topic,
                details={
                    "score": score,
                    "threshold": LOW_QUIZ_THRESHOLD,
                    "quiz_id": quiz_id,
                },
                severity=2,
            )
        
        return None
    
    async def check_message(
        self,
        user_id: str,
        message: str,
        topic: Optional[str] = None,
    ) -> Optional[StruggleAlert]:
        """
        Check for explicit struggle statements.
        
        Triggers if message contains phrases like "I don't understand".
        """
        message_lower = message.lower()
        
        for phrase in STRUGGLE_PHRASES:
            if phrase in message_lower:
                return await self._create_alert(
                    user_id=user_id,
                    trigger=StruggleTrigger.EXPLICIT_STATEMENT,
                    topic=topic or "general",
                    details={
                        "detected_phrase": phrase,
                        "message_preview": message[:100],
                    },
                    severity=4,  # Higher severity for explicit statements
                )
        
        return None
    
    async def check_execution_failure(
        self,
        user_id: str,
        topic: str,
        exercise_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[StruggleAlert]:
        """
        Check for repeated execution failures.
        
        Triggers if 5+ failed executions in a row.
        """
        key = f"{user_id}:{exercise_id or 'general'}"
        self._execution_failures[key] += 1
        
        if self._execution_failures[key] >= FAILED_EXECUTION_THRESHOLD:
            # Reset counter after alert
            failure_count = self._execution_failures[key]
            self._execution_failures[key] = 0
            
            return await self._create_alert(
                user_id=user_id,
                trigger=StruggleTrigger.FAILED_EXECUTIONS,
                topic=topic,
                exercise_id=exercise_id,
                details={
                    "failure_count": failure_count,
                    "last_error": error_message[:200] if error_message else None,
                },
                severity=3,
            )
        
        return None
    
    def reset_execution_failures(self, user_id: str, exercise_id: Optional[str] = None):
        """Reset failure counter on successful execution."""
        key = f"{user_id}:{exercise_id or 'general'}"
        self._execution_failures[key] = 0
    
    def complete_exercise(self, user_id: str, exercise_id: str):
        """Mark exercise as complete, clearing tracking data."""
        key = f"{user_id}:{exercise_id}"
        
        # Clear start time
        if key in self._exercise_start_times:
            del self._exercise_start_times[key]
        
        # Clear failure counter
        if key in self._execution_failures:
            del self._execution_failures[key]
    
    async def _create_alert(
        self,
        user_id: str,
        trigger: StruggleTrigger,
        topic: str,
        exercise_id: Optional[str] = None,
        details: dict = None,
        severity: int = 3,
    ) -> StruggleAlert:
        """Create and publish a struggle alert."""
        # Check for recent duplicate alerts (within 5 minutes)
        alert_key = f"{user_id}:{trigger.value}:{topic}"
        if alert_key in self._recent_alerts:
            last_alert = self._recent_alerts[alert_key]
            if datetime.utcnow() - last_alert < timedelta(minutes=5):
                logger.debug("skipping_duplicate_alert", user_id=user_id, trigger=trigger.value)
                return None
        
        # Create alert
        alert = StruggleAlert(
            id=str(uuid4()),
            user_id=user_id,
            trigger=trigger,
            topic=topic,
            exercise_id=exercise_id,
            details=details or {},
            severity=severity,
        )
        
        # Track alert time
        self._recent_alerts[alert_key] = datetime.utcnow()
        
        # Publish to Kafka (within 30 seconds requirement)
        await self._publish_alert(alert)
        
        logger.info(
            "struggle_alert_created",
            user_id=user_id,
            trigger=trigger.value,
            topic=topic,
            severity=severity,
        )
        
        return alert
    
    async def _publish_alert(self, alert: StruggleAlert) -> None:
        """Publish alert to Kafka via Dapr."""
        try:
            await self.dapr.publish_event(
                topic=settings.kafka_topic_struggle,
                data={
                    "event_type": "struggle_detected",
                    "alert_id": alert.id,
                    "user_id": alert.user_id,
                    "trigger": alert.trigger.value,
                    "topic": alert.topic,
                    "exercise_id": alert.exercise_id,
                    "details": alert.details,
                    "severity": alert.severity,
                    "created_at": alert.created_at.isoformat(),
                },
            )
            logger.info("struggle_alert_published", alert_id=alert.id)
        except Exception as e:
            logger.exception("failed_to_publish_alert", error=str(e))
    
    async def get_active_alerts(self, user_id: str) -> list[dict]:
        """Get active (unresolved) alerts for a user."""
        # In production, this would query the database
        # For now, return recent alerts from memory
        alerts = []
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        for key, timestamp in self._recent_alerts.items():
            if key.startswith(f"{user_id}:") and timestamp > cutoff:
                parts = key.split(":")
                if len(parts) >= 3:
                    alerts.append({
                        "trigger": parts[1],
                        "topic": parts[2],
                        "timestamp": timestamp.isoformat(),
                    })
        
        return alerts


# Global instance
_detector: Optional[StruggleDetector] = None


def get_struggle_detector() -> StruggleDetector:
    """Get or create the global struggle detector instance."""
    global _detector
    if _detector is None:
        _detector = StruggleDetector()
    return _detector
