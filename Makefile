.PHONY: lab12-self-test lab13-self-test

lab12-self-test:
	@env -u OPENAI_API_KEY bash bin/lab12-self-test

lab13-self-test:
	@env -u OPENAI_API_KEY bash bin/lab13-self-test
