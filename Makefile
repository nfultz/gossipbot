.PHONY = manual  update clean

export AWS_DEFAULT_REGION = us-east-1

manual :
	SLACK_WEBHOOK=$(<.slack_webhook) ./gossip.py socaltech.email


update : gossip.zip
	aws lambda update-function-code --function-name gossip_lambda \
	                                --zip-file fileb://./$<


%/ :
	pip3 install --system $* -t .

gossip.zip : gossip.py bs4/ soupsieve/ requests/ certifi/ chardet/ idna/ urllib3/
	zip -r $@ $?

clean :
	rm -rf */ gossip.zip
