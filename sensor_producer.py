# sensor_producer.py
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
    tipos = ["temperatura", "puerta", "movimiento", "humo", "vibracion", "alarma_manual"]
    tipo = random.choice(tipos)
    sensor_id = f"S-{random.randint(100, 199)}"
    now = datetime.now(timezone.utc).isoformat()

    if tipo == "temperatura":
        valor = round(random.uniform(20, 60), 1)  # °C
    elif tipo == "puerta":
        valor = random.choice(["abierta", "cerrada"])
    elif tipo == "movimiento":
        valor = random.choice(["detectado", "no_detectado"])
    elif tipo == "humo":
        valor = round(random.uniform(0, 100), 1)  # %
    elif tipo == "vibracion":
        valor = round(random.uniform(0, 10), 2)   # g
    elif tipo == "alarma_manual":
        valor = random.choice(["activada", "inactiva"])
    else:
        valor = None

    evento = {
        "sensor_id": sensor_id,
        "tipo": tipo,
        "valor": valor,
        "timestamp": now
    }
    return evento

def main():
    conn, ch = conectar_rabbit()
    ch.queue_declare(queue=QUEUE_NAME, durable=True)

    print("[MON-Producer] Enviando eventos de sensores... Ctrl+C para salir")
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
        print("\nSaliendo productor...")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
