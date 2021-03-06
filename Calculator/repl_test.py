from pytest import mark

from dialogue import Dialogue, normalize

from repl import repl


def test_repl_quit(capsys):
    dlg = Dialogue('> .q\n')
    repl(dlg.fake_input)
    captured = capsys.readouterr()
    assert dlg.session == normalize(captured.out)


@mark.parametrize("session", [
    """
    >
    > .q
    """,
    """
    > 3
    3
    > .q
    """,
    """
    > 3
    3
    """,
    """
    > (* (+ 2 4) (- 10 3))
    42
    > (/ (* (- 100 32) 5) 9)
    37
    """,
])
def test_repl(capsys, session):
    dlg = Dialogue(session)
    repl(dlg.fake_input)
    captured = capsys.readouterr()
    assert dlg.session == normalize(captured.out)
