from typing import List, Tuple
from datetime import datetime
import os
import pandas as pd
from google.cloud import storage
from google.cloud import bigquery
from typing import List, Tuple

def q2_time(file_path: str) -> List[Tuple[str, int]]:

    # Se define función para obtener el cliente de BigQuery
    def get_bigquery_client():
        print('Getting BigQuery client')
        return bigquery.Client()
    
    # Se define función para ejecutar una consulta en BigQuery
    def run_bigquery_query(query: str):
        client = get_bigquery_client()
        query_job = client.query(query)
        results = query_job.result()
        return results
    
    # Se define función que permite cargar un archivo en un bucket de Google Cloud Storage
    def create_bucket_and_upload_file(project_id, bucket_name, file_path, destination_blob_name):
        # Inicializar el cliente de almacenamiento
        storage_client = storage.Client(project=project_id)
        
        # Verificar si el bucket ya existe
        bucket = storage_client.bucket(bucket_name)
        if not bucket.exists():
            # Crear un nuevo bucket con la ubicación especificada
            new_bucket = storage_client.create_bucket(bucket, location="US")
            print(f'Bucket {bucket_name} created in location US.')
        else:
            print(f'Bucket {bucket_name} already exists.')
            new_bucket = bucket
        
        # Subir el archivo al bucket
        blob = new_bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        print(f'File {file_path} uploaded to {bucket_name}/{destination_blob_name}.')

    # Se define función que crea tabla de bigquery a partir de archivo almacenado en GCS
    def load_data_from_gcs_to_bigquery(uri, table_id):
        # Inicializa el cliente de BigQuery
        client = bigquery.Client()

        job_config = bigquery.LoadJobConfig(
            schema=schema,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            max_bad_records=0,  # No permitir registros malos antes de fallar
            time_partitioning=bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="date"  # Campo de partición
            )
        )

        load_job = client.load_table_from_uri(
            uri, table_id, job_config=job_config
        )

        print(f'Starting job {load_job.job_id}')
        load_job.result()
        print(f'Job finished.')

        destination_table = client.get_table(table_id)
        print(f'Loaded {destination_table.num_rows} rows.')

    ### PARAMETROS PARA GCP
    # Configurar el proyecto
    project_id = 'project-latam-challenge'
    bucket_name = 'bucket-project-latam-challenge-q2-time'
    destination_blob_name = 'farmers-protest-tweets-2021-2-4.json'
    # Parámetros para carga de archivo en tabla de bigquery
    dataset_id = 'twitter_data'
    table_id = 'farmers_protest_tweets_2021'

    # if __name__ == "__main__":
    #     create_bucket_and_upload_file(project_id, bucket_name, file_path, destination_blob_name)




    schema = [
        bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the tweet"),
        bigquery.SchemaField(name="date", field_type="TIMESTAMP", mode="NULLABLE", description="Date and time of the tweet"),
        bigquery.SchemaField(name="content", field_type="STRING", mode="NULLABLE", description="Text content of the tweet"),
        bigquery.SchemaField(name="renderedContent", field_type="STRING", mode="NULLABLE", description="Rendered text content of the tweet"),
        bigquery.SchemaField(name="id", field_type="INTEGER", mode="REQUIRED", description="Unique identifier for the Tweet"),
        bigquery.SchemaField(name="user", field_type="RECORD", mode="NULLABLE", description="The user who posted this Tweet", fields=[
            bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the user"),
            bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the user"),
            bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="Unique identifier for the user"),
            bigquery.SchemaField(name="description", field_type="STRING", mode="NULLABLE", description="User's description"),
            bigquery.SchemaField(name="rawDescription", field_type="STRING", mode="NULLABLE", description="Raw description of the user"),
            bigquery.SchemaField(name="descriptionUrls", field_type="RECORD", mode="REPEATED", description="URLs in the user's description", fields=[
                bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL in the description"),
                bigquery.SchemaField(name="text", field_type="STRING", mode="NULLABLE", description="Text in the description"),
                bigquery.SchemaField(name="indices", field_type="INTEGER", mode="REPEATED", description="Indices in the description"),
                bigquery.SchemaField(name="tcourl", field_type="STRING", mode="NULLABLE", description="t.co URL in the description")
            ]),
            bigquery.SchemaField(name="verified", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user is verified"),
            bigquery.SchemaField(name="created", field_type="TIMESTAMP", mode="NULLABLE", description="Account creation date"),
            bigquery.SchemaField(name="followersCount", field_type="INTEGER", mode="NULLABLE", description="Number of followers"),
            bigquery.SchemaField(name="friendsCount", field_type="INTEGER", mode="NULLABLE", description="Number of friends"),
            bigquery.SchemaField(name="statusesCount", field_type="INTEGER", mode="NULLABLE", description="Number of statuses"),
            bigquery.SchemaField(name="favouritesCount", field_type="INTEGER", mode="NULLABLE", description="Number of favourites"),
            bigquery.SchemaField(name="listedCount", field_type="INTEGER", mode="NULLABLE", description="Number of times listed"),
            bigquery.SchemaField(name="mediaCount", field_type="INTEGER", mode="NULLABLE", description="Number of media uploaded"),
            bigquery.SchemaField(name="location", field_type="STRING", mode="NULLABLE", description="Location of the user"),
            bigquery.SchemaField(name="protected", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user's tweets are protected"),
            bigquery.SchemaField(name="linkUrl", field_type="STRING", mode="NULLABLE", description="User's link URL"),
            bigquery.SchemaField(name="linkTcourl", field_type="STRING", mode="NULLABLE", description="User's link t.co URL"),
            bigquery.SchemaField(name="profileImageUrl", field_type="STRING", mode="NULLABLE", description="Profile image URL"),
            bigquery.SchemaField(name="profileBannerUrl", field_type="STRING", mode="NULLABLE", description="Profile banner URL"),
            bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="User's URL")
        ]),
        bigquery.SchemaField(name="outlinks", field_type="STRING", mode="REPEATED", description="Outlinks in the tweet"),
        bigquery.SchemaField(name="tcooutlinks", field_type="STRING", mode="REPEATED", description="t.co outlinks in the tweet"),
        bigquery.SchemaField(name="replyCount", field_type="INTEGER", mode="NULLABLE", description="Number of replies"),
        bigquery.SchemaField(name="retweetCount", field_type="INTEGER", mode="NULLABLE", description="Number of retweets"),
        bigquery.SchemaField(name="likeCount", field_type="INTEGER", mode="NULLABLE", description="Number of likes"),
        bigquery.SchemaField(name="quoteCount", field_type="INTEGER", mode="NULLABLE", description="Number of quotes"),
        bigquery.SchemaField(name="conversationId", field_type="INTEGER", mode="NULLABLE", description="Conversation ID"),
        bigquery.SchemaField(name="lang", field_type="STRING", mode="NULLABLE", description="Language of the tweet"),
        bigquery.SchemaField(name="source", field_type="STRING", mode="NULLABLE", description="Source of the tweet"),
        bigquery.SchemaField(name="sourceUrl", field_type="STRING", mode="NULLABLE", description="Source URL"),
        bigquery.SchemaField(name="sourceLabel", field_type="STRING", mode="NULLABLE", description="Source label"),
        bigquery.SchemaField(name="media", field_type="RECORD", mode="REPEATED", description="Media attached to the tweet", fields=[
            bigquery.SchemaField(name="duration", field_type="FLOAT", mode="NULLABLE", description="Duration of the media"),
            bigquery.SchemaField(name="fullUrl", field_type="STRING", mode="NULLABLE", description="Full URL of the media"),
            bigquery.SchemaField(name="previewUrl", field_type="STRING", mode="NULLABLE", description="Preview URL of the media"),
            bigquery.SchemaField(name="thumbnailUrl", field_type="STRING", mode="NULLABLE", description="Thumbnail URL of the media"),
            bigquery.SchemaField(name="type", field_type="STRING", mode="NULLABLE", description="Type of media"),
            bigquery.SchemaField(name="variants", field_type="RECORD", mode="REPEATED", description="Variants of the media", fields=[
                bigquery.SchemaField(name="bitrate", field_type="INTEGER", mode="NULLABLE", description="Bitrate of the media variant"),
                bigquery.SchemaField(name="contentType", field_type="STRING", mode="NULLABLE", description="Content type of the media variant"),
                bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the media variant")
            ])
        ]),
        bigquery.SchemaField(name="retweetedTweet", field_type="RECORD", mode="NULLABLE", description="Retweeted tweet", fields=[
            bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the retweeted tweet"),
            bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the retweeted tweet"),
            bigquery.SchemaField(name="user", field_type="RECORD", mode="NULLABLE", description="User who posted the retweeted tweet", fields=[
                bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username user who posted the retweeted tweet"),
                bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name user who posted the retweeted tweet"),
                bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="Unique identifier for the user who posted the retweeted tweet"),
                bigquery.SchemaField(name="description", field_type="STRING", mode="NULLABLE", description="User's who posted the retweeted tweet description"),
                bigquery.SchemaField(name="rawDescription", field_type="STRING", mode="NULLABLE", description="Raw description user who posted the retweeted tweet"),
                bigquery.SchemaField(name="descriptionUrls", field_type="RECORD", mode="REPEATED", description="URLs in the user's description", fields=[
                    bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL in the description"),
                    bigquery.SchemaField(name="text", field_type="STRING", mode="NULLABLE", description="Text in the description"),
                    bigquery.SchemaField(name="indices", field_type="INTEGER", mode="REPEATED", description="Indices in the description"),
                    bigquery.SchemaField(name="tcourl", field_type="STRING", mode="NULLABLE", description="t.co URL in the description")
                ]),
                bigquery.SchemaField(name="verified", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user who retweeted tweet description is verified"),
                bigquery.SchemaField(name="created", field_type="TIMESTAMP", mode="NULLABLE", description="Account creation date of the user who posted the retweeted tweet"),
                bigquery.SchemaField(name="followersCount", field_type="INTEGER", mode="NULLABLE", description="Number of followers of the user who posted the retweeted tweet"),
                bigquery.SchemaField(name="friendsCount", field_type="INTEGER", mode="NULLABLE", description="Number of friends of the user who posted the retweeted tweet"),
                bigquery.SchemaField(name="statusesCount", field_type="INTEGER", mode="NULLABLE", description="Number of statuses of the user who posted the retweeted tweet"),
                bigquery.SchemaField(name="favouritesCount", field_type="INTEGER", mode="NULLABLE", description="Number of favourites of the user who posted the retweeted tweet"),
                bigquery.SchemaField(name="listedCount", field_type="INTEGER", mode="NULLABLE", description="Number of times listed of the user who posted the retweeted tweet"),
                bigquery.SchemaField(name="mediaCount", field_type="INTEGER", mode="NULLABLE", description="Number of media uploaded of the user who posted the retweeted tweet"),
                bigquery.SchemaField(name="location", field_type="STRING", mode="NULLABLE", description="Location user who posted the retweeted tweet"),
                bigquery.SchemaField(name="protected", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user's who posted the retweeted tweet tweets are protected"),
                bigquery.SchemaField(name="linkUrl", field_type="STRING", mode="NULLABLE", description="User's who posted the retweeted tweet link URL"),
                bigquery.SchemaField(name="linkTcourl", field_type="STRING", mode="NULLABLE", description="User's link t.co URL"),
                bigquery.SchemaField(name="profileImageUrl", field_type="STRING", mode="NULLABLE", description="Profile image URL"),
                bigquery.SchemaField(name="profileBannerUrl", field_type="STRING", mode="NULLABLE", description="Profile banner URL"),
                bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="User's URL")
            ]),
            bigquery.SchemaField(name="date", field_type="TIMESTAMP", mode="NULLABLE", description="Date and time of the retweeted tweet"),
            bigquery.SchemaField(name="content", field_type="STRING", mode="NULLABLE", description="Content of the retweeted tweet"),
        ]),
        bigquery.SchemaField(name="quotedTweet", field_type="RECORD", mode="NULLABLE", description="Quoted tweet", fields=[
            bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the quoted tweet"),
            bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the quoted tweet"),
            bigquery.SchemaField(name="user", field_type="RECORD", mode="NULLABLE", description="User who posted the quoted tweet", fields=[
                bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="description", field_type="STRING", mode="NULLABLE", description="Description of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="rawDescription", field_type="STRING", mode="NULLABLE", description="Raw description of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="descriptionUrls", field_type="RECORD", mode="REPEATED", description="URLs in the user's description", fields=[
                    bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL in the description"),
                    bigquery.SchemaField(name="text", field_type="STRING", mode="NULLABLE", description="Text in the description"),
                    bigquery.SchemaField(name="indices", field_type="INTEGER", mode="REPEATED", description="Indices in the description"),
                    bigquery.SchemaField(name="tcourl", field_type="STRING", mode="NULLABLE", description="t.co URL in the description")
                ]),
                bigquery.SchemaField(name="verified", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user who posted the quoted tweet is verified"),
                bigquery.SchemaField(name="created", field_type="TIMESTAMP", mode="NULLABLE", description="Account creation date of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="followersCount", field_type="INTEGER", mode="NULLABLE", description="Number of followers of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="friendsCount", field_type="INTEGER", mode="NULLABLE", description="Number of friends of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="statusesCount", field_type="INTEGER", mode="NULLABLE", description="Number of statuses of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="favouritesCount", field_type="INTEGER", mode="NULLABLE", description="Number of favourites of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="listedCount", field_type="INTEGER", mode="NULLABLE", description="Number of times listed of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="mediaCount", field_type="INTEGER", mode="NULLABLE", description="Number of media uploaded of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="location", field_type="STRING", mode="NULLABLE", description="Location of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="protected", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user's who posted the quoted tweet tweets are protected"),
                bigquery.SchemaField(name="linkUrl", field_type="STRING", mode="NULLABLE", description="User's link URL of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="linkTcourl", field_type="STRING", mode="NULLABLE", description="User's link t.co URL of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="profileImageUrl", field_type="STRING", mode="NULLABLE", description="Profile image URL of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="profileBannerUrl", field_type="STRING", mode="NULLABLE", description="Profile banner URL of the user who posted the quoted tweet"),
                bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the user who posted the quoted tweet")
            ]),
            bigquery.SchemaField(name="date", field_type="TIMESTAMP", mode="NULLABLE", description="Date and time of the quoted tweet"),
            bigquery.SchemaField(name="content", field_type="STRING", mode="NULLABLE", description="Content of the quoted tweet"),
            bigquery.SchemaField(name="renderedContent", field_type="STRING", mode="NULLABLE", description="Rendered content of the quoted tweet"),
            bigquery.SchemaField(name="conversationId", field_type="INTEGER", mode="NULLABLE", description="Conversation ID of the quoted tweet"),
            bigquery.SchemaField(name="lang", field_type="STRING", mode="NULLABLE", description="Language of the quoted tweet"),
            bigquery.SchemaField(name="likeCount", field_type="INTEGER", mode="NULLABLE", description="Number of likes of the quoted tweet"),
            bigquery.SchemaField(name="media", field_type="RECORD", mode="REPEATED", description="Media attached to the quoted tweet", fields=[
                bigquery.SchemaField(name="duration", field_type="FLOAT", mode="NULLABLE", description="Duration of the media"),
                bigquery.SchemaField(name="fullUrl", field_type="STRING", mode="NULLABLE", description="Full URL of the media"),
                bigquery.SchemaField(name="previewUrl", field_type="STRING", mode="NULLABLE", description="Preview URL of the media"),
                bigquery.SchemaField(name="thumbnailUrl", field_type="STRING", mode="NULLABLE", description="Thumbnail URL of the media"),
                bigquery.SchemaField(name="type", field_type="STRING", mode="NULLABLE", description="Type of media"),
                bigquery.SchemaField(name="variants", field_type="RECORD", mode="REPEATED", description="Variants of the media", fields=[
                    bigquery.SchemaField(name="bitrate", field_type="INTEGER", mode="NULLABLE", description="Bitrate of the media variant"),
                    bigquery.SchemaField(name="contentType", field_type="STRING", mode="NULLABLE", description="Content type of the media variant"),
                    bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the media variant")
                ])
            ]),
            bigquery.SchemaField(name="outlinks", field_type="STRING", mode="REPEATED", description="Outlinks in the quoted tweet"),
            bigquery.SchemaField(name="quoteCount", field_type="INTEGER", mode="NULLABLE", description="Number of quotes of the quoted tweet"),
            bigquery.SchemaField(name="replyCount", field_type="INTEGER", mode="NULLABLE", description="Number of replies of the quoted tweet"),
            bigquery.SchemaField(name="retweetCount", field_type="INTEGER", mode="NULLABLE", description="Number of retweets of the quoted tweet"),
            bigquery.SchemaField(name="source", field_type="STRING", mode="NULLABLE", description="Source of the quoted tweet"),
            bigquery.SchemaField(name="sourceLabel", field_type="STRING", mode="NULLABLE", description="Source label of the quoted tweet"),
            bigquery.SchemaField(name="sourceUrl", field_type="STRING", mode="NULLABLE", description="Source URL of the quoted tweet"),
            bigquery.SchemaField(name="tcooutlinks", field_type="STRING", mode="REPEATED", description="t.co outlinks in the quoted tweet"),
            bigquery.SchemaField(name="mentionedUsers", field_type="RECORD", mode="REPEATED", description="Users mentioned in the quoted tweet", fields=[
                bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the mentioned user"),
                bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the mentioned user"),
                bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the mentioned user"),
                bigquery.SchemaField(name="description", field_type="STRING", mode="NULLABLE", description="Description of the mentioned user"),
                bigquery.SchemaField(name="rawDescription", field_type="STRING", mode="NULLABLE", description="Raw description of the mentioned user"),
                bigquery.SchemaField(name="descriptionUrls", field_type="RECORD", mode="REPEATED", description="URLs in the description of the mentioned user", fields=[
                    bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL in the description"),
                    bigquery.SchemaField(name="text", field_type="STRING", mode="NULLABLE", description="Text in the description"),
                    bigquery.SchemaField(name="indices", field_type="INTEGER", mode="REPEATED", description="Indices in the description"),
                    bigquery.SchemaField(name="tcourl", field_type="STRING", mode="NULLABLE", description="t.co URL in the description")
                ]),
                bigquery.SchemaField(name="verified", field_type="BOOLEAN", mode="NULLABLE", description="Whether the mentioned user is verified"),
                bigquery.SchemaField(name="created", field_type="TIMESTAMP", mode="NULLABLE", description="Account creation date of the mentioned user"),
                bigquery.SchemaField(name="followersCount", field_type="INTEGER", mode="NULLABLE", description="Number of followers of the mentioned user"),
                bigquery.SchemaField(name="friendsCount", field_type="INTEGER", mode="NULLABLE", description="Number of friends of the mentioned user"),
                bigquery.SchemaField(name="statusesCount", field_type="INTEGER", mode="NULLABLE", description="Number of statuses of the mentioned user"),
                bigquery.SchemaField(name="favouritesCount", field_type="INTEGER", mode="NULLABLE", description="Number of favourites of the mentioned user"),
                bigquery.SchemaField(name="listedCount", field_type="INTEGER", mode="NULLABLE", description="Number of times the mentioned user is listed"),
                bigquery.SchemaField(name="mediaCount", field_type="INTEGER", mode="NULLABLE", description="Number of media uploaded by the mentioned user"),
                bigquery.SchemaField(name="location", field_type="STRING", mode="NULLABLE", description="Location of the mentioned user"),
                bigquery.SchemaField(name="protected", field_type="BOOLEAN", mode="NULLABLE", description="Whether the mentioned user's tweets are protected"),
                bigquery.SchemaField(name="linkUrl", field_type="STRING", mode="NULLABLE", description="Link URL of the mentioned user"),
                bigquery.SchemaField(name="linkTcourl", field_type="STRING", mode="NULLABLE", description="Link t.co URL of the mentioned user"),
                bigquery.SchemaField(name="profileImageUrl", field_type="STRING", mode="NULLABLE", description="Profile image URL of the mentioned user"),
                bigquery.SchemaField(name="profileBannerUrl", field_type="STRING", mode="NULLABLE", description="Profile banner URL of the mentioned user"),
                bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the mentioned user")
            ]),
            bigquery.SchemaField(name="retweetedTweet", field_type="RECORD", mode="NULLABLE", description="Retweeted tweet within the quoted tweet", fields=[
                bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the retweeted tweet within the quoted tweet"),
                bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the retweeted tweet within the quoted tweet"),
                bigquery.SchemaField(name="user", field_type="RECORD", mode="NULLABLE", description="User who posted the retweeted tweet within the quoted tweet", fields=[
                    bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the user who posted the retweeted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the user who posted the retweeted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the user who posted the retweeted tweet within the quoted tweet"),
                ]),
                bigquery.SchemaField(name="date", field_type="TIMESTAMP", mode="NULLABLE", description="Date and time of the retweeted tweet within the quoted tweet"),
                bigquery.SchemaField(name="content", field_type="STRING", mode="NULLABLE", description="Content of the retweeted tweet within the quoted tweet"),
                        ]),
            bigquery.SchemaField(name="quotedTweet", field_type="RECORD", mode="NULLABLE", description="Quoted tweet within the quoted tweet", fields=[
                bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="user", field_type="RECORD", mode="NULLABLE", description="User who posted the quoted tweet within the quoted tweet", fields=[
                    bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="description", field_type="STRING", mode="NULLABLE", description="Description of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="rawDescription", field_type="STRING", mode="NULLABLE", description="Raw description of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="descriptionUrls", field_type="RECORD", mode="REPEATED", description="URLs in the user's description", fields=[
                        bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL in the description"),
                        bigquery.SchemaField(name="text", field_type="STRING", mode="NULLABLE", description="Text in the description"),
                        bigquery.SchemaField(name="indices", field_type="INTEGER", mode="REPEATED", description="Indices in the description"),
                        bigquery.SchemaField(name="tcourl", field_type="STRING", mode="NULLABLE", description="t.co URL in the description")
                    ]),
                    bigquery.SchemaField(name="verified", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user who posted the quoted tweet within the quoted tweet is verified"),
                    bigquery.SchemaField(name="created", field_type="TIMESTAMP", mode="NULLABLE", description="Account creation date of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="followersCount", field_type="INTEGER", mode="NULLABLE", description="Number of followers of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="friendsCount", field_type="INTEGER", mode="NULLABLE", description="Number of friends of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="statusesCount", field_type="INTEGER", mode="NULLABLE", description="Number of statuses of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="favouritesCount", field_type="INTEGER", mode="NULLABLE", description="Number of favourites of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="listedCount", field_type="INTEGER", mode="NULLABLE", description="Number of times listed of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="mediaCount", field_type="INTEGER", mode="NULLABLE", description="Number of media uploaded of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="location", field_type="STRING", mode="NULLABLE", description="Location of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="protected", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user's who posted the quoted tweet within the quoted tweet tweets are protected"),
                    bigquery.SchemaField(name="linkUrl", field_type="STRING", mode="NULLABLE", description="User's link URL of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="linkTcourl", field_type="STRING", mode="NULLABLE", description="User's link t.co URL of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="profileImageUrl", field_type="STRING", mode="NULLABLE", description="Profile image URL of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="profileBannerUrl", field_type="STRING", mode="NULLABLE", description="Profile banner URL of the user who posted the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the user who posted the quoted tweet within the quoted tweet")
                ]),
                bigquery.SchemaField(name="date", field_type="TIMESTAMP", mode="NULLABLE", description="Date and time of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="content", field_type="STRING", mode="NULLABLE", description="Content of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="renderedContent", field_type="STRING", mode="NULLABLE", description="Rendered content of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="conversationId", field_type="INTEGER", mode="NULLABLE", description="Conversation ID of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="lang", field_type="STRING", mode="NULLABLE", description="Language of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="likeCount", field_type="INTEGER", mode="NULLABLE", description="Number of likes of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="media", field_type="RECORD", mode="REPEATED", description="Media attached to the quoted tweet within the quoted tweet", fields=[
                    bigquery.SchemaField(name="duration", field_type="FLOAT", mode="NULLABLE", description="Duration of the media"),
                    bigquery.SchemaField(name="fullUrl", field_type="STRING", mode="NULLABLE", description="Full URL of the media"),
                    bigquery.SchemaField(name="previewUrl", field_type="STRING", mode="NULLABLE", description="Preview URL of the media"),
                    bigquery.SchemaField(name="thumbnailUrl", field_type="STRING", mode="NULLABLE", description="Thumbnail URL of the media"),
                    bigquery.SchemaField(name="type", field_type="STRING", mode="NULLABLE", description="Type of media"),
                    bigquery.SchemaField(name="variants", field_type="RECORD", mode="REPEATED", description="Variants of the media", fields=[
                        bigquery.SchemaField(name="bitrate", field_type="INTEGER", mode="NULLABLE", description="Bitrate of the media variant"),
                        bigquery.SchemaField(name="contentType", field_type="STRING", mode="NULLABLE", description="Content type of the media variant"),
                        bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the media variant")
                    ])
                ]),
                bigquery.SchemaField(name="outlinks", field_type="STRING", mode="REPEATED", description="Outlinks in the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="quoteCount", field_type="INTEGER", mode="NULLABLE", description="Number of quotes of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="replyCount", field_type="INTEGER", mode="NULLABLE", description="Number of replies of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="retweetCount", field_type="INTEGER", mode="NULLABLE", description="Number of retweets of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="source", field_type="STRING", mode="NULLABLE", description="Source of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="sourceLabel", field_type="STRING", mode="NULLABLE", description="Source label of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="sourceUrl", field_type="STRING", mode="NULLABLE", description="Source URL of the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="tcooutlinks", field_type="STRING", mode="REPEATED", description="t.co outlinks in the quoted tweet within the quoted tweet"),
                bigquery.SchemaField(name="mentionedUsers", field_type="RECORD", mode="REPEATED", description="Users mentioned in the quoted tweet", fields=[
                    bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the mentioned user"),
                    bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the mentioned user"),
                    bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the mentioned user"),
                    bigquery.SchemaField(name="description", field_type="STRING", mode="NULLABLE", description="Description of the mentioned user"),
                    bigquery.SchemaField(name="rawDescription", field_type="STRING", mode="NULLABLE", description="Raw description of the mentioned user"),
                    bigquery.SchemaField(name="descriptionUrls", field_type="RECORD", mode="REPEATED", description="URLs in the description of the mentioned user", fields=[
                        bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL in the description"),
                        bigquery.SchemaField(name="text", field_type="STRING", mode="NULLABLE", description="Text in the description"),
                        bigquery.SchemaField(name="indices", field_type="INTEGER", mode="REPEATED", description="Indices in the description"),
                        bigquery.SchemaField(name="tcourl", field_type="STRING", mode="NULLABLE", description="t.co URL in the description")
                    ]),
                    bigquery.SchemaField(name="verified", field_type="BOOLEAN", mode="NULLABLE", description="Whether the mentioned user is verified"),
                    bigquery.SchemaField(name="created", field_type="TIMESTAMP", mode="NULLABLE", description="Account creation date of the mentioned user"),
                    bigquery.SchemaField(name="followersCount", field_type="INTEGER", mode="NULLABLE", description="Number of followers of the mentioned user"),
                    bigquery.SchemaField(name="friendsCount", field_type="INTEGER", mode="NULLABLE", description="Number of friends of the mentioned user"),
                    bigquery.SchemaField(name="statusesCount", field_type="INTEGER", mode="NULLABLE", description="Number of statuses of the mentioned user"),
                    bigquery.SchemaField(name="favouritesCount", field_type="INTEGER", mode="NULLABLE", description="Number of favourites of the mentioned user"),
                    bigquery.SchemaField(name="listedCount", field_type="INTEGER", mode="NULLABLE", description="Number of times the mentioned user is listed"),
                    bigquery.SchemaField(name="mediaCount", field_type="INTEGER", mode="NULLABLE", description="Number of media uploaded by the mentioned user"),
                    bigquery.SchemaField(name="location", field_type="STRING", mode="NULLABLE", description="Location of the mentioned user"),
                    bigquery.SchemaField(name="protected", field_type="BOOLEAN", mode="NULLABLE", description="Whether the mentioned user's tweets are protected"),
                    bigquery.SchemaField(name="linkUrl", field_type="STRING", mode="NULLABLE", description="Link URL of the mentioned user"),
                    bigquery.SchemaField(name="linkTcourl", field_type="STRING", mode="NULLABLE", description="Link t.co URL of the mentioned user"),
                    bigquery.SchemaField(name="profileImageUrl", field_type="STRING", mode="NULLABLE", description="Profile image URL of the mentioned user"),
                    bigquery.SchemaField(name="profileBannerUrl", field_type="STRING", mode="NULLABLE", description="Profile banner URL of the mentioned user"),
                    bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the mentioned user")
                ]),
                bigquery.SchemaField(name="retweetedTweet", field_type="RECORD", mode="NULLABLE", description="Retweeted tweet within the quoted tweet within the quoted tweet", fields=[
                    bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the retweeted tweet within the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the retweeted tweet within the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="user", field_type="RECORD", mode="NULLABLE", description="User who posted the retweeted tweet within the quoted tweet within the quoted tweet", fields=[
                        bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the user who posted the retweeted tweet within the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the user who posted the retweeted tweet within the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the user who posted the retweeted tweet within the quoted tweet within the quoted tweet"),
                    ]),
                    bigquery.SchemaField(name="date", field_type="TIMESTAMP", mode="NULLABLE", description="Date and time of the retweeted tweet within the quoted tweet within the quoted tweet"),
                    bigquery.SchemaField(name="content", field_type="STRING", mode="NULLABLE", description="Content of the retweeted tweet within the quoted tweet within the quoted tweet"),
                ]),            
                bigquery.SchemaField(name="quotedTweet", field_type="RECORD", mode="NULLABLE", description="Quoted tweet", fields=[
                    bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the quoted tweet"),
                    bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the quoted tweet"),
                    bigquery.SchemaField(name="user", field_type="RECORD", mode="NULLABLE", description="User who posted the quoted tweet", fields=[
                        bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="description", field_type="STRING", mode="NULLABLE", description="Description of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="rawDescription", field_type="STRING", mode="NULLABLE", description="Raw description of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="descriptionUrls", field_type="RECORD", mode="REPEATED", description="URLs in the user's description", fields=[
                            bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL in the description"),
                            bigquery.SchemaField(name="text", field_type="STRING", mode="NULLABLE", description="Text in the description"),
                            bigquery.SchemaField(name="indices", field_type="INTEGER", mode="REPEATED", description="Indices in the description"),
                            bigquery.SchemaField(name="tcourl", field_type="STRING", mode="NULLABLE", description="t.co URL in the description")
                        ]),
                        bigquery.SchemaField(name="verified", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user who posted the quoted tweet is verified"),
                        bigquery.SchemaField(name="created", field_type="TIMESTAMP", mode="NULLABLE", description="Account creation date of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="followersCount", field_type="INTEGER", mode="NULLABLE", description="Number of followers of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="friendsCount", field_type="INTEGER", mode="NULLABLE", description="Number of friends of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="statusesCount", field_type="INTEGER", mode="NULLABLE", description="Number of statuses of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="favouritesCount", field_type="INTEGER", mode="NULLABLE", description="Number of favourites of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="listedCount", field_type="INTEGER", mode="NULLABLE", description="Number of times listed of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="mediaCount", field_type="INTEGER", mode="NULLABLE", description="Number of media uploaded of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="location", field_type="STRING", mode="NULLABLE", description="Location of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="protected", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user's who posted the quoted tweet tweets are protected"),
                        bigquery.SchemaField(name="linkUrl", field_type="STRING", mode="NULLABLE", description="User's link URL of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="linkTcourl", field_type="STRING", mode="NULLABLE", description="User's link t.co URL of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="profileImageUrl", field_type="STRING", mode="NULLABLE", description="Profile image URL of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="profileBannerUrl", field_type="STRING", mode="NULLABLE", description="Profile banner URL of the user who posted the quoted tweet"),
                        bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the user who posted the quoted tweet")
                    ]),
                    bigquery.SchemaField(name="date", field_type="TIMESTAMP", mode="NULLABLE", description="Date and time of the quoted tweet"),
                    bigquery.SchemaField(name="content", field_type="STRING", mode="NULLABLE", description="Content of the quoted tweet"),
                    bigquery.SchemaField(name="renderedContent", field_type="STRING", mode="NULLABLE", description="Rendered content of the quoted tweet"),
                    bigquery.SchemaField(name="conversationId", field_type="INTEGER", mode="NULLABLE", description="Conversation ID of the quoted tweet"),
                    bigquery.SchemaField(name="lang", field_type="STRING", mode="NULLABLE", description="Language of the quoted tweet"),
                    bigquery.SchemaField(name="likeCount", field_type="INTEGER", mode="NULLABLE", description="Number of likes of the quoted tweet"),
                    bigquery.SchemaField(name="media", field_type="RECORD", mode="REPEATED", description="Media attached to the quoted tweet", fields=[
                        bigquery.SchemaField(name="duration", field_type="FLOAT", mode="NULLABLE", description="Duration of the media"),
                        bigquery.SchemaField(name="fullUrl", field_type="STRING", mode="NULLABLE", description="Full URL of the media"),
                        bigquery.SchemaField(name="previewUrl", field_type="STRING", mode="NULLABLE", description="Preview URL of the media"),
                        bigquery.SchemaField(name="thumbnailUrl", field_type="STRING", mode="NULLABLE", description="Thumbnail URL of the media"),
                        bigquery.SchemaField(name="type", field_type="STRING", mode="NULLABLE", description="Type of media"),
                        bigquery.SchemaField(name="variants", field_type="RECORD", mode="REPEATED", description="Variants of the media", fields=[
                            bigquery.SchemaField(name="bitrate", field_type="INTEGER", mode="NULLABLE", description="Bitrate of the media variant"),
                            bigquery.SchemaField(name="contentType", field_type="STRING", mode="NULLABLE", description="Content type of the media variant"),
                            bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the media variant")
                        ])
                    ]),
                    bigquery.SchemaField(name="outlinks", field_type="STRING", mode="REPEATED", description="Outlinks in the quoted tweet"),
                    bigquery.SchemaField(name="quoteCount", field_type="INTEGER", mode="NULLABLE", description="Number of quotes of the quoted tweet"),
                    bigquery.SchemaField(name="replyCount", field_type="INTEGER", mode="NULLABLE", description="Number of replies of the quoted tweet"),
                    bigquery.SchemaField(name="retweetCount", field_type="INTEGER", mode="NULLABLE", description="Number of retweets of the quoted tweet"),
                    bigquery.SchemaField(name="source", field_type="STRING", mode="NULLABLE", description="Source of the quoted tweet"),
                    bigquery.SchemaField(name="sourceLabel", field_type="STRING", mode="NULLABLE", description="Source label of the quoted tweet"),
                    bigquery.SchemaField(name="sourceUrl", field_type="STRING", mode="NULLABLE", description="Source URL of the quoted tweet"),
                    bigquery.SchemaField(name="tcooutlinks", field_type="STRING", mode="REPEATED", description="t.co outlinks in the quoted tweet"),
                    bigquery.SchemaField(name="mentionedUsers", field_type="RECORD", mode="REPEATED", description="Users mentioned in the quoted tweet", fields=[
                        bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the mentioned user"),
                        bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the mentioned user"),
                        bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the mentioned user"),
                        bigquery.SchemaField(name="description", field_type="STRING", mode="NULLABLE", description="Description of the mentioned user"),
                        bigquery.SchemaField(name="rawDescription", field_type="STRING", mode="NULLABLE", description="Raw description of the mentioned user"),
                        bigquery.SchemaField(name="descriptionUrls", field_type="RECORD", mode="REPEATED", description="URLs in the description of the mentioned user", fields=[
                            bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL in the description"),
                            bigquery.SchemaField(name="text", field_type="STRING", mode="NULLABLE", description="Text in the description"),
                            bigquery.SchemaField(name="indices", field_type="INTEGER", mode="REPEATED", description="Indices in the description"),
                            bigquery.SchemaField(name="tcourl", field_type="STRING", mode="NULLABLE", description="t.co URL in the description")
                        ]),
                        bigquery.SchemaField(name="verified", field_type="BOOLEAN", mode="NULLABLE", description="Whether the mentioned user is verified"),
                        bigquery.SchemaField(name="created", field_type="TIMESTAMP", mode="NULLABLE", description="Account creation date of the mentioned user"),
                        bigquery.SchemaField(name="followersCount", field_type="INTEGER", mode="NULLABLE", description="Number of followers of the mentioned user"),
                        bigquery.SchemaField(name="friendsCount", field_type="INTEGER", mode="NULLABLE", description="Number of friends of the mentioned user"),
                        bigquery.SchemaField(name="statusesCount", field_type="INTEGER", mode="NULLABLE", description="Number of statuses of the mentioned user"),
                        bigquery.SchemaField(name="favouritesCount", field_type="INTEGER", mode="NULLABLE", description="Number of favourites of the mentioned user"),
                        bigquery.SchemaField(name="listedCount", field_type="INTEGER", mode="NULLABLE", description="Number of times the mentioned user is listed"),
                        bigquery.SchemaField(name="mediaCount", field_type="INTEGER", mode="NULLABLE", description="Number of media uploaded by the mentioned user"),
                        bigquery.SchemaField(name="location", field_type="STRING", mode="NULLABLE", description="Location of the mentioned user"),
                        bigquery.SchemaField(name="protected", field_type="BOOLEAN", mode="NULLABLE", description="Whether the mentioned user's tweets are protected"),
                        bigquery.SchemaField(name="linkUrl", field_type="STRING", mode="NULLABLE", description="Link URL of the mentioned user"),
                        bigquery.SchemaField(name="linkTcourl", field_type="STRING", mode="NULLABLE", description="Link t.co URL of the mentioned user"),
                        bigquery.SchemaField(name="profileImageUrl", field_type="STRING", mode="NULLABLE", description="Profile image URL of the mentioned user"),
                        bigquery.SchemaField(name="profileBannerUrl", field_type="STRING", mode="NULLABLE", description="Profile banner URL of the mentioned user"),
                        bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the mentioned user")
                    ]),
                    bigquery.SchemaField(name="retweetedTweet", field_type="RECORD", mode="NULLABLE", description="Retweeted tweet within the quoted tweet", fields=[
                        bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the retweeted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the retweeted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="user", field_type="RECORD", mode="NULLABLE", description="User who posted the retweeted tweet within the quoted tweet", fields=[
                            bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the user who posted the retweeted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the user who posted the retweeted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the user who posted the retweeted tweet within the quoted tweet"),
                        ]),
                        bigquery.SchemaField(name="date", field_type="TIMESTAMP", mode="NULLABLE", description="Date and time of the retweeted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="content", field_type="STRING", mode="NULLABLE", description="Content of the retweeted tweet within the quoted tweet"),
                                ]),
                    bigquery.SchemaField(name="quotedTweet", field_type="RECORD", mode="NULLABLE", description="Quoted tweet within the quoted tweet", fields=[
                        bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="user", field_type="RECORD", mode="NULLABLE", description="User who posted the quoted tweet within the quoted tweet", fields=[
                            bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="description", field_type="STRING", mode="NULLABLE", description="Description of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="rawDescription", field_type="STRING", mode="NULLABLE", description="Raw description of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="descriptionUrls", field_type="RECORD", mode="REPEATED", description="URLs in the user's description", fields=[
                                bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL in the description"),
                                bigquery.SchemaField(name="text", field_type="STRING", mode="NULLABLE", description="Text in the description"),
                                bigquery.SchemaField(name="indices", field_type="INTEGER", mode="REPEATED", description="Indices in the description"),
                                bigquery.SchemaField(name="tcourl", field_type="STRING", mode="NULLABLE", description="t.co URL in the description")
                            ]),
                            bigquery.SchemaField(name="verified", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user who posted the quoted tweet within the quoted tweet is verified"),
                            bigquery.SchemaField(name="created", field_type="TIMESTAMP", mode="NULLABLE", description="Account creation date of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="followersCount", field_type="INTEGER", mode="NULLABLE", description="Number of followers of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="friendsCount", field_type="INTEGER", mode="NULLABLE", description="Number of friends of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="statusesCount", field_type="INTEGER", mode="NULLABLE", description="Number of statuses of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="favouritesCount", field_type="INTEGER", mode="NULLABLE", description="Number of favourites of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="listedCount", field_type="INTEGER", mode="NULLABLE", description="Number of times listed of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="mediaCount", field_type="INTEGER", mode="NULLABLE", description="Number of media uploaded of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="location", field_type="STRING", mode="NULLABLE", description="Location of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="protected", field_type="BOOLEAN", mode="NULLABLE", description="Whether the user's who posted the quoted tweet within the quoted tweet tweets are protected"),
                            bigquery.SchemaField(name="linkUrl", field_type="STRING", mode="NULLABLE", description="User's link URL of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="linkTcourl", field_type="STRING", mode="NULLABLE", description="User's link t.co URL of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="profileImageUrl", field_type="STRING", mode="NULLABLE", description="Profile image URL of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="profileBannerUrl", field_type="STRING", mode="NULLABLE", description="Profile banner URL of the user who posted the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the user who posted the quoted tweet within the quoted tweet")
                        ]),
                        bigquery.SchemaField(name="date", field_type="TIMESTAMP", mode="NULLABLE", description="Date and time of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="content", field_type="STRING", mode="NULLABLE", description="Content of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="renderedContent", field_type="STRING", mode="NULLABLE", description="Rendered content of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="conversationId", field_type="INTEGER", mode="NULLABLE", description="Conversation ID of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="lang", field_type="STRING", mode="NULLABLE", description="Language of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="likeCount", field_type="INTEGER", mode="NULLABLE", description="Number of likes of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="media", field_type="RECORD", mode="REPEATED", description="Media attached to the quoted tweet within the quoted tweet", fields=[
                            bigquery.SchemaField(name="duration", field_type="FLOAT", mode="NULLABLE", description="Duration of the media"),
                            bigquery.SchemaField(name="fullUrl", field_type="STRING", mode="NULLABLE", description="Full URL of the media"),
                            bigquery.SchemaField(name="previewUrl", field_type="STRING", mode="NULLABLE", description="Preview URL of the media"),
                            bigquery.SchemaField(name="thumbnailUrl", field_type="STRING", mode="NULLABLE", description="Thumbnail URL of the media"),
                            bigquery.SchemaField(name="type", field_type="STRING", mode="NULLABLE", description="Type of media"),
                            bigquery.SchemaField(name="variants", field_type="RECORD", mode="REPEATED", description="Variants of the media", fields=[
                                bigquery.SchemaField(name="bitrate", field_type="INTEGER", mode="NULLABLE", description="Bitrate of the media variant"),
                                bigquery.SchemaField(name="contentType", field_type="STRING", mode="NULLABLE", description="Content type of the media variant"),
                                bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the media variant")
                            ])
                        ]),
                        bigquery.SchemaField(name="outlinks", field_type="STRING", mode="REPEATED", description="Outlinks in the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="quoteCount", field_type="INTEGER", mode="NULLABLE", description="Number of quotes of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="replyCount", field_type="INTEGER", mode="NULLABLE", description="Number of replies of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="retweetCount", field_type="INTEGER", mode="NULLABLE", description="Number of retweets of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="source", field_type="STRING", mode="NULLABLE", description="Source of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="sourceLabel", field_type="STRING", mode="NULLABLE", description="Source label of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="sourceUrl", field_type="STRING", mode="NULLABLE", description="Source URL of the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="tcooutlinks", field_type="STRING", mode="REPEATED", description="t.co outlinks in the quoted tweet within the quoted tweet"),
                        bigquery.SchemaField(name="retweetedTweet", field_type="RECORD", mode="NULLABLE", description="Retweeted tweet within the quoted tweet within the quoted tweet", fields=[
                            bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the retweeted tweet within the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the retweeted tweet within the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="user", field_type="RECORD", mode="NULLABLE", description="User who posted the retweeted tweet within the quoted tweet within the quoted tweet", fields=[
                                bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the user who posted the retweeted tweet within the quoted tweet within the quoted tweet"),
                                bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the user who posted the retweeted tweet within the quoted tweet within the quoted tweet"),
                                bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the user who posted the retweeted tweet within the quoted tweet within the quoted tweet"),
                            ]),
                            bigquery.SchemaField(name="date", field_type="TIMESTAMP", mode="NULLABLE", description="Date and time of the retweeted tweet within the quoted tweet within the quoted tweet"),
                            bigquery.SchemaField(name="content", field_type="STRING", mode="NULLABLE", description="Content of the retweeted tweet within the quoted tweet within the quoted tweet"),
                        ])
                    ])
                ]),
            ])
        ]),
        bigquery.SchemaField(name="mentionedUsers", field_type="RECORD", mode="REPEATED", description="Users mentioned in the tweet", fields=[
            bigquery.SchemaField(name="username", field_type="STRING", mode="NULLABLE", description="Username of the mentioned user"),
            bigquery.SchemaField(name="displayname", field_type="STRING", mode="NULLABLE", description="Display name of the mentioned user"),
            bigquery.SchemaField(name="id", field_type="INTEGER", mode="NULLABLE", description="ID of the mentioned user"),
            bigquery.SchemaField(name="description", field_type="STRING", mode="NULLABLE", description="Description of the mentioned user"),
            bigquery.SchemaField(name="rawDescription", field_type="STRING", mode="NULLABLE", description="Raw description of the mentioned user"),
            bigquery.SchemaField(name="descriptionUrls", field_type="RECORD", mode="REPEATED", description="URLs in the description of the mentioned user", fields=[
                bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL in the description"),
                bigquery.SchemaField(name="text", field_type="STRING", mode="NULLABLE", description="Text in the description"),
                bigquery.SchemaField(name="indices", field_type="INTEGER", mode="REPEATED", description="Indices in the description"),
                bigquery.SchemaField(name="tcourl", field_type="STRING", mode="NULLABLE", description="t.co URL in the description")
            ]),
            bigquery.SchemaField(name="verified", field_type="BOOLEAN", mode="NULLABLE", description="Whether the mentioned user is verified"),
            bigquery.SchemaField(name="created", field_type="TIMESTAMP", mode="NULLABLE", description="Account creation date of the mentioned user"),
            bigquery.SchemaField(name="followersCount", field_type="INTEGER", mode="NULLABLE", description="Number of followers of the mentioned user"),
            bigquery.SchemaField(name="friendsCount", field_type="INTEGER", mode="NULLABLE", description="Number of friends of the mentioned user"),
            bigquery.SchemaField(name="statusesCount", field_type="INTEGER", mode="NULLABLE", description="Number of statuses of the mentioned user"),
            bigquery.SchemaField(name="favouritesCount", field_type="INTEGER", mode="NULLABLE", description="Number of favourites of the mentioned user"),
            bigquery.SchemaField(name="listedCount", field_type="INTEGER", mode="NULLABLE", description="Number of times the mentioned user is listed"),
            bigquery.SchemaField(name="mediaCount", field_type="INTEGER", mode="NULLABLE", description="Number of media uploaded by the mentioned user"),
            bigquery.SchemaField(name="location", field_type="STRING", mode="NULLABLE", description="Location of the mentioned user"),
            bigquery.SchemaField(name="protected", field_type="BOOLEAN", mode="NULLABLE", description="Whether the mentioned user's tweets are protected"),
            bigquery.SchemaField(name="linkUrl", field_type="STRING", mode="NULLABLE", description="Link URL of the mentioned user"),
            bigquery.SchemaField(name="linkTcourl", field_type="STRING", mode="NULLABLE", description="Link t.co URL of the mentioned user"),
            bigquery.SchemaField(name="profileImageUrl", field_type="STRING", mode="NULLABLE", description="Profile image URL of the mentioned user"),
            bigquery.SchemaField(name="profileBannerUrl", field_type="STRING", mode="NULLABLE", description="Profile banner URL of the mentioned user"),
            bigquery.SchemaField(name="url", field_type="STRING", mode="NULLABLE", description="URL of the mentioned user")
        ])
    ]



    # if __name__ == '__main__':
    #     uri = 'gs://bucket-project-latam-challenge/farmers-protest-tweets-2021-2-4.json'
    #     table_ref = f"{project_id}.{dataset_id}.{table_id}"

    #     load_data_from_gcs_to_bigquery(uri, table_ref)
    # def get_bigquery_client():
    #     return bigquery.Client()

    # def run_bigquery_query(query: str):
    #     client = get_bigquery_client()
    #     query_job = client.query(query)
    #     results = query_job.result()
    #     return results

    query = """
    WITH EmojiExtractor AS (
    -- Separa todos los caracteres de cada tweet
    SELECT
        content,
        SPLIT(content, '') AS chars
    FROM
        `project-latam-challenge.twitter_data.farmers_protest_tweets_2021`
    ), EmojiCount AS (
    -- Calcula la frecuencia de cada caracter
    SELECT char,
        COUNT(*) AS frequency
    FROM EmojiExtractor
    LEFT JOIN UNNEST(chars) AS char
    WHERE
    --LISTA DE POSIBLES EMOJIS
        char IN (
        '😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', '😋', '😎', '😍', '😘', '😗', '😙', '😚', '☺', '🙂', '🤗', '🤩', '🤔', '🤨', '😐', '😑', '😶', '🙄', '😏', '😣', '😥', '😮', '🤐', '😯', '😪', '😫', '😴', '😌', '😛', '😜', '😝', '🤤', '😒', '😓', '😔', '😕', '🙃', '🤑', '😲', '☹', '🙁', '😖', '😞', '😟', '😤', '😢', '😭', '😦', '😧', '😨', '😩', '🤯', '😬', '😰', '😱', '😳', '🤪', '😵', '😡', '😠', '🤬', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '😇', '🤠', '🤡', '🤥', '🤫', '🤭', '🧐', '🤓', '😈', '👿', '👹', '👺', '💀', '☠', '👻', '👽', '👾', '🤖', '💩', '😺', '😸', '😹', '😻', '😼', '😽', '🙀', '😿', '😾'
        )
    GROUP BY char
    )
    SELECT char AS emoji,
    frequency
    FROM EmojiCount
    ORDER BY frequency DESC
    LIMIT 10
        """
    
    results = run_bigquery_query(query)
    # Ruta a archivo de credenciales JSON de Google Cloud
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../credentials/project-latam-challenge-749ce1a96052.json"
    
    uri = 'gs://bucket-project-latam-challenge/farmers-protest-tweets-2021-2-4.json'

    # Leer el archivo CSV en un DataFrame
    df = pd.read_json(file_path,lines=True)
    
    create_bucket_and_upload_file(project_id, bucket_name, file_path, destination_blob_name)

    if __name__ == '__main__':

        # Asegurarse de que los datos se conviertan al formato correcto antes de devolverlos
        output = [(row.fecha, row.username) for row in results]
        
        # Convertir la fecha al formato datetime.date
        formatted_output = [(date(fecha.year, fecha.month, fecha.day), username) for fecha, username in output]
        
        return formatted_output


    pass