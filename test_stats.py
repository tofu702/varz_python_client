import unittest

import stats

class SamplerStatsTestCase(unittest.TestCase):
  def setUp(self):
    self.latest_time_sec = 60 * 140000
  
  def createFakeData(self, all_time_duration_sec=3600*24*3, all_time_samples=1000, all_time_events=5000):
    minute_samples = self.createFakeSamples(self.latest_time_sec,
                                            self.latest_time_sec - 60, 100, 2000)
    alltime_samples = self.createFakeSamples(self.latest_time_sec,
                                             self.latest_time_sec - all_time_duration_sec,
                                             all_time_samples,
                                             all_time_events)
    return {"latest_time_sec": self.latest_time_sec,
            "last_minute_samples": minute_samples,
            "all_time_samples": alltime_samples}

  def createFakeSamples(self, start_time, end_time, num_samples, num_events=None):
    num_events = num_events if num_events is not None else num_samples
    step = (end_time - start_time) / float(num_samples)
    sample_times_sec = [start_time + int(x*step) for x in range(0, num_samples)]
    return {"sample_values": range(0, num_samples),
            "sample_times_sec": sample_times_sec,
            "samples_size": num_samples,
            "num_events": num_events}

  def test_last_minute_stats(self):
    s = stats.SamplerStats(self.createFakeData(), self.latest_time_sec)
    min_stats = s.last_minute_stats()
    self.assertEquals(25, min_stats["quartile_1"])
    self.assertEquals(50, min_stats["median"])
    self.assertEquals(75, min_stats["quartile_3"])
    self.assertEquals(95, min_stats["percentile_95"])
    self.assertEquals(99, min_stats["largest_value"])
    self.assertEquals(2000, min_stats["count"])

  def test_last_minute_stats_returns_correctly_if_different_sec_but_same_min(self):
    s = stats.SamplerStats(self.createFakeData(), self.latest_time_sec + 59)
    min_stats = s.last_minute_stats()
    self.assertEquals(25, min_stats["quartile_1"])
    self.assertEquals(50, min_stats["median"])
    self.assertEquals(75, min_stats["quartile_3"])
    self.assertEquals(95, min_stats["percentile_95"])
    self.assertEquals(99, min_stats["largest_value"])
    self.assertEquals(2000, min_stats["count"])


  def test_last_minute_stats_returns_zeros_if_minutes_are_off(self):
    s = stats.SamplerStats(self.createFakeData(), self.latest_time_sec + 60)
    min_stats = s.last_minute_stats()
    self.assertEquals(0, min_stats["quartile_1"])
    self.assertEquals(0, min_stats["median"])
    self.assertEquals(0, min_stats["quartile_3"])
    self.assertEquals(0, min_stats["percentile_95"])
    self.assertEquals(0, min_stats["largest_value"])
    self.assertEquals(0, min_stats["count"])

  def test_all_time_stats(self):  
    s = stats.SamplerStats(self.createFakeData(), self.latest_time_sec)
    at_stats= s.all_time_stats()
    self.assertEquals(250, at_stats["quartile_1"])
    self.assertEquals(500, at_stats["median"])
    self.assertEquals(750, at_stats["quartile_3"])
    self.assertEquals(950, at_stats["percentile_95"])
    self.assertEquals(999, at_stats["largest_value"])
    self.assertEquals(5000, at_stats["count"])

  def test_hour_stats(self):
    s = stats.SamplerStats(self.createFakeData(3600*3, 600, 6000), self.latest_time_sec)
    hr_stats = s.last_hour_stats()
    self.assertEquals(50, hr_stats["quartile_1"])
    self.assertEquals(100, hr_stats["median"])
    self.assertEquals(150, hr_stats["quartile_3"])
    self.assertEquals(190, hr_stats["percentile_95"])
    self.assertEquals(199, hr_stats["largest_value"])
    self.assertEquals(2000, hr_stats["count"])

  def test_hour_stats_with_partial_hour_overlap(self):
    s = stats.SamplerStats(self.createFakeData(3600*3, 600, 6000), self.latest_time_sec+1800)
    hr_stats = s.last_hour_stats()
    self.assertEquals(25, hr_stats["quartile_1"])
    self.assertEquals(50, hr_stats["median"])
    self.assertEquals(75, hr_stats["quartile_3"])
    self.assertEquals(95, hr_stats["percentile_95"])
    self.assertEquals(99, hr_stats["largest_value"])
    self.assertEquals(1000, hr_stats["count"])

  def test_hour_stats_with_no_hour_overlap(self):
    s = stats.SamplerStats(self.createFakeData(3600*3, 600, 6000), self.latest_time_sec+3600)
    hr_stats = s.last_hour_stats()
    self.assertEquals(0, hr_stats["quartile_1"])
    self.assertEquals(0, hr_stats["median"])
    self.assertEquals(0, hr_stats["quartile_3"])
    self.assertEquals(0, hr_stats["percentile_95"])
    self.assertEquals(0, hr_stats["largest_value"])
    self.assertEquals(0, hr_stats["count"])


class CounterStatsTestCase(unittest.TestCase):
  def setUp(self):
    pass

  def createFakeData(self, latest_time_sec=615*60):
    return {"min_counters": range(0,60),
            "all_time_count": 5000,
            "latest_time_sec": latest_time_sec}

  def test_last_minute_count(self):
    s = stats.CounterStats(self.createFakeData(), 615*60)
    self.assertEquals(15, s.last_minute_count())

  def test_last_minute_count_diff_second_in_same_minute(self):
    s = stats.CounterStats(self.createFakeData(), 615*60+15)
    self.assertEquals(15, s.last_minute_count())

  def test_last_minute_count_for_prior_minute_returns_zero(self):
    s = stats.CounterStats(self.createFakeData(), 616*60)
    self.assertEquals(0, s.last_minute_count())
   
  def test_last_minute_count_returns_zero_for_future_minute(self):
    s = stats.CounterStats(self.createFakeData(), 614*60)
    self.assertEquals(0, s.last_minute_count())

  def test_last_hour_count_for_full_hour(self):
    s = stats.CounterStats(self.createFakeData(), 615*60)
    self.assertEquals(1770, s.last_hour_count())

  def test_last_hour_count_for_partial_hour(self):
    s = stats.CounterStats(self.createFakeData(), 620*60)
    self.assertEquals(1770-16-17-18-19-20, s.last_hour_count())

  def test_last_hour_count_returns_zero_for_more_than_1_hr_ahead(self):
    s = stats.CounterStats(self.createFakeData(), 675*60)
    self.assertEquals(0, s.last_hour_count())

  def test_last_hour_count_returns_zero_for_future_time(self):
    s = stats.CounterStats(self.createFakeData(), 610*60)
    self.assertEquals(0, s.last_hour_count())

  def test_all_time_count(self):
    s = stats.CounterStats(self.createFakeData(), 610*60)
    self.assertEquals(5000, s.all_time_count())

if __name__ == "__main__":
  unittest.main()
