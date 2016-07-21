#!/usr/bin/python

import argparse
import datetime
import os
import requests
import time

import gtts
import soco
import yweather

import config


def get_weather():
    client = yweather.Client()
    woeid = client.fetch_woeid(config.WEATHER_LOCATION)
    weather = client.fetch_weather(woeid)
    return weather


def get_weather_new():
    data = {"q": 'select * from weather.forecast where woeid in (select woeid from geo.places(1) where text="%s")' % config.WEATHER_LOCATION,
            "format": "json"}
    resp = requests.post('https://query.yahooapis.com/v1/public/yql', data=data)
    jdata = resp.json()
    weather = jdata['query']['results']['channel']['item']
    return weather


def forecast_to_txt(weather, save_location):
    for day in range(2):
        f = weather['forecast'][day]
        f_date = datetime.datetime.strptime(f['date'], "%d %b %Y")
        if f_date.date() >= datetime.datetime.today().date():
            forecast_str = (
                "The forecast for %s, %s %s "
                "is %s with a high of %s and a low of %s"
                % (f_date.strftime("%A"), f_date.strftime("%B"), f_date.day,
                   f['text'], f['high'], f['low']))
            fp = open('%sforecast%d.txt' % (save_location, day), "w")
            fp.write(forecast_str)
            fp.close()

def forecast_to_mp3(weather, save_location, lang='en'):
    """
    @param weather Weather fetched from Yahoo Weather
    @type weather
    @param day Number of days ahead to get forecast (today = 0)
    @type int
    @param save_location Path to save location
    @type str
    @param lang Language to speak in
    @type str
    """
    today_idx = tomorrow_idx = 0

    for day in range(2):
        f = weather['forecast'][day]
        f_date = datetime.datetime.strptime(f['date'], "%d %b %Y")

        if f_date.date() >= datetime.datetime.today().date():
            forecast_str = (
                "The forecast for %s, %s %s "
                "is %s with a high of %s and a low of %s"
                % (f_date.strftime("%A"), f_date.strftime("%B"), f_date.day,
                   f['text'], f['high'], f['low']))
            tts = gtts.gTTS(text=forecast_str, lang=lang)
            tts.save(os.path.join(save_location, ("forecast%d.mp3" % day)))


def play_forecast(sonos_ip, play_location):
    """
    @param sonos_ip IP address of Sonos Player
    @type str
    @param play_location Location of forecast mp3s
    @type str
    """
    sonos = soco.SoCo(sonos_ip)
    # If it's after 6pm local time, play tomorrow's forecast
    day = int(datetime.datetime.now().hour > 18)
    current_track = sonos.get_current_track_info()
    sonos.play_uri(os.path.join(play_location, ("forecast%d.mp3" % day)))
#    sonos.add_uri_to_queue(os.path.join(play_location, ("forecast%d.mp3" % day)))
#    sonos.play_from_queue(sonos.queue_size-1)
    time.sleep(30)
    sonos.remove_from_queue(sonos.queue_size-1)

def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--fetch', action='store_const', const=True)
    parser.add_argument('--speak', action='store_const', const=True)
    parser.add_argument('--text', action='store_const', const=True)
    return parser.parse_args()

if (__name__ == "__main__"):
    args = parse_args()
    if args.text:
        weather = get_weather_new()
        forecast_to_txt(weather, config.FORECAST_SAVE_TXT_LOCATION)
    if args.fetch:
        weather = get_weather()
        forecast_to_mp3(weather, config.FORECAST_SAVE_MP3_LOCATION)
    if args.speak:
        play_forecast(config.SONOS_IP, config.FORECAST_PLAY_MP3_LOCATION)
