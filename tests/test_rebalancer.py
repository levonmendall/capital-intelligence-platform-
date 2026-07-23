from intelligence.rebalancer import calculate_rebalance


def test_rebalancer_returns_actions():

    actions = calculate_rebalance("PRES")

    assert len(actions) > 0


def test_actions_have_valid_type():

    actions = calculate_rebalance("PRES")

    valid = {
        "BUY",
        "SELL",
        "HOLD",
    }

    for action in actions:

        assert action.action in valid
