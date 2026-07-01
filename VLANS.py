def clasificar_vlan():
    print("--- Clasificador de VLANs (escriba 'exit' para salir) ---")
    
    while True:
        entrada = input("\nIngrese el número de VLAN: ").lower()
        
        
        if entrada == 'exit':
            print("Saliendo del programa. ¡Hasta pronto!")
            break
            
        try:
            vlan = int(entrada)
            
            
            if 1 <= vlan <= 1005:
                print(f"La VLAN {vlan} corresponde al Rango Normal.")
            elif 1006 <= vlan <= 4094:
                print(f"La VLAN {vlan} corresponde al Rango Extendido.")
            else:
                print("Error: Número fuera de rango (1 - 4094).")
                
        except ValueError:
            print("Error: Entrada inválida. Por favor, ingrese un número o 'exit'.")

if __name__ == "__main__":
    clasificar_vlan()