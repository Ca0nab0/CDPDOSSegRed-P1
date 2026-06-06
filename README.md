[README.md](https://github.com/user-attachments/files/28658645/README.md)
# CDPDOSSegRed-P1# Ataque DoS mediante el protocolo CDP

> **Nombre:** Emmanuel Báez Ramírez
> **Matrícula:** 2022-0375
> **Video ilustrativo:** https://youtu.be/iwnL7N4eYz4
> **Playlist (Práctica 1):** https://www.youtube.com/playlist?list=PLp7pfUFf22-zekAmQ7hncCvmJHZe7lLHk

---

# Objetivo del laboratorio.
Demostrar de forma controlada un ataque de Denegación de Servicio (DoS) contra un switch Cisco abusando del protocolo CDP (Cisco Discovery Protocol), evidenciar su impacto sobre la tabla de vecinos y la CPU del equipo, e implementar y verificar la contramedida que lo mitiga.

# Objetivo del script.
Inundar al switch con anuncios CDP de dispositivos vecinos falsos. Cada paquete usa una dirección MAC de origen aleatoria y un Device-ID único, por lo que el switch registra cada uno como un vecino nuevo. Esto satura la tabla de vecinos CDP y consume CPU y memoria del equipo, degradando su funcionamiento.

# Parámetros usados.
Comando de ejecución:

    sudo python3 ./cdp_dos.py -i eth1 -n 100 -p 500

- `-i eth1` : interfaz de red del atacante (interfaz hacia el switch).
- `-n 100`  : número de dispositivos falsos por ráfaga.
- `-p 500`  : relleno del campo SoftwareVersion (amplifica el tamaño del paquete).
- `-d`      : retardo entre paquetes en segundos (opcional, por defecto 0).
- `-c`      : número de ráfagas (opcional, 0 = infinito).

Elementos internos del script:
- `load_contrib("cdp")` : carga el soporte de CDP en Scapy.
- `RandMAC()` : genera una MAC de origen aleatoria por cada paquete.
- Encapsulado `Ether / LLC / SNAP (OUI 0x00000c, code 0x2000) / CDPv2_HDR` : estructura correcta de una trama CDP.
- `CDPMsgDeviceID` : nombre de vecino falso único (SRV-VULN-...).
- `CDPMsgPlatform` : plataforma simulada (Cisco Nexus 9000).
- `Ether(raw(pkt))` : fuerza el recálculo de checksums antes de enviar.

# Requisitos para utilizar la herramienta.
- Python3
- Scapy (`sudo apt install python3-scapy`)
- Permisos root (los ataques de capa 2 requieren raw sockets).
- Estar conectado al switch víctima por LAN (puerto de acceso).

# Documentación del funcionamiento del script.
El script construye tramas CDP a mano usando el contrib oficial de Scapy. En un bucle infinito de ráfagas, por cada iteración genera `n` paquetes; cada uno lleva una MAC de origen aleatoria (`RandMAC()`) y un Device-ID único con el formato `SRV-VULN-<ráfaga>-<índice>`. Los paquetes se envían al destino multicast de CDP (`01:00:0c:cc:cc:cc`) encapsulados en LLC/SNAP. Como cada trama parece provenir de un dispositivo distinto, el switch las registra como vecinos nuevos, llenando su tabla de vecinos CDP y elevando el uso de CPU. El ataque corre hasta detenerse con Ctrl+C.

# Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso (víctima) |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.133 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.131 | Cliente / víctima |

Imágenes usadas:
- `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (switch SW1)
- `c3725-adventerprisek9-mz.124-15.T14` (router R1)

Mapa de puertos en SW1:
- Gi0/0 -> R1
- Gi0/1 -> PC1
- Gi0/2 -> Kali (atacante)

# Capturas de pantalla.
- Topología (Emmanuel Baez 20220375)



<img width="516" height="305" alt="image" src="https://github.com/user-attachments/assets/aa28611a-8d5e-4605-ad6a-06bc7fcaa4cb" />


- Ejecución del script en Kali


<img width="770" height="407" alt="cdp_ejecucion" src="https://github.com/user-attachments/assets/371e09ec-a564-4395-a1e0-e71b0de3c7cd" />


- Tabla CDP del switch saturada (cientos de vecinos falsos SRV-VULN)



<img width="683" height="327" alt="cdp_neighbors_358" src="https://github.com/user-attachments/assets/25051e75-bd07-4bbe-8dc3-5e95f6aa511e" />


<img width="737" height="408" alt="cdp_wireshark" src="https://github.com/user-attachments/assets/33284be3-67f0-4e7c-9abb-6e0ec3c83cc6" />



- Impacto en la CPU del switch

<img width="667" height="161" alt="cdp_cpu_861" src="https://github.com/user-attachments/assets/1eb8a04e-60da-4d38-88b5-8ad19cfcbe04" />

# Documentación de contra-medidas.
La mitigación es deshabilitar CDP donde no se necesita. CDP no debe estar activo en puertos de acceso hacia usuarios.

Deshabilitar CDP globalmente:

    SW1# configure terminal
    SW1(config)# no cdp run

O deshabilitarlo solo en el puerto del atacante:

    SW1(config)# interface GigabitEthernet0/2
    SW1(config-if)# no cdp enable

Verificación:

    SW1# show cdp
    SW1# show cdp neighbors

Con CDP deshabilitado, el switch deja de procesar estos paquetes: la tabla de vecinos no crece y la CPU se mantiene estable. Al relanzar el ataque ya no aparecen vecinos falsos.

Otras buenas prácticas:
- Mantener CDP solo en enlaces de infraestructura entre equipos de confianza.
- Monitorear el uso de CPU y el tamaño de la tabla de vecinos CDP.
