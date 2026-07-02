from netmiko import ConnectHandler
from datetime import datetime


router = {
    "device_type": "cisco_ios",
    "host": "192.168.56.102",
    "username": "cisco",
    "password": "cisco123!",
    "secret": "cisco123!",
    "port": 22,

    "timeout": 60,
    "global_delay_factor": 2,

    "session_log": "netmiko_session.log",
}

PROCESO_EIGRP = "REDLAB"
AS_NUMBER     = 200


INTERFAZ_GI1  = "GigabitEthernet1"
RED_IPV4_GI1  = "192.168.56.0"
WILDCARD_GI1  = "0.0.0.255"

INTERFACES_NUEVAS = {
    "Loopback2": {
        "ipv4_address": "192.168.20.1",
        "ipv4_mask":    "255.255.255.0",
        "ipv4_network": "192.168.20.0",
        "wildcard":     "0.0.0.255",
        "ipv6_address": "2001:db8:20::1/64",
    },
    "Loopback3": {
        "ipv4_address": "192.168.30.1",
        "ipv4_mask":    "255.255.255.0",
        "ipv4_network": "192.168.30.0",
        "wildcard":     "0.0.0.255",
        "ipv6_address": "2001:db8:30::1/64",
    },
}


def configurar_eigrp(conn):
    config_eigrp = [
        "ipv6 unicast-routing",
    ]


    for nombre_if, datos in INTERFACES_NUEVAS.items():
        config_eigrp += [
            f"interface {nombre_if}",
            f"ip address {datos['ipv4_address']} {datos['ipv4_mask']}",
            f"ipv6 address {datos['ipv6_address']}",
            "no shutdown",
            "exit",
        ]


    config_eigrp.append(f"router eigrp {PROCESO_EIGRP}")

    config_eigrp.append(f"address-family ipv4 unicast autonomous-system {AS_NUMBER}")
    config_eigrp.append(f"network {RED_IPV4_GI1} {WILDCARD_GI1}")
    for datos in INTERFACES_NUEVAS.values():
        config_eigrp.append(f"network {datos['ipv4_network']} {datos['wildcard']}")

    for nombre_if in [INTERFAZ_GI1, *INTERFACES_NUEVAS.keys()]:
        config_eigrp += [
            f"af-interface {nombre_if}",
            "passive-interface",
            "exit-af-interface",
        ]
    config_eigrp.append("exit-address-family")


    config_eigrp.append(f"address-family ipv6 unicast autonomous-system {AS_NUMBER}")
    for nombre_if in [INTERFAZ_GI1, *INTERFACES_NUEVAS.keys()]:
        config_eigrp += [
            f"af-interface {nombre_if}",
            "passive-interface",
            "exit-af-interface",
        ]
    config_eigrp.append("exit-address-family")

    for nombre_if in INTERFACES_NUEVAS.keys():
        config_eigrp += [
            f"interface {nombre_if}",
            f"ipv6 eigrp {AS_NUMBER}",
            "exit",
        ]


    bloques = [
        ("Habilitar IPv6 + direcciones en interfaces nuevas", config_eigrp[:1 + len(INTERFACES_NUEVAS) * 5]),
        ("Resto de la configuración EIGRP", config_eigrp[1 + len(INTERFACES_NUEVAS) * 5:]),
    ]

    for nombre_bloque, comandos in bloques:
        print(f"\n>>> Enviando bloque: {nombre_bloque}...\n")
        salida = conn.send_config_set(comandos, cmd_verify=False)
        print(salida)

    conn.save_config()  


def obtener_informacion(conn):
    comandos = {
        "EIGRP running-config":    "show running-config | section eigrp",
        "Interfaces IPv4":         "show ip interface brief",
        "Interfaces IPv6":         "show ipv6 interface brief",
        "Running config completa": "show running-config",
        "Version":                 "show version",
    }

    resultados = {}
    for nombre, cmd in comandos.items():
        salida = conn.send_command(cmd)
        resultados[nombre] = salida
        print(f"\n{'='*20} {nombre} {'='*20}\n{salida}")

    return resultados


def guardar_reporte(resultados):
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"reporte_csr1000v_{fecha}.txt"
    with open(nombre_archivo, "w") as f:
        for nombre, salida in resultados.items():
            f.write(f"\n{'='*20} {nombre} {'='*20}\n{salida}\n")
    print(f"\nReporte guardado en {nombre_archivo}")


def main():
    conn = None
    try:
        conn = ConnectHandler(**router)
        conn.enable()

        configurar_eigrp(conn)
        resultados = obtener_informacion(conn)
        guardar_reporte(resultados)

    except Exception as e:
        print(f"\n[ERROR] Ocurrió un problema durante la ejecución: {e}")

    finally:
        if conn:
            conn.disconnect()
            print("\nConexión cerrada correctamente.")


if __name__ == "__main__":
    main()