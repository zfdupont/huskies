cd server
touch log
mvn wrapper:wrapper
./mvnw spring-boot:run &> log &
cd ../static/app
if [ -z "$(ls -A /path/to/dir)" ]; then
	git clone https://github.com/zfdupont/huskies-client.git .
fi
npm install --force
npm run build
serve -s build
