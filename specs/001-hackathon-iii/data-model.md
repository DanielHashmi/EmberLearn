# Data Model: EmberLearn

**Date**: 2026-01-05
**Feature**: 001-hackathon-iii
**Database**: Neon PostgreSQL (serverless)
**Migration Tool**: Alembic

---

## Entity Relationship Diagram

```
User (Student/Teacher/Admin)
  ├──> Progress (many: topics × mastery scores)
  ├──> ExerciseSubmission (many: attempts)
  ├──> QuizAttempt (many: quiz results)
  └──> StruggleAlert (many: detected struggles)

Topic
  ├──> Exercise (many: coding challenges)
  ├──> Quiz (many: assessment questions)
  └──> Progress (many: student mastery per topic)

Exercise
  ├──> TestCase (many: validation criteria)
  └──> ExerciseSubmission (many: student attempts)

Event
  └──> Kafka topics (external, not in PostgreSQL)
```

---

## 1. User

**Purpose**: Students, teachers, and admins with authentication and profile data.

**Identity Strategy**: Numeric ID (primary key) + UUID (for cross-service references, JWT claims, Kafka partition keys)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Numeric ID for database relations |
| `uuid` | UUID | UNIQUE, NOT NULL, DEFAULT gen_random_uuid() | Global identifier for services |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Authentication identifier |
| `password_hash` | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| `role` | ENUM('student', 'teacher', 'admin') | NOT NULL, DEFAULT 'student' | Role-based access control |
| `first_name` | VARCHAR(100) | NOT NULL | Display name |
| `last_name` | VARCHAR(100) | NOT NULL | Display name |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last profile update |
| `last_login_at` | TIMESTAMP | NULL | Last successful authentication |

**Indexes**:
- `idx_user_uuid` on `uuid` (for JWT lookups)
- `idx_user_email` on `email` (for login)

