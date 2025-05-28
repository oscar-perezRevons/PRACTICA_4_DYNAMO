# -- coding: utf-8 --
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

logger = logging.getLogger(_name_)
logger.setLevel(logging.INFO)

# Configuración de clientes AWS
iot_client = boto3.client('iot-data')
dynamodb = boto3.resource('dynamodb')

THING_NAME = "Panel_Objeto"  # nombre del dispositivo IoT
USERS_TABLE_NAME = "UsuariosV2"  # nombre de la tabla de usuarios

def get_user_id(handler_input):
    """Obtiene el ID de usuario de Alexa"""
    return handler_input.request_envelope.context.system.user.user_id

def check_user_access(user_id, thing_name=THING_NAME):
    """
    Verifica en DynamoDB si el usuario tiene acceso al dispositivo,
    usando la clave de partición (user_id) y la clave de ordenación (thing_name).
    """
    logger.info(f"DEBUG: check_user_access: Recibido user_id de Alexa: {user_id}")
    logger.info(f"DEBUG: check_user_access: Intentando verificar acceso para thing_name: {thing_name}")
    logger.info(f"DEBUG: check_user_access: Usando tabla DynamoDB: {USERS_TABLE_NAME}")

    try:
        table = dynamodb.Table(USERS_TABLE_NAME)
        
        # Para una clave compuesta, debes proporcionar AMBAS claves.
        key_to_send = {
            'user_id': user_id,       # Clave de partición
            'thing_name': thing_name  # Clave de ordenación
        }
        logger.info(f"DEBUG: check_user_access: Clave COMPLETA que se enviará a DynamoDB: {key_to_send}")
        
        response = table.get_item(
            Key=key_to_send
        )
        
        logger.info(f"DEBUG: check_user_access: Respuesta RAW de DynamoDB: {json.dumps(response, indent=2)}")

        if 'Item' in response:
            item = response['Item']
            logger.info(f"DEBUG: check_user_access: Item encontrado en DynamoDB: {json.dumps(item, indent=2)}")
            
            # Si el item existe con ambas claves, el acceso es concedido.
            logger.info(f"DEBUG: check_user_access: Acceso concedido para user_id '{user_id}' y thing_name '{thing_name}'.")
            return True
        else:
            logger.info(f"DEBUG: check_user_access: No se encontró ningún Item para el user_id '{user_id}' y thing_name '{thing_name}' en la tabla '{USERS_TABLE_NAME}'.")
            return False
    except Exception as e:
        logger.error(f"Error al verificar acceso de usuario: {str(e)}")
        logger.error(f"DEBUG: Tipo de excepción: {type(e)._name_}, Mensaje: {e}")
        return False

def get_shadow_state(thing_name=THING_NAME):
    """
    Obtiene el estado actual directamente del shadow del dispositivo IoT
    """
    try:
        response = iot_client.get_thing_shadow(thingName=thing_name)
        payload = json.loads(response['payload'].read())
        
        reported = payload.get('state', {}).get('reported', {})
        
        # Maneja tanto "Nublado" como "nublado" (case insensitive)
        is_cloudy = False
        for key in reported:
            if key.lower() == 'nublado':
                is_cloudy = reported[key]
                if isinstance(is_cloudy, str):
                    is_cloudy = is_cloudy.lower() == 'true'
                break
        
        return {
            "thing_name": thing_name,
            "light_level": reported.get('lightLevel', 'desconocido').lower(),
            "light_intensity": int(reported.get('intensity', 0)),
            "servo_angle": int(reported.get('angleValue', 0)),
            "last_update": reported.get('timestamp', 0),
            "is_cloudy": is_cloudy,
            "noche_mode": reported.get('Noche', 'False').lower() == 'true' # Añadido para obtener el estado de "Noche"
        }
    except Exception as e:
        logger.error(f"Error al obtener shadow: {str(e)}")
        return None

