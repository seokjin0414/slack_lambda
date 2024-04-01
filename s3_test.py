import json
import os
import logging
import boto3
from urllib import request
import datetime
from typing import List

s3_client = boto3.client('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def _shortterm_api(service_name, short_term_time,  base_date, base_time):
    temp_url = f'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/{service_name}'
    api = f"{temp_url}?serviceKey={os.getenv('serviceKey')}&numOfRows=10&pageNo=1&dataType=json&base_date={base_date}&base_time={base_time + short_term_time}&nx=63&ny=126"
    logger.info(f"{service_name}'s api is {api}")
    return api

def _request_data(api):
    try:
        response = request.urlopen(api)
        # HTTPResponse 객체에서 데이터를 읽어옴
        data = response.read().decode('utf-8')
        res = json.loads(data)
        items = res['response']['body']['items']['item']
        logger.info(f"{api} done")
        return items
    except Exception as e:
        logger.error(f"Error occurred in request_data: {e}")
        return None
        
def _save_to_s3(service_name, base_datetime, data: List[dict]):
    try :
        bucket_name = 'ds-forecast'  # S3 버킷 이름 입력
        file_name = f"{service_name}-{base_datetime}.json"
        s3_key = f"shorterm/test-{file_name}"  # S3에 저장할 폴더 경로 입력
        s3_client.put_object(Body=json.dumps(data),Bucket=bucket_name,Key=s3_key)
        logger.info(f"{s3_key} file Uploaded on {bucket_name}")
    except Exception as e:
        logger.error(f"Error occurred in save_to_s3: {e}")

def lambda_handler(event, context):
    # TODO implement
    service_key = os.getenv("serviceKey")
    
    base_date = datetime.datetime.today().strftime("%Y%m%d")
    base_time = datetime.datetime.now().strftime("%H")
    base_datetime = datetime.datetime.today().strftime("%Y%m%d%H%M")
    
    short_term_service_list = ['getUltraSrtNcst', 'getUltraSrtFcst']
    short_term_time_list = ['00', '30']
    
    results = {}
    for i in range(len(short_term_time_list)):
        try:
            api = _shortterm_api(short_term_service_list[i], short_term_time_list[i], base_date, base_time)
            data = _request_data(api)
            
            if data is not None:
                _save_to_s3(short_term_service_list[i], base_datetime, data)
                results[short_term_service_list[i]] = "success"
            else:
                results[short_term_service_list[i]] = "failed"
        except Exception as e:
            results[short_term_service_list[i]] = "failed"
            logger.error(f"Error occurred in lambda_handler: {e}")
    
    return results