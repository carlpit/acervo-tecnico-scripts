#!/usr/bin/env python3
"""
crt_monitor.py - Monitor OSINT de certificados SSL e resolução DNS via crt.sh

Consulta logs públicos de Certificate Transparency para levantar domínios e
subdomínios que contêm um termo/marca e verifica quais possuem resolução DNS
ativa. Útil para reconhecimento passivo e para identificar domínios que usam o
nome da marca (possível phishing). Não gera variações de typosquatting; para
monitoramento contínuo, agende a execução (ex.: cron).

Desenvolvido por Carlpit (github.com/carlpit)
"""

import argparse
import json
import socket
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import quote


def buscar_certificados(termo: str, timeout: int = 25) -> list[str]:
    """Consulta a API JSON do crt.sh e retorna domínios únicos ordenados."""
    url = f"https://crt.sh/?q=%25{quote(termo)}%25&output=json"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) crt-monitor/1.1"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8", errors="replace").strip()
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"Erro HTTP {err.code} ao consultar crt.sh") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"Falha de conexão com crt.sh: {err.reason}") from err
    except TimeoutError as err:
        raise RuntimeError("Tempo limite excedido ao consultar crt.sh") from err

    if not payload:
        return []

    try:
        registros = json.loads(payload)
    except json.JSONDecodeError as err:
        raise RuntimeError("Resposta inválida (não-JSON) recebida do crt.sh") from err

    termo_lower = termo.lower()
    dominios = {
        nome.strip().lstrip("*.").rstrip(".")
        for item in registros
        for nome in item.get("name_value", "").splitlines()
        if termo_lower in nome.lower() and " " not in nome.strip()
    }
    return sorted(d for d in dominios if d)


def resolver_dns(dominio: str) -> tuple[str, str | None]:
    """Resolve o endereço IPv4 de um domínio, retornando None se não resolver."""
    try:
        ip = socket.gethostbyname(dominio)
        return dominio, ip
    except socket.gaierror:
        return dominio, None


def verificar_dominios(
    dominios: list[str], threads: int = 10
) -> list[dict[str, str | None]]:
    """Executa resolução DNS concorrente para uma lista de domínios."""
    resultados: list[dict[str, str | None]] = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futuros = {executor.submit(resolver_dns, dom): dom for dom in dominios}
        for futuro in as_completed(futuros):
            dom, ip = futuro.result()
            resultados.append({
                "domain": dom,
                "status": "active" if ip else "no_dns",
                "ip": ip,
            })
    return sorted(resultados, key=lambda item: item["domain"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor OSINT de certificados SSL e resolução DNS via crt.sh",
        epilog="Desenvolvido por Carlpit | github.com/carlpit",
    )
    parser.add_argument(
        "-t", "--target", required=True, help="Termo ou domínio alvo (ex: empresa)"
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=50, help="Limite de domínios verificados (padrão: 50)"
    )
    parser.add_argument(
        "-w", "--workers", type=int, default=10, help="Threads para resolução DNS (padrão: 10)"
    )
    parser.add_argument(
        "--only-active", action="store_true", help="Exibe apenas domínios com DNS ativo"
    )
    parser.add_argument(
        "-o", "--output", help="Salva os resultados em arquivo JSON"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    socket.setdefaulttimeout(3)

    print(f"[*] Consultando crt.sh para '{args.target}'...")
    try:
        dominios = buscar_certificados(args.target)
    except RuntimeError as err:
        print(f"[!] {err}", file=sys.stderr)
        return 1

    if not dominios:
        print("[-] Nenhum certificado encontrado para o termo informado.")
        return 0

    alvo_lista = dominios[: args.limit] if args.limit > 0 else dominios
    print(f"[+] {len(dominios)} domínios únicos encontrados. Verificando {len(alvo_lista)}...\n")

    resultados = verificar_dominios(alvo_lista, threads=args.workers)
    filtrados = [r for r in resultados if not args.only_active or r["status"] == "active"]

    for item in filtrados:
        if item["ip"]:
            print(f"[ATIVO]   {item['domain']} -> {item['ip']}")
        else:
            print(f"[SEM DNS] {item['domain']}")

    if args.output:
        relatorio = {
            "target": args.target,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_found": len(dominios),
            "checked": len(alvo_lista),
            "results": filtrados,
        }
        with open(args.output, "w", encoding="utf-8") as arq:
            json.dump(relatorio, arq, indent=2, ensure_ascii=False)
        print(f"\n[+] Relatório salvo em: {args.output}")

    print("\n---")
    print("Desenvolvido por Carlpit")
    return 0


if __name__ == "__main__":
    sys.exit(main())