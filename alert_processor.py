# alert_processor.py
import pika
import json
import requests

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "sensores_mon"
WS_BRIDGE_URL = "http://localhost:9000/alert"  # endpoint del WS Server

def clasificar_alerta(evento):
    tipo = evento.get("tipo")
    valor = evento.get("valor")
    sensor_id = evento.get("sensor_id")
    timestamp = evento.get("timestamp")

    alerta = "Evento recibido"
    nivel = "verde"
    mensaje = ""

    if tipo == "temperatura":
        # Ejemplo de reglas
        if valor < 35:
            nivel = "verde"
            alerta = "Temperatura normal"
            mensaje = f"Sensor {sensor_id}: {valor}°C dentro de rango seguro."
        elif 35 <= valor <= 45:
            nivel = "amarillo"
            alerta = "Temperatura elevada"
            mensaje = f"Sensor {sensor_id}: {valor}°C supera 35°C, monitorear."
        else:  # > 45
            nivel = "rojo"
            alerta = "Temperatura crítica"
            mensaje = f"Sensor {sensor_id}: {valor}°C supera 45°C, posible sobrecalentamiento."

    elif tipo == "puerta":
        if valor == "abierta":
            nivel = "amarillo"
            alerta = "Puerta abierta"
            mensaje = f"Puerta del sensor {sensor_id} está abierta."
        else:
            nivel = "verde"
            alerta = "Puerta cerrada"
            mensaje = f"Puerta del sensor {sensor_id} cerrada."

    elif tipo == "movimiento":
        if valor == "detectado":
            nivel = "amarillo"
            alerta = "Movimiento detectado"
            mensaje = f"Movimiento detectado por sensor {sensor_id}."
        else:
            nivel = "verde"
            alerta = "Sin movimiento"
            mensaje = f"Sin movimiento en zona del sensor {sensor_id}."

    elif tipo == "humo":
        if valor < 20:
            nivel = "verde"
            alerta = "Niveles de humo normales"
            mensaje = f"Humo {valor}% en sensor {sensor_id}."
        elif 20 <= valor <= 60:
            nivel = "amarillo"
            alerta = "Niveles de humo elevados"
            mensaje = f"Humo {valor}% en sensor {sensor_id}, revisar."
        else:
            nivel = "rojo"
            alerta = "Humo crítico"
            mensaje = f"Humo {valor}% en sensor {sensor_id}, posible incendio."

    elif tipo == "vibracion":
        if valor < 3:
            nivel = "verde"
            alerta = "Vibración normal"
            mensaje = f"Vibración {valor}g en sensor {sensor_id}."
        elif 3 <= valor <= 7:
            nivel = "amarillo"
            alerta = "Vibración elevada"
            mensaje = f"Vibración {valor}g en sensor {sensor_id}, revisar estructura."
        else:
            nivel = "rojo"
            alerta = "Vibración crítica"
            mensaje = f"Vibración {valor}g en sensor {sensor_id}, posible daño estructural."

    elif tipo == "alarma_manual":
        if valor == "activada":
            nivel = "rojo"
            alerta = "Alarma manual activada"
            mensaje = f"Operador activó alarma manual en sensor {sensor_id}."
        else:
            nivel = "verde"
            alerta = "Alarma manual inactiva"
            mensaje = f"Alarma manual inactiva en sensor {sensor_id}."

    alerta_procesada = {
        "alerta": alerta,
        "nivel": nivel,
        "mensaje": mensaje,
        "sensor_id": sensor_id,
        "tipo": tipo,
        "valor": valor,
        "timestamp": timestamp
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
    print(f"[RECIBIDO MON] {evento}")
    alerta = clasificar_alerta(evento)
    print(f"[PROCESADO] {alerta}")
    enviar_a_ws(alerta)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
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
