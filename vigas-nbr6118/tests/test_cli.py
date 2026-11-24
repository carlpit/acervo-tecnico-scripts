import json

from typer.testing import CliRunner

from vigas_nbr6118.cli import app

runner = CliRunner()
BASE = ["dimensionar", "--b", "20", "--h", "50", "--d", "45", "--fck", "25", "--mk", "100"]


def test_cli_texto():
    r = runner.invoke(app, BASE)
    assert r.exit_code == 0, r.output
    assert "8.23" in r.output
    assert "domínio 3" in r.output


def test_cli_json():
    r = runner.invoke(app, [*BASE, "--json"])
    assert r.exit_code == 0, r.output
    dados = json.loads(r.stdout)
    assert round(dados["as_tracao"], 2) == 8.23
    assert dados["entrada"]["aco"] == "CA-50"


def test_cli_memorial(tmp_path):
    arq = tmp_path / "v1.md"
    r = runner.invoke(app, [*BASE, "--memorial", str(arq), "--titulo", "V1"])
    assert r.exit_code == 0, r.output
    txt = arq.read_text(encoding="utf-8")
    assert "# Memorial de cálculo — V1" in txt
    assert "8,23 cm²" in txt
    assert "ART" in txt


def test_cli_d_padrao():
    r = runner.invoke(app, ["dimensionar", "--b", "20", "--h", "50", "--fck", "25", "--mk", "100"])
    assert r.exit_code == 0
    assert "d = h − 5 = 45" in r.output


def test_cli_erro_entrada():
    r = runner.invoke(app, ["dimensionar", "--b", "20", "--h", "50", "--fck", "60", "--mk", "100"])
    assert r.exit_code == 1


def test_cli_secao_insuficiente_exit_2():
    r = runner.invoke(
        app, ["dimensionar", "--b", "12", "--h", "30", "--fck", "20", "--mk", "200"]
    )
    assert r.exit_code == 2


def test_cli_versao():
    r = runner.invoke(app, ["--versao"])
    assert r.exit_code == 0
    assert "0.1.0" in r.output
