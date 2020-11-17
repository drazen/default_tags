import json
import boto3

def default_tags(event, context):
    # decode the aws config item response
    invoking_event = json.loads(event['invokingEvent'])
    config_item = invoking_event["configurationItem"]
    if config_item['resourceType'] == 'AWS::S3::Bucket':
        # tags = config_item['configuration'].get('tags')
        tags = config_item.get('tags')
        print(tags)

        # TODO - Generalize the default tagging using introspection to get default
        # tag names based on matching config rule names for that resource type
        #
        # Inspect the defined config rules that apply to the current resource type.
        # For those that do not have a TagKey defined for scope that matches the 
        # config rule name, make sure we add a default tag to the current resource 
        # config_service = boto3.client('configservice')
        # response = config_service.describe_config_rules()

        DEFAULT_TAGS = ['S3PublicReadProhibited', 'S3PublicWriteProhibited', 'S3ServerSideLoggingEnabled']
        tags_to_add = []
        for t in DEFAULT_TAGS:
            if not (t in list(tags)):
                tags_to_add.append({'Key': t, 'Value': 'true'})

        if tags_to_add:
            s3 = boto3.resource('s3')
            bucket = s3.Bucket(config_item['resourceName'])

            # Extract current tags
            try:
                tag_set = bucket.Tagging().tag_set
            except:
                # No current tags
                tag_set = []

            # Append missing default tags
            bucket.Tagging().put(Tagging={'TagSet':tag_set + tags_to_add})
            print(f'Added default tags {[tags_to_add]} for bucket {config_item["resourceName"]}')

    return {
        'statusCode': 200,
        'body': json.dumps('All Done!')
    }
