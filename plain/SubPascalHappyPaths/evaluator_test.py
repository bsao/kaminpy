from pytest import mark, raises, fixture

from evaluator import evaluate, define_function, UserFunction
import errors


def test_evaluate_number():
    got = evaluate({}, 7)
    assert 7 == got


@mark.parametrize("ast, value", [
    (['+', 1, 2], 3),
    (['*', 6, ['+', 3, 4]], 42),
    (['/', ['*', ['-', 100, 32], 5], 9], 37)
])
def test_expression(ast, value):
    got = evaluate({}, ast)
    assert value == got


def test_evaluate_undefined_variable():
    ast = 'x'
    with raises(errors.UndefinedVariable) as excinfo:
        evaluate({}, ast)
    assert "Undefined variable: 'x'." == str(excinfo.value)


def test_set_global():
    # backup global_environment
    import evaluator
    initial_globals = evaluator.global_environment
    evaluator.global_environment = {}
    # test
    ast = ['set', 'test_set_var', ['/', 6, 2]]
    want_name = 'test_set_var'
    want_value = 3
    empty_env = {}
    got = evaluate(empty_env, ast)
    assert want_value == got
    assert len(empty_env) == 0
    assert want_name in evaluator.global_environment
    assert want_value == evaluator.global_environment[want_name]
    # restore global_environment
    evaluator.global_environment = initial_globals


@mark.parametrize("ast ,want", [
    (['if', 1, 2, 3], 2),
    (['if', 0, 2, 3], 3),
    # (if (> 1 0) 2 (/ 3 0))
    (['if', ['>', 1, 0], 2, ['/', 3, 0]], 2),
])
def test_evaluate_if(ast, want):
    got = evaluate({}, ast)
    assert want == got


def test_print(capsys):
    ast = ['print', 7]
    got = evaluate({}, ast)
    assert 7 == got
    captured = capsys.readouterr()
    assert '7\n' == captured.out


def test_begin(capsys):
    ast = ['begin',
           ['print', 1],
           ['print', 2],
           ['print', 3]
          ]
    got = evaluate({}, ast)
    assert 3 == got
    captured = capsys.readouterr()
    assert '1\n2\n3\n' == captured.out


def test_while_false(capsys):
    ast = ['while', 0, ['print', 9]]
    got = evaluate({}, ast)
    assert 0 == got
    captured = capsys.readouterr()
    assert len(captured.out) == 0


def test_while(capsys):
    # backup global_environment
    import evaluator
    initial_globals = evaluator.global_environment
    evaluator.global_environment = {}
    # test
    ast = ['begin',
           ['set', 'x', 3],
           ['while', 'x',
            ['begin',
             ['print', 'x'],
             ['set', 'x', ['-', 'x', 1]]
             ]]]
    got = evaluate({}, ast)
    assert 0 == got
    captured = capsys.readouterr()
    assert '3\n2\n1\n' == captured.out
    # restore global_environment
    evaluator.global_environment = initial_globals


def test_define_function():
    # backup function_definitions
    import evaluator
    initial_fundefs = evaluator.function_definitions
    evaluator.function_definitions = {}
    # test
    parts = ['double', ['n'], ['*', 'n', 2]]
    want_name = 'double'
    want_formals = ['n']
    want_body = ['*', 'n', 2]
    got = define_function(parts)
    assert '<UserFunction double(n)>' == got
    new_func = evaluator.function_definitions[want_name]
    assert want_name == new_func.name
    assert want_formals == new_func.formals
    assert want_body == new_func.body
    # restore function_definitions
    evaluator.function_definitions = initial_fundefs


@fixture
def mod_body():
    return ['-', 'm', ['*', 'n', ['/', 'm', 'n']]]


def test_user_function_repr(mod_body):
    func = UserFunction('mod', ['m', 'n'], mod_body)
    assert '<UserFunction mod(m, n)>' == repr(func)


def test_user_function_call(mod_body):
    func = UserFunction('mod', ['m', 'n'], mod_body)
    got = func(17, 5)
    assert 2 == got


def test_evaluate_undefined_function():
    ast = ['spam', 99]
    with raises(errors.UndefinedFunction) as excinfo:
        evaluate({}, ast)
    assert "Undefined function: 'spam'." == str(excinfo.value)


def test_apply_user_function():
    # backup function_definitions
    import evaluator
    initial_fundefs = evaluator.function_definitions
    evaluator.function_definitions = {}
    # test
    parts = 'triple', ['n'], ['*', 'n', 3]
    define_function(parts)
    ast = ['triple', 7]
    assert 21 == evaluate({}, ast)
    # restore function_definitions
    evaluator.function_definitions = initial_fundefs
