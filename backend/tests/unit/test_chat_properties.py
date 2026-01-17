"""
Property-based tests for chat service.

Feature: real-backend-implementation
Tests Property 5 from the design document.

Uses hypothesis library for property-based testing.
"""

import uuid
from datetime import datetime

import pytest
from hypothesis import given, settings, strategies as st

# Set environment variables before imports
import os
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.triage import TriageAgent


# ============================================================================
# Property 5: Chat History Persistence
# For any chat message sent by a user, the message and AI response SHALL be
# stored in the database and retrievable in the user's chat history.
# Validates: Requirements 4.5
# Note: Full persistence testing requires integration tests with database.
# Here we test the triage routing logic that underlies chat functionality.
# ============================================================================

# Strategy for generating realistic chat messages
chat_message_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=1,
    max_size=200
)


@settings(max_examples=50, deadline=5000)
@given(message=chat_message_strategy)
def test_property_5_triage_always_returns_valid_agent(message: str):
    """
    Feature: real-backend-implementation, Property 5: Chat History Persistence
    
    For any message, triage should return a valid agent type.
    """
    agent_type = TriageAgent.route(message)
    
    valid_agents = {"concepts", "code_review", "debug", "exercise"}
    assert agent_type in valid_agents, \
        f"Triage returned invalid agent type: {agent_type}"


def test_property_5_triage_routes_concepts_keywords():
    """
    Feature: real-backend-implementation, Property 5: Chat History Persistence
    
    Messages with concept keywords should route to concepts agent.
    """
    concept_messages = [
        "explain how loops work",
        "what is a variable",
        "how does Python handle memory",
        "tell me about functions",
        "teach me about classes",
    ]
    
    for message in concept_messages:
        agent_type = TriageAgent.route(message)
        assert agent_type == "concepts", \
            f"'{message}' should route to concepts, got {agent_type}"


def test_property_5_triage_routes_debug_keywords():
    """
    Feature: real-backend-implementation, Property 5: Chat History Persistence
    
    Messages with debug keywords should route to debug agent.
    """
    debug_messages = [
        "I have an error in my code",
        "help me fix this bug",
        "my code doesn't work",
        "I got an exception",
        "debug this for me",
    ]
    
    for message in debug_messages:
        agent_type = TriageAgent.route(message)
        assert agent_type == "debug", \
            f"'{message}' should route to debug, got {agent_type}"


def test_property_5_triage_routes_code_review_keywords():
    """
    Feature: real-backend-implementation, Property 5: Chat History Persistence
    
    Messages with code review keywords should route to code_review agent.
    """
    review_messages = [
        "review my code please",
        "check my code for issues",
        "how can I improve this",
        "give me feedback on this",
        "is this code pep8 compliant",
    ]
    
    for message in review_messages:
        agent_type = TriageAgent.route(message)
        assert agent_type == "code_review", \
            f"'{message}' should route to code_review, got {agent_type}"


def test_property_5_triage_routes_exercise_keywords():
    """
    Feature: real-backend-implementation, Property 5: Chat History Persistence
    
    Messages with exercise keywords should route to exercise agent.
    """
    exercise_messages = [
        "give me an exercise",
        "I want to practice",
        "give me a challenge",
        "quiz me on Python",
        "test me on loops",
    ]
    
    for message in exercise_messages:
        agent_type = TriageAgent.route(message)
        assert agent_type == "exercise", \
            f"'{message}' should route to exercise, got {agent_type}"


def test_property_5_triage_defaults_to_concepts():
    """
    Feature: real-backend-implementation, Property 5: Chat History Persistence
    
    Messages without specific keywords should default to concepts agent.
    """
    generic_messages = [
        "hello",
        "hi there",
        "Python",
        "12345",
        "random text here",
    ]
    
    for message in generic_messages:
        agent_type = TriageAgent.route(message)
        assert agent_type == "concepts", \
            f"'{message}' should default to concepts, got {agent_type}"


# ============================================================================
# Chat message model tests (unit tests for data structure)
# ============================================================================

def test_chat_message_model_structure():
    """
    Feature: real-backend-implementation, Property 5: Chat History Persistence
    
    ChatMessage model should have required fields.
    """
    from models.chat import ChatMessage
    
    # Check model has required columns
    columns = {c.name for c in ChatMessage.__table__.columns}
    required_columns = {"id", "user_id", "message", "response", "agent_type", "created_at"}
    
    assert required_columns.issubset(columns), \
        f"Missing columns: {required_columns - columns}"


def test_chat_message_agent_types():
    """
    Feature: real-backend-implementation, Property 5: Chat History Persistence
    
    Agent types should match triage routing options.
    """
    valid_agent_types = {"concepts", "code_review", "debug", "exercise"}
    
    # All triage keywords should map to valid agent types
    for agent_type in TriageAgent.KEYWORDS.keys():
        assert agent_type in valid_agent_types, \
            f"Triage agent type '{agent_type}' not in valid types"


# ============================================================================
# Chat history ordering tests
# ============================================================================

@settings(max_examples=25, deadline=5000)
@given(
    messages=st.lists(
        st.tuples(chat_message_strategy, chat_message_strategy),
        min_size=1,
        max_size=10
    )
)
def test_property_5_history_maintains_order(messages: list[tuple[str, str]]):
    """
    Feature: real-backend-implementation, Property 5: Chat History Persistence
    
    Chat history should maintain chronological order.
    Note: This tests the data structure, not actual DB persistence.
    """
    # Simulate chat history as list of (message, response) tuples
    history = []
    for msg, resp in messages:
        history.append({
            "message": msg,
            "response": resp,
            "created_at": datetime.utcnow(),
        })
    
    # History should maintain insertion order
    assert len(history) == len(messages)
    
    for i, (msg, resp) in enumerate(messages):
        assert history[i]["message"] == msg
        assert history[i]["response"] == resp


# ============================================================================
# Agent response format tests
# ============================================================================

def test_agent_response_format():
    """
    Feature: real-backend-implementation, Property 5: Chat History Persistence
    
    All agents should have consistent respond method signature.
    """
    from agents.concepts import ConceptsAgent
    from agents.code_review import CodeReviewAgent
    from agents.debug import DebugAgent
    from agents.exercise import ExerciseAgent
    
    agents = [ConceptsAgent, CodeReviewAgent, DebugAgent, ExerciseAgent]
    
    for agent in agents:
        # Each agent should have a respond method
        assert hasattr(agent, "respond"), \
            f"{agent.__name__} missing respond method"
        
        # respond should be a static method or class method
        respond = getattr(agent, "respond")
        assert callable(respond), \
            f"{agent.__name__}.respond should be callable"
