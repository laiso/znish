from znish.bot import send_message

def test_e2e():
    response = send_message("どんな仕事してるの")
    assert len(response) > 0
