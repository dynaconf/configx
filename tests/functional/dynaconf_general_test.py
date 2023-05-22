from textwrap import dedent

from dynaconf import Dynaconf


def create_file(filepath, data):
    with open(filepath, mode="w") as f:
        f.write(dedent(data))
    return filepath


def test_exists(tmp_path):
    """
    setting.exists() should:
        - check for keys in current environment only
    """

    filename = create_file(
        tmp_path / "settings.yaml",
        """\
        default:
          foo: default
        development:
          foo: dev
          only_dev: eggs
        prod:
          foo: prod
          only_prod: eggs
        """,
    )

    setting = Dynaconf(settings_file=str(filename), environments=True)
    # current_env=development
    assert setting.exists("only_dev")
    assert not setting.exists("only_prod")

    setting.setenv("prod")
    assert setting.exists("only_prod")
    assert not setting.exists("only_dev")


def test_exists_in_environ(tmp_path):
    """
    setting.exists_in_environ() should:
        - check for keys in current environment only
    """

    filename = create_file(
        tmp_path / "settings.yaml",
        """\
        default:
          foo: default
        development:
          foo: dev
          only_dev: eggs
        """,
    )

    setting = Dynaconf(settings_file=str(filename), environments=True)
    assert not setting.exists_in_environ("foo")
    assert setting.exists_in_environ("PYTHONPATH")
