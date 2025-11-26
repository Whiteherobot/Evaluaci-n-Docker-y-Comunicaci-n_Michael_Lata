import pika
import json
import random
import time
from datetime import datetime, timezone

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "sensores_mon"

def conectar_rabbit():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    return connection, connection.channel()

def generar_evento():
    audit_trail = [""]
    audit_trail = random.choice(audit_trail)
    sensor_id = f"{random.randint(100, 199)}"


    power_level = round(random.normalvariate(50, 100))


    evento = {
        "sensor_id": sensor_id,
        "power_level": power_level,
        "audit_trail": audit_trail
        
        
    }
    return evento

def main():
    conn, ch = conectar_rabbit()
    ch.queue_declare(queue=QUEUE_NAME, durable=True)

    print("[MON-Producer] Enviando valores numericos al NODO A... Ctrl+C para salir")
    try:
        while True:
            evento = generar_evento()
            body = json.dumps(evento)
            ch.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2  # mensaje persistente
                )
            )
            print(f"[ENVIADO] {body}")
            time.sleep(random.uniform(0.5, 3.0))  # intervalo aleatorio
    except KeyboardInterrupt:
        print("\n ciclo Completado")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
