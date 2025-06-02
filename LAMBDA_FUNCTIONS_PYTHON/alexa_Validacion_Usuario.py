# -*- coding: utf-8 -*-
import logging
import ask_sdk_core.utils as ask_utils
import boto3
import json
from datetime import datetime
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

iot_client = boto3.client('iot-data')
dynamodb = boto3.resource('dynamodb')

THING_NAME = "Panel_Objeto"  # nombre del dispositivo IoT
USERS_TABLE_NAME = "UsuariosV2"  # nombre de la tabla de usuarios

def get_user_id(handler_input):
    return handler_input.request_envelope.context.system.user.user_id

def check_user_access(user_id, thing_name=THING_NAME):
    try:
        table = dynamodb.Table(USERS_TABLE_NAME)
        key_to_send = {'user_id': user_id, 'thing_name': thing_name}
        response = table.get_item(Key=key_to_send)
        return 'Item' in response
    except Exception as e:
        logger.error(f"Error al verificar acceso de usuario: {str(e)}")
        return False

def get_shadow_state(thing_name=THING_NAME):
    try:
        response = iot_client.get_thing_shadow(thingName=thing_name)
        payload = json.loads(response['payload'].read())
        reported = payload.get('state', {}).get('reported', {})

        is_cloudy = False
        for key in reported:
            if isinstance(key, str) and key.lower() == 'nublado':
                is_cloudy = reported[key]
                if isinstance(is_cloudy, str):
                    is_cloudy = is_cloudy.lower() == 'true'
                break

        return {
            "thing_name": thing_name,
            "light_level": str(reported.get('lightLevel', 'desconocido')).lower(),
            "light_intensity": int(reported.get('intensity', 0)),
            "servo_angle": int(reported.get('angleValue', 0)),
            "last_update": reported.get('timestamp', 0),
            "is_cloudy": is_cloudy,
            "noche_mode": str(reported.get('Noche', 'False')).lower() == 'true',
            "reported": reported
        }
    except Exception as e:
        logger.error(f"Error al obtener shadow: {str(e)}")
        return None

def update_shadow_noche_true(thing_name=THING_NAME):
    try:
        update_payload = {"state": {"reported": {"Noche": True}}}
        iot_client.update_thing_shadow(
            thingName=thing_name,
            payload=json.dumps(update_payload).encode('utf-8')
        )
        return True
    except Exception as e:
        logger.error(f"Error actualizando shadow: {str(e)}")
        return False

def handle_iot_rule_event(event):
    reported = None
    if "state" in event and "reported" in event["state"]:
        reported = event["state"]["reported"]
    elif "detail" in event and "state" in event["detail"] and "reported" in event["detail"]["state"]:
        reported = event["detail"]["state"]["reported"]

    if not reported:
        return False

    light_level = str(reported.get("lightLevel", "")).lower()
    if light_level == "bajo":
        return update_shadow_noche_true()
    return False

def update_shadow_recalibracion_true(thing_name=THING_NAME):
    try:
        update_payload = {"state": {"reported": {"recalibracion": True}}}
        iot_client.update_thing_shadow(
            thingName=thing_name,
            payload=json.dumps(update_payload).encode('utf-8')
        )
        return True
    except Exception as e:
        logger.error(f"Error actualizando shadow para recalibración: {str(e)}")
        return False

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        user_id = get_user_id(handler_input)
        if not check_user_access(user_id):
            return handler_input.response_builder.speak("No tienes permiso para acceder a este dispositivo.").response

        speak_output = (
            "Bienvenido al sistema de control de tu panel solar inteligente. "
            "Puedes preguntarme por el estado actual, el nivel de luz o si está en modo nublado. "
            "¿Qué te gustaría saber?"
        )
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class EstadoPanelIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("EstadoPanelIntent")(handler_input)

    def handle(self, handler_input):
        user_id = get_user_id(handler_input)
        if not check_user_access(user_id):
            return handler_input.response_builder.speak("No tienes permiso para acceder a este dispositivo.").response

        panel_state = get_shadow_state()

        if panel_state is None:
            speak_output = (
                "No pude conectar con el panel solar en este momento. "
                "Por favor, verifica que el dispositivo esté encendido y conectado."
            )
        else:
            estado_luz = panel_state["light_level"]
            intensidad = panel_state["light_intensity"]
            angulo = panel_state["servo_angle"]
            nublado = panel_state["is_cloudy"]
            noche_modo = panel_state["noche_mode"]
            timestamp = panel_state["last_update"]
            try:
                last_update = datetime.fromtimestamp(int(timestamp)/1000).strftime('%H:%M') if timestamp else "desconocida"
            except:
                last_update = "desconocida"

            if noche_modo:
                speak_output = (
                    f"El panel solar está en modo noche. "
                    f"La última actualización fue a las {last_update}. "
                    f"Posición actual: {angulo} grados. "
                    f"Intensidad de luz detectada: {intensidad} unidades."
                )
            elif nublado:
                speak_output = (
                    f"El panel solar está operando en modo nublado. "
                    f"La última actualización fue a las {last_update}. "
                    f"Posición actual: {angulo} grados. "
                    f"Intensidad de luz detectada: {intensidad} unidades."
                )
            else:
                estado_desc = "excelente" if estado_luz == "alto" else "moderada" if estado_luz == "medio" else "baja"
                speak_output = (
                    f"Estado actual del panel solar:\n"
                    f"- Nivel de luz: {estado_desc}\n"
                    f"- Intensidad: {intensidad} unidades\n"
                    f"- Ángulo: {angulo} grados\n"
                    f"- Última actualización: {last_update}"
                )

        return handler_input.response_builder.speak(speak_output).ask("¿Deseas consultar otra información?").response

class ModoNubladoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ModoNubladoIntent")(handler_input)

    def handle(self, handler_input):
        user_id = get_user_id(handler_input)
        if not check_user_access(user_id):
            speak_output = "No tienes permiso para acceder a este dispositivo."
            return handler_input.response_builder.speak(speak_output).response

        panel_state = get_shadow_state()

        if not panel_state or "reported" not in panel_state:
            speak_output = "No pude verificar el estado del panel en este momento."
            return handler_input.response_builder.speak(speak_output).response

        reported = panel_state["reported"]
        nublado = reported.get("Nublado")

        if nublado is True:
            speak_output = (
                "Sí, el panel solar está en modo nublado. "
                "Esto significa que no se ha detectado suficiente luz solar."
            )
        elif nublado is False:
            speak_output = "No, el panel solar no está en modo nublado."
        else:
            speak_output = "El estado de nublado no está disponible actualmente."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("¿Te gustaría saber algo más?")
                .response
        )

class RecalibrarPanelIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("RecalibrarPanelIntent")(handler_input)

    def handle(self, handler_input):
        user_id = get_user_id(handler_input)
        if not check_user_access(user_id):
            speak_output = "No tienes permiso para recalibrar este dispositivo."
            return handler_input.response_builder.speak(speak_output).response

        success = update_shadow_recalibracion_true()
        if success:
            speak_output = (
                "He solicitado la recalibración del panel solar. "
                "Por favor, espera unos momentos mientras el sistema ejecuta el proceso."
            )
        else:
            speak_output = (
                "No pude solicitar la recalibración en este momento. "
                "Por favor, intenta de nuevo más tarde."
            )
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = (
            "Puedes preguntarme por: "
            "- El estado actual del panel solar, "
            "- Si está en modo nublado, "
            "- El nivel de luz actual, "
            "- O la posición del panel. "
            "También puedes solicitar una recalibración diciendo: recalibra el panel. "
            "¿Qué información necesitas?"
        )
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Gracias por usar el sistema de panel solar. ¡Hasta pronto!"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speak_output = "Lo siento, hubo un problema al procesar tu solicitud. Por favor, inténtalo de nuevo."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

def lambda_handler(event, context):
    logger.info(f"Evento recibido: {json.dumps(event)}")
    
    if ("state" in event and "reported" in event["state"] and
        "lightLevel" in event["state"]["reported"]):
        logger.info("Ejecución Lambda desde regla IoT por lightLevel.")
        result = handle_iot_rule_event(event)
        if result:
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Shadow actualizado con Noche=True por regla IoT"})
            }
        else:
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Regla IoT: No se requirió actualización del shadow"})
            }
        
    if 'thingName' in event:
        thing = event['thingName']
        logger.info(f"Invocación desde IoT Core para {thing}. Actualizando 'Noche' a True...")
        success = update_shadow_noche_true(thing_name=thing)
        if success:
            return {
                "statusCode": 200,
                "body": json.dumps({"message": f"Shadow de {thing} actualizado con Noche=True"})
            }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Error actualizando shadow"})
            }
    else:
        logger.info(f"Invocación desde Alexa Skill.")
        return sb.lambda_handler()(event, context)

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(EstadoPanelIntentHandler())
sb.add_request_handler(ModoNubladoIntentHandler())
sb.add_request_handler(RecalibrarPanelIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())