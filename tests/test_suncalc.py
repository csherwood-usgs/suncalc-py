# +
# Modified version of the test file provided in suncalc-py

# I copied suncalc.py into this directory, rather than installing it
from suncalc import get_position, get_times

from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd

testTimes = {
    'solar_noon': '2013-03-05T10:10:57Z',
    'nadir': '2013-03-04T22:10:57Z',
    'sunrise': '2013-03-05T04:34:56Z',
    'sunset': '2013-03-05T15:46:57Z',
    'sunrise_end': '2013-03-05T04:38:19Z',
    'sunset_start': '2013-03-05T15:43:34Z',
    'dawn': '2013-03-05T04:02:17Z',
    'dusk': '2013-03-05T16:19:36Z',
    'nautical_dawn': '2013-03-05T03:24:31Z',
    'nautical_dusk': '2013-03-05T16:57:22Z',
    'night_end': '2013-03-05T02:46:17Z',
    'night': '2013-03-05T17:35:36Z',
    'golden_hour_end': '2013-03-05T05:19:01Z',
    'golden_hour': '2013-03-05T15:02:52Z'}

heightTestTimes = {
    'solar_noon': '2013-03-05T10:10:57Z',
    'nadir': '2013-03-04T22:10:57Z',
    'sunrise': '2013-03-05T04:25:07Z',
    'sunset': '2013-03-05T15:56:46Z'}

def test_get_position():
    """getPosition returns azimuth and altitude for the given time and location
    """
    pos = get_position(date, lng, lat)
    assert np.isclose(pos['azimuth'], -2.5003175907168385)
    assert np.isclose(pos['altitude'], -0.7000406838781611)

def test_get_times():
    """getTimes returns sun phases for the given date and location
    """
    times = get_times(date, lng, lat)
    for key, value in testTimes.items():
        assert times[key].strftime("%Y-%m-%dT%H:%M:%SZ") == value

def test_get_times_height():
    """getTimes adjusts sun phases when additionally given the observer height
    """
    times = get_times(date, lng, lat, height)
    for key, value in heightTestTimes.items():
        assert times[key].strftime("%Y-%m-%dT%H:%M:%SZ") == value

def test_get_position_pandas_single_timestamp():
    ts_date = pd.Timestamp(date)

    pos = get_position(ts_date, lng, lat)
    assert np.isclose(pos['azimuth'], -2.5003175907168385)
    assert np.isclose(pos['altitude'], -0.7000406838781611)

def test_get_position_pandas_datetime_series():
    df = pd.DataFrame({'date': [date] * 3, 'lat': [lat] * 3, 'lng': [lng] * 3})

    pos = pd.DataFrame(get_position(df['date'], df['lng'], df['lat']))

    assert pos.shape == (3, 2)
    assert all(x in pos.columns for x in ['azimuth', 'altitude'])
    assert pos.dtypes['azimuth'] == np.dtype('float64')
    assert pos.dtypes['altitude'] == np.dtype('float64')

    assert np.isclose(pos['azimuth'].iloc[0], -2.5003175907168385)
    assert np.isclose(pos['altitude'].iloc[0], -0.7000406838781611)

def test_get_times_pandas_single():
    times = get_times(date, lng, lat)

    assert isinstance(times['solar_noon'], pd.Timestamp)

def test_get_times_datetime_single():
    times = get_times(date, lng, lat)

    # This is true because pd.Timestamp is an instance of datetime.datetime
    assert isinstance(times['solar_noon'], datetime)

def test_get_times_arrays():
    df = pd.DataFrame({'date': [date] * 3, 'lat': [lat] * 3, 'lng': [lng] * 3})

    times = pd.DataFrame(get_times(df['date'], df['lng'], df['lat']))

    assert pd.api.types.is_datetime64_any_dtype(times['solar_noon'])

    assert times['solar_noon'].iloc[0].strftime(
        "%Y-%m-%dT%H:%M:%SZ") == testTimes['solar_noon']

def test_get_times_for_high_latitudes():
    """getTimes may fail (maybe only on Windows?) for high latitudes in the summer

    See https://github.com/kylebarron/suncalc-py/issues/4
    """
    date = datetime(2020, 5, 26, 0, 0, 0)
    lng = -114.0719
    lat = 51.0447

    # Make sure this doesn't raise an exception (though it will emit a warning
    # due to a division error)
    times = get_times(date, lng, lat)


# +
# Need these specific inputs to run tests
date = datetime(2013, 3, 5, tzinfo=timezone.utc)
lat = 50.5
lng = 30.5
height = 2000

# Nothing will be returned if tests are successful
test_get_position()
test_get_times()
test_get_times_height()
test_get_position_pandas_single_timestamp()
#test_get_position_pandas_datetime_series() #This doesnt work
test_get_times_pandas_single()
test_get_times_datetime_single()
test_get_times_arrays()
test_get_times_for_high_latitudes()

# +
# Here is a test with coordinates for Marconi camera (CACO-02)
date = datetime(2022, 3, 4, 17, 0, tzinfo=timezone.utc)
print(date)
lat = 41.893
lng = -69.963
height = 20.

pos = get_position(date,lng,lat)
print(pos)
times = get_times(date, lng, lat)
print('Sunrise: ',times['sunrise'])
print('Noon   : ',times['solar_noon'])
print('Sunset : ',times['sunset'])

# +
start = datetime(2022, 1, 1, 17, 0, tzinfo=timezone.utc)
dates = [start + timedelta(days=i) for i in range(10)]
sunrise = np.ones_like(dates)
sunset = np.ones_like(dates)

for i, dt in enumerate(dates):
    times = get_times(dt, lng, lat)
    sunrise[i] = times['sunrise']
    sunset[i]  = times['sunset']

print(sunrise)

df = pd.DataFrame({'date':dates,'sunrise':sunrise,'sunset':sunset})
df.to_csv('marconi_sunrise_sunset.csv',index=False)

# +
# get values for specific date
df.set_index(pd.DatetimeIndex(df.date), inplace=True)

df.sort_index().loc['2022-01-05']['sunrise'].values
# -

pd.to_datetime(dates)

# This is a reasonable way to create a dataframe with date range and columns of lat/lon
dates = pd.date_range(start="2022-03-04 17:00:00",
                                   end = '2022-03-13 17:00:00',
                                   freq = '1D',
                                   tz=timezone.utc).values
print(np.shape(dates))
print(type(dates[0]))
df = pd.DataFrame({
     'date': [pd.to_datetime(dates)],

     'lon': [lons],
     'lat': [lats]
})
print(df)

# ...but suncalc.py cannot convert the DateTimeIndex to a datetime. I think this is a missing feature in suncalc-py
df['sunrise'] = get_times(df['date'], df['lon'], df['lat'])['sunrise']
print(df)



