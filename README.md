## AWS Signature Version 4
Signature Version 4 is the process to add authentication information to AWS requests sent by HTTP. By using this libary 
you can use AWS services. more detail visit on [AWS](https://docs.amazonaws.cn/en_us/general/latest/gr/signature-version-4.html)

##### Feature List

| Name                                 | status     
| ---                                  | ---        
| AWS IoT Core                         | `done`       
| AWS EC2                              | `Comming`    



## Example 
```python
"""
IoT Core Example 
"""
import datetime
from AWSSignV4.client import Client

endpoint="https://your_aws_iot_endpoint"

client = Client(
    aws_region="<AWS region>",
    aws_service="iotdevicegateway",
    aws_access_key="<your aws access key>",
    aws_secret_key="<your aws secret key>",
    date_time=datetime.datetime.now().utcnow()
)

client.build_canonical(canonical_uri="/topics/<your IoT topic name>", canonical_querystring="qos=1")
response = client.post(url=endpoint, data={"hello": "IoT Core"})
# If everthing is fine you will get success message like bellow
# {"message":"OK","traceId":"137a8fd1-78ae-af36-bd47-ae70e1e691e7"}
# or you can also subscript your topic name on AWS IoT core test client feature. 
print(response.text)
```
To learn more [Documentation](./docs/GUIDE.md).

## Changelog
See [Changelog](CHANGELOG.md)

## License
MIT