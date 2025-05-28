import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # El objeto 'context' de la Lambda contiene información del entorno de ejecución
        aws_account_id = context.invoked_function_arn.split(":")[4]
        logger.info(f"El ID de la cuenta de AWS de esta Lambda es: {aws_account_id}")

        # También puedes obtener el ARN del rol de ejecución de la Lambda
        execution_role_arn = context.invoked_function_arn.split(":")[5] # Este es el rol o usuario que invoca la función
        logger.info(f"El ARN del rol de ejecución de esta Lambda es: {execution_role_arn}")

        # Si quieres el ARN de la función Lambda misma:
        lambda_arn = context.invoked_function_arn
        logger.info(f"El ARN de la función Lambda es: {lambda_arn}")

        return {
            'statusCode': 200,
            'body': json.dumps(f"ID de cuenta de AWS: {aws_account_id}")
        }
    except Exception as e:
        logger.error(f"Error al obtener el ID de la cuenta de AWS: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps("Error interno")
        }