import gtts
import soco
import yweather

import config

days = {'Sun': 'Sunday',
        'Mon': 'Monday',
        'Tues': 'Tuesday',
        'Wed': 'Wednesday',
        'Thurs': 'Thursday',
        'Fri': 'Friday',
        'Sat': 'Saturday'}

client = yweather.Client()
woeid = client.fetch_woeid(config.WEATHER_LOCATION)
weather = client.fetch_weather(woeid)
# Get today's forecast
tf = weather['forecast'][0]
forecast_str = "It is %s. Today's forecast is a high of %s, a low of %s, and %s" % (days[tf['day']], tf['high'], tf['low'], tf['text'])
tts = gtts.gTTS(text=forecast_str, lang='en')
tts.save(config.FORECAST_SAVE_MP3_LOCATION + "forecast.mp3")
sonos = soco.SoCo(config.SONOS_IP)
sonos.play_uri(config.FORECAST_PLAY_MP3_LOCATION + 'forecast.mp3')
