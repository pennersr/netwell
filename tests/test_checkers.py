import pytest

from netwell.checkers import Outcome, RuleFailedException


def test_outcome():
    outcome = Outcome()
    with pytest.raises(RuleFailedException):
        outcome.fail('foobar')
    assert outcome.message == 'foobar'
    assert outcome.failed
