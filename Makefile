UNAME_S := $(shell uname -s)

api_test:
	make clean
	@echo "Fetching Player Stats for $(USER)"
	time python3 backend/player_info.py get_skills "$(USER)"

run:
	docker build -t my-app:1.0 .
	docker run --name my-app -p 8080:8080 -d my-app:1.0
	@echo "Opening browser..."
	sleep 2
# ifeq ($(UNAME_S), Windows) 
# 	python -m webbrowser "http://localhost:8080/"
# endif
ifeq ($(UNAME_S), Darwin)
	open http://localhost:8080/
endif

clean:
	-docker stop my-app
	-docker rm my-app
	@if [ -f backend/skill_stats.json ]; then \
		echo "Removing existing skill_stats.json file."; \
		rm backend/skill_stats.json; \
	fi

