import boto3

boto3.setup_default_session(profile_name='face')
session = boto3.Session(profile_name="face")
personalize = session.client('personalize')

if __name__ == "__main__":
    schema_name = 'YourSchemaName'

    # Define the schema for your dataset
    schema = {
        "type": "record",
        "name": "Interactions",
        "namespace": "com.amazonaws.personalize.schema",
        "fields": [
            {
                "name": "USER_ID",
                "type": "string"
            },
            {
                "name": "ITEM_ID",
                "type": "string"
            },
            {
                "name": "EVENT_VALUE",
                "type": "float"
            },
            {
                "name": "EVENT_TYPE",
                "type": "string"
            },
            {
                "name": "TIMESTAMP",
                "type": "long"
            }
        ],
        "version": "1.0"
    }

    # Create the schema for Amazon Personalize
    create_schema_response = personalize.create_schema(
        name=schema_name,
        schema=json.dumps(schema)
    )

    # To get the schema ARN, use the following lines
    schema_arn = create_schema_response['schemaArn']
    print('Schema ARN:' + schema_arn)
