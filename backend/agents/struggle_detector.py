"""
Struggle Detector - Identifies when students need additional help.

Triggers:
1. 3+ same error type in 10 minutes
2. 5+ failed code executions in a row
3. Quiz score below 50%
4. No progress on exercise for 15+ minutes
5. Explicit help request keywords
"""

import time
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
import structlog

logger = structlog.get_logger()


@dataclass
class StruggleEvent:
    student_id: str
    trigger: str
    details: dict
    timestamp: float = field(default_factory=time.time)
    severity: str = "medium"  # low, medium, high


class StruggleDetector:
    """Detects when students are struggling and need intervention."""

    def __init__(self):
        # Track error history per student: {student_id: [(error_type, timestamp), ...]}
        self.error_history: dict[str, list[tuple[str, float]]] = defaultdict(list)

        # Track failed executions: {student_id: [timestamp, ...]}
        self.failed_executions: dict[str, list[float]] = defaultdict(list)

        # Track exercise start times: {student_id: {exercise_id: start_time}}
        self.exercise_starts: dict[str, dict[str, float]] = defaultdict(dict)

        # Time windows
        self.ERROR_WINDOW_SECONDS = 600  # 10 minutes
        self.EXECUTION_WINDOW_COUNT = 5  # consecutive failures
        self.EXERCISE_STALL_MINUTES = 15

    def _cleanup_old_entries(self, student_id: str) -> None:
        """Remove entries older than the time window."""
        current_time = time.time()
        cutoff = current_time - self.ERROR_WINDOW_SECONDS

        # Clean error history
        self.error_history[student_id] = [
            (err, ts) for err, ts in self.error_history[student_id] if ts > cutoff
        ]

    def check_repeated_errors(
        self, student_id: str, error_type: str
    ) -> Optional[StruggleEvent]:
        """
        Trigger 1: 3+ same error type in 10 minutes.
        """
        current_time = time.time()
        self._cleanup_old_entries(student_id)

        # Add new error
        self.error_history[student_id].append((error_type, current_time))

        # Count same error type
        same_errors = sum(
            1 for err, _ in self.error_history[student_id] if err == error_type
        )

        if same_errors >= 3:
            logger.info(
                "struggle_detected",
                trigger="repeated_errors",
                student_id=student_id,
                error_type=error_type,
                count=same_errors,
            )
            return StruggleEvent(
                student_id=student_id,
                trigger="repeated_errors",
                details={
                    "error_type": error_type,
                    "count": same_errors,
                    "window_minutes": self.ERROR_WINDOW_SECONDS // 60,
                },
                severity="medium",
            )
        return None

    def check_failed_executions(
        self, student_id: str, success: bool
    ) -> Optional[StruggleEvent]:
        """
        Trigger 2: 5+ failed code executions in a row.
        """
        if success:
            # Reset on success
            self.failed_executions[student_id] = []
            return None

        current_time = time.time()
        self.failed_executions[student_id].append(current_time)

        # Keep only recent failures
        self.failed_executions[student_id] = self.failed_executions[student_id][
            -self.EXECUTION_WINDOW_COUNT :
        ]

        if len(self.failed_executions[student_id]) >= self.EXECUTION_WINDOW_COUNT:
            logger.info(
                "struggle_detected",
                trigger="failed_executions",
                student_id=student_id,
                count=len(self.failed_executions[student_id]),
            )
            return StruggleEvent(
                student_id=student_id,
                trigger="failed_executions",
                details={"consecutive_failures": self.EXECUTION_WINDOW_COUNT},
                severity="high",
            )
        return None

    def check_quiz_score(
        self, student_id: str, score: float, topic: str
    ) -> Optional[StruggleEvent]:
        """
        Trigger 3: Quiz score below 50%.
        """
        if score < 50:
            logger.info(
                "struggle_detected",
                trigger="low_quiz_score",
                student_id=student_id,
                score=score,
                topic=topic,
            )
            return StruggleEvent(
                student_id=student_id,
                trigger="low_quiz_score",
                details={"score": score, "topic": topic, "threshold": 50},
                severity="medium",
            )
        return None

    def start_exercise(self, student_id: str, exercise_id: str) -> None:
        """Track when a student starts an exercise."""
        self.exercise_starts[student_id][exercise_id] = time.time()

    def check_exercise_stall(
        self, student_id: str, exercise_id: str
    ) -> Optional[StruggleEvent]:
        """
        Trigger 4: No progress on exercise for 15+ minutes.
        """
        start_time = self.exercise_starts.get(student_id, {}).get(exercise_id)
        if not start_time:
            return None

        elapsed_minutes = (time.time() - start_time) / 60

        if elapsed_minutes >= self.EXERCISE_STALL_MINUTES:
            logger.info(
                "struggle_detected",
                trigger="exercise_stall",
                student_id=student_id,
                exercise_id=exercise_id,
                elapsed_minutes=elapsed_minutes,
            )
            return StruggleEvent(
                student_id=student_id,
                trigger="exercise_stall",
                details={
                    "exercise_id": exercise_id,
                    "elapsed_minutes": int(elapsed_minutes),
                    "threshold_minutes": self.EXERCISE_STALL_MINUTES,
                },
                severity="low",
            )
        return None

    def complete_exercise(self, student_id: str, exercise_id: str) -> None:
        """Mark exercise as completed, stop tracking."""
        if student_id in self.exercise_starts:
            self.exercise_starts[student_id].pop(exercise_id, None)

    def check_help_keywords(
        self, student_id: str, query: str
    ) -> Optional[StruggleEvent]:
        """
        Trigger 5: Explicit help request keywords.
        """
        help_keywords = [
            "i don't understand",
            "i'm stuck",
            "help me",
            "confused",
            "frustrated",
            "give up",
            "too hard",
            "can't figure",
            "doesn't make sense",
        ]

        query_lower = query.lower()
        for keyword in help_keywords:
            if keyword in query_lower:
                logger.info(
                    "struggle_detected",
                    trigger="help_keyword",
                    student_id=student_id,
                    keyword=keyword,
                )
                return StruggleEvent(
                    student_id=student_id,
                    trigger="help_keyword",
                    details={"keyword": keyword, "query": query[:100]},
                    severity="high",
                )
        return None


# Global instance
struggle_detector = StruggleDetector()
