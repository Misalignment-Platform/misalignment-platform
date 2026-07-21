import pytest

from backend.src.domain.events import Event
from backend.src.domain.interventions import Intervention


def test_event_state_transition_validation() -> None:
    event = Event(system_id="sys-1", source="monitor", content="ok")
    event.transition_state("in-progress")
    assert event.state == "in-progress"

    event.transition_state("resolved")
    assert event.state == "resolved"

    with pytest.raises(ValueError):
        event.transition_state("open")


def test_intervention_transition_lifecycle() -> None:
    intervention = Intervention(
        system_id="sys-1",
        event_id="evt-1",
        evaluation_id="eval-1",
        action="review",
    )
    intervention.start()
    assert intervention.state == "in-progress"

    intervention.resolve()
    assert intervention.state == "resolved"