def update_shadow_noche_true(thing_name=THING_NAME):
    """
    Actualiza el shadow del dispositivo estableciendo el campo 'Noche' a True en desired
    """
    try:
        update_payload = {
            "state": {
                "desired": {
                    "Noche": True
                }
            }
        }
        response = iot_client.update_thing_shadow(
            thingName=thing_name,
            payload=json.dumps(update_payload).encode('utf-8')
        )
        logger.info(f"Shadow actualizado con Noche=True para {thing_name}")
        return True
    except Exception as e:
        logger.error(f"Error actualizando shadow: {str(e)}")
        return False

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler para cuando se lanza la skill sin intent específico"""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        user_id = get_user_id(handler_input)
        if not check_user_access(user_id):
            speak_output = "No tienes permiso para acceder a este dispositivo."
            return handler_input.response_builder.speak(speak_output).response
            
        speak_output = (
            "Bienvenido al sistema de control de tu panel solar inteligente. "
            "Puedes preguntarme por el estado actual, el nivel de luz o si está en modo nublado. "
            "¿Qué te gustaría saber?"
        )
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class EstadoPanelIntentHandler(AbstractRequestHandler):
    """Handler para consultar el estado del panel solar"""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("EstadoPanelIntent")(handler_input)

    def handle(self, handler_input):
        user_id = get_user_id(handler_input)
        if not check_user_access(user_id):
            speak_output = "No tienes permiso para acceder a este dispositivo."
            return handler_input.response_builder.speak(speak_output).response
        
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
            noche_modo = panel_state["noche_mode"] # Obtener el estado de Noche
            
            timestamp = panel_state["last_update"]
            if timestamp:
                try:
                    last_update = datetime.fromtimestamp(int(timestamp)/1000).strftime('%H:%M')
                except:
                    last_update = "desconocida"
            else:
                last_update = "desconocida"
            
            # Ajustar la respuesta para incluir el modo noche si es relevante
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
                if estado_luz == "alto":
                    estado_desc = "excelente"
                elif estado_luz == "medio":
                    estado_desc = "moderada"
                else: # asume 'bajo' o 'desconocido'
                    estado_desc = "baja"
                
                speak_output = (
                    f"Estado actual del panel solar:\n"
                    f"- Nivel de luz: {estado_desc}\n"
                    f"- Intensidad: {intensidad} unidades\n"
                    f"- Ángulo: {angulo} grados\n"
                    f"- Última actualización: {last_update}"
                )

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("¿Deseas consultar otra información?")
                .response
        )

class ModoNubladoIntentHandler(AbstractRequestHandler):
    """Handler específico para consultar el estado 'Nublado' del panel solar"""
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ModoNubladoIntent")(handler_input)

    def handle(self, handler_input):
        user_id = get_user_id(handler_input)

        # Validación de acceso del usuario
        if not check_user_access(user_id):
            speak_output = "No tienes permiso para acceder a este dispositivo."
            return handler_input.response_builder.speak(speak_output).response

        # Obtener el estado actual del shadow (solo 'reported')
        panel_state = get_shadow_state()

        if not panel_state or "state" not in panel_state or "reported" not in panel_state["state"]:
            speak_output = "No pude verificar el estado del panel en este momento."
            return handler_input.response_builder.speak(speak_output).response

        reported = panel_state["state"]["reported"]

        # Extraer valor del campo 'Nublado'
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


class HelpIntentHandler(AbstractRequestHandler):
    """Handler para ayuda"""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = (
            "Puedes preguntarme por: "
            "- El estado actual del panel solar, "
            "- Si está en modo nublado, "
            "- El nivel de luz actual, "
            "- O la posición del panel. "
            "¿Qué información necesitas?"
        )
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler para cancelar o detener"""
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
    """Handler para fin de sesión"""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Handler para excepciones"""
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
    
    # Esta parte maneja las invocaciones de Lambda que vienen de IoT Core (por ejemplo, para actualizar un shadow).
    # Se espera que el evento de IoT Core contenga 'thingName' para identificar el dispositivo.
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
    # Si no es una invocación de IoT, se asume que es una solicitud de Alexa Skill
    # y se la pasa al manejador del skill.
    else:
        logger.info(f"Invocación desde Alexa Skill.")
        return sb.lambda_handler()(event, context)

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(EstadoPanelIntentHandler())
sb.add_request_handler(ModoNubladoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())