**Validation Rules**:
- Email must be valid format (regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
- Password must be ≥8 characters with uppercase, lowercase, digit, special char
- Role must be one of: student, teacher, admin

**State Transitions**: None (stateless entity)

---

## 2. Topic

**Purpose**: Python curriculum modules (8 topics from spec: Basics, Control Flow, Data Structures, Functions, OOP, Files, Errors, Libraries).

**Identity Strategy**: Numeric ID (primary key)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Numeric ID |
| `slug` | VARCHAR(100) | UNIQUE, NOT NULL | URL-friendly identifier (e.g., "control-flow") |
| `name` | VARCHAR(100) | NOT NULL | Display name (e.g., "Control Flow") |
| `description` | TEXT | NOT NULL | Topic overview |
| `order` | INTEGER | NOT NULL | Display sequence (1-8) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Topic creation timestamp |

**Indexes**:
- `idx_topic_slug` on `slug` (for routing)
- `idx_topic_order` on `order` (for curriculum display)

**Validation Rules**:
- Slug must match pattern: `^[a-z0-9-]+$`
- Order must be 1-8 (8 topics total)

**Initial Data** (seeded via migration):

```sql
INSERT INTO topics (slug, name, description, "order") VALUES
('basics', 'Python Basics', 'Variables, data types, operators', 1),
('control-flow', 'Control Flow', 'If statements, loops (for/while)', 2),
('data-structures', 'Data Structures', 'Lists, tuples, dicts, sets', 3),
('functions', 'Functions', 'Defining functions, parameters, return values', 4),
('oop', 'Object-Oriented Programming', 'Classes, inheritance, polymorphism', 5),
('files', 'File Handling', 'Reading/writing files, context managers', 6),
('errors', 'Error Handling', 'Try/except, raising exceptions, debugging', 7),
('libraries', 'Standard Library', 'Common modules (math, random, datetime)', 8);
```

---

## 3. Progress

**Purpose**: Track student mastery per topic using weighted formula.

**Identity Strategy**: Composite key (`user_id`, `topic_id`)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL | Student reference |
| `topic_id` | INTEGER | FOREIGN KEY (topics.id), NOT NULL | Topic reference |
| `exercise_completion_pct` | DECIMAL(5,2) | NOT NULL, DEFAULT 0.00, CHECK (0 <= value <= 100) | % of exercises completed (40% weight) |
| `quiz_score_avg` | DECIMAL(5,2) | NOT NULL, DEFAULT 0.00, CHECK (0 <= value <= 100) | Average quiz score (30% weight) |
| `code_quality_avg` | DECIMAL(5,2) | NOT NULL, DEFAULT 0.00, CHECK (0 <= value <= 100) | Average code quality rating (20% weight) |
| `consistency_score` | DECIMAL(5,2) | NOT NULL, DEFAULT 0.00, CHECK (0 <= value <= 100) | Streak/consistency (10% weight) |
| `mastery_score` | DECIMAL(5,2) | NOT NULL, DEFAULT 0.00, CHECK (0 <= value <= 100) | Computed weighted score |
| `mastery_level` | ENUM('beginner', 'learning', 'proficient', 'mastered') | NOT NULL, DEFAULT 'beginner' | Color-coded level |
| `last_activity_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last interaction timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last recalculation |

**Primary Key**: `(user_id, topic_id)`

**Indexes**:
- `idx_progress_user` on `user_id` (for student dashboard)
- `idx_progress_topic` on `topic_id` (for topic analytics)
- `idx_progress_mastery` on `mastery_score` (for leaderboards)

**Validation Rules**:
- All percentages must be 0-100
- Mastery score calculation (enforced by trigger):
  ```sql
  mastery_score = (exercise_completion_pct * 0.40) +
                  (quiz_score_avg * 0.30) +
                  (code_quality_avg * 0.20) +
                  (consistency_score * 0.10)
  ```
- Mastery level mapping (enforced by trigger):
  - 0-40%: 'beginner' (Red)
  - 41-70%: 'learning' (Yellow)
  - 71-90%: 'proficient' (Green)
  - 91-100%: 'mastered' (Blue)

**State Transitions**:
```
beginner → learning → proficient → mastered
(Can also regress if consistency drops)
```

---

## 4. Exercise

**Purpose**: Coding challenges generated by Exercise agent or pre-defined.

**Identity Strategy**: Numeric ID + UUID for event correlation

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Numeric ID |
| `uuid` | UUID | UNIQUE, NOT NULL, DEFAULT gen_random_uuid() | Event correlation ID |
| `topic_id` | INTEGER | FOREIGN KEY (topics.id), NOT NULL | Associated topic |
| `title` | VARCHAR(200) | NOT NULL | Exercise name |
| `description` | TEXT | NOT NULL | Instructions and context |
| `difficulty` | ENUM('easy', 'medium', 'hard') | NOT NULL | Difficulty level |
| `starter_code` | TEXT | NOT NULL, DEFAULT '' | Initial code template |
| `solution_code` | TEXT | NOT NULL | Reference solution |
| `created_by` | INTEGER | FOREIGN KEY (users.id), NULL | Creator (NULL = AI-generated) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- `idx_exercise_uuid` on `uuid` (for Kafka events)
- `idx_exercise_topic` on `topic_id` (for topic exercises list)
- `idx_exercise_difficulty` on `difficulty` (for filtering)

**Validation Rules**:
- Difficulty must be: easy, medium, hard
- Solution code must pass all associated test cases

---

## 5. TestCase

**Purpose**: Validation criteria for exercises (input → expected output).

**Identity Strategy**: Numeric ID

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Numeric ID |
| `exercise_id` | INTEGER | FOREIGN KEY (exercises.id, ON DELETE CASCADE), NOT NULL | Associated exercise |
| `input_data` | TEXT | NOT NULL | Test input (JSON or string) |
| `expected_output` | TEXT | NOT NULL | Expected result |
| `is_hidden` | BOOLEAN | NOT NULL, DEFAULT FALSE | Hidden from students (edge case testing) |
| `weight` | DECIMAL(3,2) | NOT NULL, DEFAULT 1.00 | Test case weight (for grading) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- `idx_testcase_exercise` on `exercise_id` (for exercise validation)

**Validation Rules**:
- Weight must be > 0
- Must have at least 1 visible test case per exercise

---

## 6. ExerciseSubmission

**Purpose**: Student attempts at exercises with auto-grading results.

**Identity Strategy**: Numeric ID + UUID for event correlation

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Numeric ID |
| `uuid` | UUID | UNIQUE, NOT NULL, DEFAULT gen_random_uuid() | Event correlation ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL | Student reference |
| `exercise_id` | INTEGER | FOREIGN KEY (exercises.id), NOT NULL | Exercise reference |
| `code` | TEXT | NOT NULL | Submitted code |
| `execution_result` | JSONB | NOT NULL | Sandbox execution output |
| `test_results` | JSONB | NOT NULL | Test case pass/fail results |
| `passed_count` | INTEGER | NOT NULL, DEFAULT 0 | Number of tests passed |
| `total_count` | INTEGER | NOT NULL | Total test cases |
| `score` | DECIMAL(5,2) | NOT NULL, DEFAULT 0.00, CHECK (0 <= value <= 100) | Weighted score |
| `code_quality_rating` | DECIMAL(5,2) | NULL, CHECK (0 <= value <= 100) | Code Review agent rating |
| `status` | ENUM('pending', 'passed', 'failed', 'error') | NOT NULL, DEFAULT 'pending' | Submission status |
| `submitted_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Submission timestamp |

**Indexes**:
- `idx_submission_uuid` on `uuid` (for Kafka events)
- `idx_submission_user_exercise` on `(user_id, exercise_id)` (for student history)
- `idx_submission_status` on `status` (for filtering)

**Validation Rules**:
- Score = (passed_count / total_count) * 100
- Status transitions: `pending → passed | failed | error`

**JSONB Structures**:

**execution_result**:
```json
{
  "success": true,
  "stdout": "Hello, World!\n",
  "stderr": "",
  "returncode": 0,
  "execution_time_ms": 45
}
```

**test_results**:
```json
{
  "test_cases": [
    {
      "test_id": 1,
      "passed": true,
      "expected": "Hello, World!",
      "actual": "Hello, World!",
      "weight": 1.0
    },
    {
      "test_id": 2,
      "passed": false,
      "expected": "42",
      "actual": "43",
      "weight": 1.5,
      "error": "Assertion failed"
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 1,
    "total": 2
  }
}
```

---

## 7. Quiz

**Purpose**: Multiple-choice assessments per topic.

**Identity Strategy**: Numeric ID

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Numeric ID |
| `topic_id` | INTEGER | FOREIGN KEY (topics.id), NOT NULL | Associated topic |
| `question` | TEXT | NOT NULL | Question text |
| `options` | JSONB | NOT NULL | Answer choices |
| `correct_answer` | VARCHAR(1) | NOT NULL, CHECK (value IN ('A', 'B', 'C', 'D')) | Correct option |
| `explanation` | TEXT | NOT NULL | Why this answer is correct |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- `idx_quiz_topic` on `topic_id` (for topic quizzes)

**JSONB Structure** (options):
```json
{
  "A": "for i in range(10):",
  "B": "for i in 10:",
  "C": "for i = 0 to 10:",
  "D": "foreach i in range(10):"
}
```

---

## 8. QuizAttempt

**Purpose**: Student quiz attempts with scores.

**Identity Strategy**: Numeric ID

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Numeric ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL | Student reference |
| `topic_id` | INTEGER | FOREIGN KEY (topics.id), NOT NULL | Topic reference |
| `answers` | JSONB | NOT NULL | Student's answers |
| `correct_count` | INTEGER | NOT NULL, DEFAULT 0 | Number correct |
| `total_count` | INTEGER | NOT NULL | Total questions |
| `score` | DECIMAL(5,2) | NOT NULL, DEFAULT 0.00, CHECK (0 <= value <= 100) | Percentage score |
| `completed_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Completion timestamp |

**Indexes**:
- `idx_quizattempt_user_topic` on `(user_id, topic_id)` (for progress calculation)

**JSONB Structure** (answers):
```json
{
  "quiz_id_1": {"selected": "A", "correct": "A", "is_correct": true},
  "quiz_id_2": {"selected": "C", "correct": "B", "is_correct": false}
}
```

---

## 9. StruggleAlert

**Purpose**: Detect and alert teachers when students are struggling.

**Identity Strategy**: Numeric ID + UUID for event correlation

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Numeric ID |
| `uuid` | UUID | UNIQUE, NOT NULL, DEFAULT gen_random_uuid() | Event correlation ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL | Student reference |
| `topic_id` | INTEGER | FOREIGN KEY (topics.id), NULL | Related topic (if applicable) |
| `trigger_type` | ENUM('same_error_3x', 'stuck_10min', 'quiz_fail', 'explicit_help', 'failed_executions_5x') | NOT NULL | Trigger condition |
| `trigger_data` | JSONB | NOT NULL | Context-specific details |
| `severity` | ENUM('low', 'medium', 'high') | NOT NULL, DEFAULT 'medium' | Alert priority |
| `resolved` | BOOLEAN | NOT NULL, DEFAULT FALSE | Teacher acknowledged |
| `resolved_by` | INTEGER | FOREIGN KEY (users.id), NULL | Teacher who resolved |
| `resolved_at` | TIMESTAMP | NULL | Resolution timestamp |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Alert creation timestamp |

**Indexes**:
- `idx_strugglealert_uuid` on `uuid` (for Kafka events)
- `idx_strugglealert_user` on `user_id` (for student alerts)
- `idx_strugglealert_unresolved` on `resolved` WHERE `resolved = FALSE` (for teacher dashboard)

**JSONB Structure** (trigger_data):

**same_error_3x**:
```json
{
  "error_type": "NameError",
  "error_message": "name 'x' is not defined",
  "occurrences": 3,
  "exercise_id": 42,
  "last_occurrence_at": "2026-01-05T10:30:45Z"
}
```

**stuck_10min**:
```json
{
  "exercise_id": 42,
  "started_at": "2026-01-05T10:20:00Z",
  "last_submission_at": "2026-01-05T10:21:30Z",
  "duration_minutes": 15
}
```

**quiz_fail**:
```json
{
  "quiz_attempt_id": 10,
  "score": 30.0,
  "threshold": 50.0,
  "topic_id": 2
}
```

---

## 10. Event (Kafka - Not in PostgreSQL)

**Purpose**: Distributed event-driven communication between microservices.

**Identity Strategy**: UUID (message key and correlation ID)

**Topics**:
- `learning.query` - Student asks question
- `learning.response` - Agent responds
- `code.submitted` - Student submits code
- `code.executed` - Sandbox execution result
- `exercise.assigned` - New exercise created
- `exercise.completed` - Student completes exercise
- `struggle.detected` - Struggle alert triggered

**Message Structure** (all topics):
```json
{
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "student_id": 42,
  "event_type": "code.submitted",
  "timestamp": "2026-01-05T10:30:45.123456Z",
  "payload": {
    // Event-specific data
  }
}
```

**Partition Key**: `student_id` (ensures ordered processing per student)

---

## Database Migrations

**Tool**: Alembic

**Migration Strategy**:
1. **Initial migration** (001_initial_schema.py): Create all tables
2. **Seed migration** (002_seed_topics.py): Insert 8 topics
3. **Triggers migration** (003_mastery_triggers.py): Auto-calculate mastery scores

**Trigger Example** (mastery score calculation):

```sql
CREATE OR REPLACE FUNCTION update_mastery_score()
RETURNS TRIGGER AS $$
BEGIN
  NEW.mastery_score := (
    (NEW.exercise_completion_pct * 0.40) +
    (NEW.quiz_score_avg * 0.30) +
    (NEW.code_quality_avg * 0.20) +
    (NEW.consistency_score * 0.10)
  );

  NEW.mastery_level := CASE
    WHEN NEW.mastery_score >= 91 THEN 'mastered'
    WHEN NEW.mastery_score >= 71 THEN 'proficient'
    WHEN NEW.mastery_score >= 41 THEN 'learning'
    ELSE 'beginner'
  END;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_mastery_before_update
BEFORE INSERT OR UPDATE ON progress
FOR EACH ROW
EXECUTE FUNCTION update_mastery_score();
```

---

## Summary

10 entities modeled with:
- ✅ Identity strategies (numeric IDs + UUIDs where needed)
- ✅ Relationships (FKs with CASCADE where appropriate)
- ✅ Validation rules (CHECK constraints, ENUMs)
- ✅ State transitions (Progress mastery levels, ExerciseSubmission status)
- ✅ Indexes for performance (lookups, filtering, sorting)
- ✅ JSONB for flexible data (test results, quiz answers, trigger data)
- ✅ Triggers for computed fields (mastery score/level)
- ✅ Kafka events for inter-service communication (not in PostgreSQL)

Ready for API contract generation in Phase 1.
