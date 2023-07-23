# UOPS

This is the base package for UST OPS gen2 automation. Document related to V 1.0

## Prerequisites

This module is working with Python3

## install ops_stack

```bash
pip install --extra-index-url http://54.245.3.207:8080/simple/ --trusted-host 54.245.3.207 ops_stack --user
```

## Methods and Services

#### Common Methods - common methods to application
```python
from ops_stack import CommonMethods
status, response = CommonMethods.get_files_in_directory(directory='logs', file_filter='*.log')
status, response = CommonMethods.clear_directory(directory='logs', file_filter='*.log')
```
#### App - initialize new automation job
```python
from ops_stack.services.app import App
app = App(app_config_file='sample.properties')
app.start()

# application code

app.stop()
```
#### AWS Services
> s3 service
```python
# Import module
from ops_stack.services.aws_service.s3 import S3

# Initialize s3 connection
s3_service = S3(AWS_ACCESS_KEY_ID='AWS_ACCESS_KEY_ID', AWS_SECRET_ACCESS_KEY='AWS_SECRET_ACCESS_KEY')

# Upload file to a s3 bucket
s3_service.upload_file(file_name='file_name', bucket='bucket', bucket_location='bucket_location', directory='file_location')

# Check file availability on s3 bucket
s3_service.check_file_availability(file_name='file_name', bucket='bucket', bucket_location='bucket_location')

# Download a file form s3 bucket
s3_service.download_file(file_name='file_name', bucket='bucket', bucket_location='bucket_location', directory='file_download_location')

# Create pre-signed url for a file
s3_service.create_presigned_url(file_name='file_name', bucket='bucket', bucket_location='bucket_location', expiration=3600)
```
#### Date Services
> DateTime service for US/Eastern timezone
```python
# Import module
from ops_stack.services.date_service import DateTime
from ops_stack.services.date_service.trading_calendar import TradingDays

# Get current date time on US/Eastern timezone in given time format 
DateTime.today(time_format='%Y-%m-%d %H:%M:%S.%f')

# Get epoch value of the given time in US/Eastern time
DateTime.to_epoch(time_string="2020/11/01 05:24:29.110200", time_format='%Y/%m/%d %H:%M:%S.%f')

# Get date and time of the given epoch in US/Eastern time
DateTime.from_epoch(1604226269110, time_format='%Y/%m/%d %H:%M:%S.%f')
```
> Trading days service
```python
# Import module
from ops_stack.services.date_service.trading_calendar import TradingDays

# Initialize the module
trading_calender = TradingDays(tradier_api_key='tradier_api_key')

# Get tradingdays of month
trading_calender.trading_dates_of_month(year='2020', month='11')

# Check the trading day status
trading_calender.trading_day_status(date='2020/11/01')

# Check last trading date
trading_calender.last_trading_date()

# Check next trading date
trading_calender.next_trading_date()
```
#### File Services
> Archive service
```python

```
> Csv service
```python

```
> Json service
```python

```
> Xml service
```python

```
> Yaml service
```python

```

#### Google Service
> gmail
```python

```
> google drive service
```python

```
#### JIRA service
> If you are using python 3.8, update bug is in the jira library on `.../jira/utils/__init__.py`
```python
for key, value in super(CaseInsensitiveDict, self).items():
    if key != key.lower():
        self[key.lower()] = value
        self.pop(key, None)
```
> Should be updated with
```python
for key in [x for x in super(CaseInsensitiveDict, self).keys() if x != x.lower()]:
    self[key.lower()] = self.pop(key, None)
```


