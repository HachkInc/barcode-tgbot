FROM python:latest
RUN pip3 install pyTelegramBotAPI python-dotenv
COPY . .
RUN chmod +x userDataHandlers.py
CMD [ "python", "main.py" ]
