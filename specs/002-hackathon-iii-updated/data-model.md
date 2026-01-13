# Data Model: EmberLearn (Updated)

**Date**: 2026-01-11
**Feature**: 002-hackathon-iii-updated
**Database**: PostgreSQL (prod) / SQLite (dev)
**Migration Tool**: Alembic

---

## Entity Relationship Diagram

```
User
  ├──> ChatMessage (many)
  ├──> ExerciseAttempt (many)
  ├──> UserProgress (many: topic_slug)
  └──> UserStreak (one)

Exercise
  └──> ExerciseAttempt (many)
```

---

## 1. User

**Implementation**: `backend/models/user.py:10`

Fields (high-level):
- `id` (UUID)
- `email` (unique)
- `password_hash`
- `name`
- timestamps

---

## 2. ChatMessage

**Implementation**: `backend/models/chat.py:10`

Fields (high-level):
- `user_id` (FK)
- `message`, `response`
- `agent_type`

---

## 3. Exercise

**Implementation**: `backend/models/exercise.py:10`

Fields (high-level):
- `topic_slug`, `topic_name`
- `starter_code`, `solution`
- `test_cases` (JSON)

---

## 4. ExerciseAttempt

**Implementation**: `backend/models/exercise.py:32`

Fields (high-level):
- `user_id`, `exercise_id` (FK)
- `code`
- `score`, `passed`
- `output`, `error`

---

## 5. UserProgress

**Implementation**: `backend/models/progress.py:10`

Fields (high-level):
- `topic_slug`
- `mastery_score`
- `exercises_completed`
- `quiz_score`, `code_quality_score`

---

## 6. UserStreak

**Implementation**: `backend/models/streak.py:10`

Fields (high-level):
- `current_streak`, `longest_streak`
- `last_activity_date`
- `total_xp`

Derived:
- `level = total_xp // 200 + 1` (`backend/models/streak.py:25`)
