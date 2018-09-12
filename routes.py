from flask import Flask, render_template, request
from forms import ScraperForm
import requests, time
import codecs
from bs4 import BeautifulSoup
from slackclient import SlackClient
from celery import Celery
import urllib.request


app = Flask(__name__)

app.secret_key = "development-key"

app.config['CELERY_BROKER_URL'] = 'localhost:5000'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

def slack_message(message, channel):
    token = 'xoxp-423876483524-424250873061-423975246835-4eb6f5ac1c6a39f700031b7fce35c711'
    sc = SlackClient(token)
    sc.api_call('chat.postMessage', channel=channel,
                text=message, username='My Sweet Bot',
                icon_emoji=':robot_face:')

@celery.task
def background_task():
    old_sample = ""
    print("Background task beginning...")
        
    for i in range(10):
        print("Checking " + str(i) + " time")
        time.sleep(3)

        # Retrieves html from MIT website
        
        #page = open("maznev.html")
        #soup = BeautifulSoup(page, 'html.parser')
        
        url = "https://scripts.mit.edu/~mitoc/wall/"
        page = requests.get(url)
        soup = BeautifulSoup(page.text,'html.parser')

        # Takes either local html or MIT html and finds the staff table
        sample = soup.find('table','timeline').text

        # If substring is present in the table then that means no one is currently set to staff the wall
        # when the script grabbed the html
        substring = "no hours"

        if substring in sample and old_sample != sample:
          slack_message("No Hours posted!","general")
          print("No hours posted")
          
        elif substring not in sample and old_sample != sample:
          print("Hours posted!")
          name = soup.find('div','name').text
          print(name)
          #slack_message("Hours posted with " + name,"general")
	      
        old_sample = sample

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/about")
def about():
  return render_template("about.html")

@app.route("/scraper", methods=["GET", "POST"])
def scraper():
  form = ScraperForm()

  if request.method == "POST":
    if form.validate() == False:
      return render_template('scraper.html', form=form)
    else:

        background_task()
        
        
    return "Success!"

  elif request.method == "GET":
    return render_template('scraper.html', form=form)

if __name__ == "__main__":
  app.run(debug=True)
