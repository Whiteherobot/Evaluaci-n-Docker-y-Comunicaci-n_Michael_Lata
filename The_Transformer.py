import pika
import json
import requests
import The_Initiator

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "sensores_mon"
WS_BRIDGE_URL = "http://localhost:9000/alert"  # endpoint del WS Server

def clasificar_alerta(evento):
    audit_trailxx = evento.get("audit_trail1")
    power_levelxx = evento.get("power_level1")
    sensor_idxx = evento.get("sensor_id1")



    power_levelxx = power_levelxx -5 , "Se resto 5 " 
    audit_trailxx = "B_processed"       

    alerta_procesada = {
        "sensor_idxx": sensor_idxx,
        "power_levelxx": power_levelxx,
        "audit_trailxx": audit_trailxx
    }
    return alerta_procesada

def enviar_a_ws(alerta):
    try:
        resp = requests.post(WS_BRIDGE_URL, json=alerta, timeout=2)
        if resp.status_code != 200:
            print(f"[MON-Processor] Error enviando a WS Server: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[MON-Processor] Excepción enviando a WS Server: {e}")

def callback(ch, method, properties, body):
    evento = json.loads(body.decode("utf-8"))
    alerta = clasificar_alerta(evento)
    print(f"[PROCESADO] {alerta}")
    enviar_a_ws(alerta)
    ch.basic_ack(delivery_tag=method.delivery_tag) #notifica al rabbitMQ

def main():  #configura conexion con el rabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    print("[MON-Processor] Esperando mensajes... Ctrl+C para salir")
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nSaliendo procesador...")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
