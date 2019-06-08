.PHONY = manual  update clean

export AWS_DEFAULT_REGION = us-east-1

manual :
	./gossip.py vgk751ho2ub1neprv3kihr03och7bjh915gf5j01


update : gossip.zip
	aws lambda update-function-code --function-name gossip_lambda \
	                                --zip-file fileb://./$<


%/ :
	pip3 install --system $* -t .

gossip.zip : gossip.py bs4/ soupsieve/ requests/ certifi/ chardet/ idna/ urllib3/
	zip -r $@ $?

clean :
	rm -rf */ gossip.zip
