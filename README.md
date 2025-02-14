# 30github 30-day challenge 

for Authoriting needs: pip install flask flask-bcrypt flask-login flask-sqlalchemy
after fully setting try to run: python app.py

----------------------------------------------------------
for the telegram bot, the structure will look like this: 

📂 MyTelegramBot/
 ├── 📂 src/main/java/com/example/bot/
 │    ├── 📄 Main.java                 # Entry point
 │    ├── 📄 BotConfig.java            # Token and config
 │    ├── 📄 MyTelegramBot.java        # Core bot logic
 │    ├── 📄 Handlers/
 │    │    ├── 📄 StartHandler.java    # Handles /start
 │    │    ├── 📄 OtherMessages.java   # Handles other messages
 │    │    ├── 📄 SurveyHandler.java   # Handles surveys
 │    │    ├── 📄 ReviewHandler.java   # Handles reviews
 │    ├── 📄 Database.java             # Database interaction
 ├── 📄 pom.xml                         # Maven dependencies

and installations for :
first don't forget you have downloaded java: java -version > It should be up to the 2023-10-07 update package 

Maven: mvn -version > Apache Maven 3.8.6 > should be downloaded maven >

Install Dependencies: mvn clean install but before pom.xml should be added 

BotConfig.java needs to be set up for the telegram bot token: ---> 

public class BotConfig {
    public static final String BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN";
}
to run ---> 
mvn package
java -jar target/MyTelegramBot.jar










