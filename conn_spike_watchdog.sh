#!/usr/bin/env bash
#
# conn_spike_watchdog.sh - Monitor de tempestade de conexões e latência em Linux
#
# Acompanha picos de sockets TCP (SYN-RECV / TIME-WAIT / ESTAB) via `ss` e
# mede latência/perda de pacotes contra um alvo crítico, gerando alerta e log.
#
# Desenvolvido por Carlpit (github.com/carlpit)

set -euo pipefail

ALVO="${1:-1.1.1.1}"          # IP do gateway ou host crítico monitorado
LIMITE_SYN="${2:-50}"         # Alerta se conexões pendentes (SYN-RECV) >= limite
LIMITE_LATENCIA_MS="${3:-80}" # Alerta se latência média (ms) >= limite
INTERVALO_SEG=5
LOG_FILE="watchdog_rede.log"

log_msg() {
    local nivel="$1"
    local msg="$2"
    local ts
    ts="$(date -Iseconds)"
    printf '[%s] [%s] %s\n' "$ts" "$nivel" "$msg" | tee -a "$LOG_FILE"
}

checar_dependencias() {
    for cmd in ss ping awk; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            echo "Erro: comando obrigatório '$cmd' não encontrado." >&2
            exit 1
        fi
    done
}

main() {
    checar_dependencias
    log_msg "INFO" "Iniciando watchdog | Alvo: $ALVO | Limite SYN_RECV: $LIMITE_SYN | Latência max: ${LIMITE_LATENCIA_MS}ms"

    while true; do
        read -r estab syn_recv time_wait < <(
            ss -tan | awk '
                NR>1 {
                    if ($1 == "ESTAB") e++
                    else if ($1 == "SYN-RECV") s++
                    else if ($1 == "TIME-WAIT") t++
                }
                END { printf "%d %d %d\n", e+0, s+0, t+0 }
            '
        )

        ping_out="$(ping -c 3 -W 2 "$ALVO" 2>/dev/null || true)"
        perda="$(printf '%s\n' "$ping_out" | awk -F',' '/packet loss/ {for (i = 1; i <= NF; i++) if ($i ~ /packet loss/) {gsub(/[^0-9.]/, "", $i); print $i+0}}')"
        latencia="$(printf '%s\n' "$ping_out" | awk -F'/' '/rtt|round-trip/ {printf "%.1f", $5}')"
        perda="${perda:-100}"
        latencia="${latencia:-999.0}"

        if (( syn_recv >= LIMITE_SYN )) || (( ${perda%.*} > 0 )) || awk "BEGIN {exit !($latencia >= $LIMITE_LATENCIA_MS)}"; then
            log_msg "ALERTA" "Anomalia detectada | ESTAB=$estab SYN_RECV=$syn_recv TIME_WAIT=$time_wait | Perda=${perda}% | Latência=${latencia}ms"
        else
            log_msg "OK" "ESTAB=$estab SYN_RECV=$syn_recv TIME_WAIT=$time_wait | Perda=${perda}% | Latência=${latencia}ms"
        fi

        sleep "$INTERVALO_SEG"
    done
}

main
