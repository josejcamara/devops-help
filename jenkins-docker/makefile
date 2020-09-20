build:
	@docker-compose -p jenkins build
run:
	@docker-compose -p jenkins up -d jnginx jmaster jproxy
	@echo "Open your browser on: http://localhost/login"
	@echo "If this is your first run, you'd need to initialise Jenkins:"
	@echo " - Wait until you're asked for the initialAdminPassword"
	@echo " - Run: docker exec -it jenkins_jmaster_1 cat /var/jenkins_home/secrets/initialAdminPassword "
stop:
	@docker-compose -p jenkins down
clean-data: 
	@docker-compose -p jenkins down -v
clean-images:
	@docker rmi $(shell docker images -q -f "dangling=true")
master-log:
	@docker-compose -p jenkins exec jmaster tail -f /var/log/jenkins/jenkins.log
