#!/usr/bin/python

import datetime
import os

import gtts
import soco
import yweather

import config


def get_weather():
    client = yweather.Client()
    woeid = client.fetch_woeid(config.WEATHER_LOCATION)
    weather = client.fetch_weather(woeid)
    return weather


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

    for day in range(3):
        f = weather['forecast'][day]
        f_date = datetime.datetime.strptime(f['date'], "%d %b %Y")

        if f_date.date() == datetime.datetime.today().date():
          today_idx = day

        forecast_str = (
            "The forecast for %s, %s %s "
            "is %s with a high of %s and a low of %s"
            % (f_date.strftime("%A"), f_date.strftime("%B"), f_date.day,
               f['text'], f['high'], f['low']))
        tts = gtts.gTTS(text=forecast_str, lang=lang)
        tts.save(os.path.join(save_location, ("forecast%d.mp3" % day)))

    return (today_idx, today_idx + 1)

def play_forecast(sonos_ip, play_location, day):
    sonos = soco.SoCo(sonos_ip)
    sonos.play_uri(os.path.join(play_location, ("forecast%d.mp3" % day)))

if (__name__ == "__main__"):
    weather = get_weather()
    (today_idx, tomorrow_idx) = forecast_to_mp3(weather, config.FORECAST_SAVE_MP3_LOCATION)
    # After 6pm, assume you want tomorrow's forecast
    if datetime.datetime.now().hour > 18:
        play_forecast(config.SONOS_IP, config.FORECAST_PLAY_MP3_LOCATION, tomorrow_idx)
    else:
        play_forecast(config.SONOS_IP, config.FORECAST_PLAY_MP3_LOCATION, today_idx)

    print today_idx
