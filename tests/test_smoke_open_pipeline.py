from scripts.smoke_open_pipeline import main


def test_open_cpu_smoke_pipeline(capsys) -> None:
    assert main() == 0
    output = capsys.readouterr().out
    assert "Open smoke пройден" in output
    assert "samples=48" in output
    assert "provider=numpy-cpu" in output
