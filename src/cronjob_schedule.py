import random

class CronJobSchedule(object):

    MINUTE = 'MINUTE'
    HOUR = 'HOUR'

    def __init__(self, car_config):
        self.car_config = car_config

    """
    _schedule(self, start, frequency, _type) is private method that builds the schedule of the MINUTE, HOUR or DAY
    """
    def _schedule(self, start, frequency, _type):
        if frequency == 0:
            return "*"
        if _type == self.MINUTE:
            MAX_VAL = 60
        elif _type == self.HOUR:
            MAX_VAL = 24
        schedule_list =[start]
        sch = ''
        # if frequency = 0, change it to 1 because it is every TYPE (minute or hour or day or month) starting from TYPE# start
        if frequency == 0:
            frequency = 1
        inc_sum = start + frequency
        while inc_sum < MAX_VAL:
            schedule_list.append(inc_sum)
            inc_sum += frequency
        last_val = schedule_list[len(schedule_list)-1]
        delta = MAX_VAL - last_val
        inc_sum = frequency - delta
        while inc_sum < start:
            schedule_list.append(inc_sum)
            inc_sum += frequency
        # build the minute schedule
        for val in schedule_list:
            sch = '{}{},'.format(sch, val)
        return sch[:len(sch)-1]



    def frequency_to_schedule(self):
        ONE_DAY_MIN = 1440
        ONE_HOUR_MIN = 60
        if self.car_config.frequency > 0 and self.car_config.frequency < ONE_HOUR_MIN and ONE_HOUR_MIN % self.car_config.frequency == 0:
            # every X minutes and randomly
            start = random.randrange(59)
            minutes = self._schedule(start, self.car_config.frequency, self.MINUTE)
            cron_schedule = '{} * * * *'.format(minutes)
        elif self.car_config.frequency >= ONE_HOUR_MIN and self.car_config.frequency < ONE_DAY_MIN and self.car_config.frequency % ONE_HOUR_MIN == 0:
            # In this case no start time is needed, will start from hour#0
            start = random.randrange(23)
            start_min = random.randrange(59)
            hours = self._schedule(start, int(self.car_config.frequency/ONE_HOUR_MIN), self.HOUR)
            cron_schedule = '{} {} * * *'.format(start_min, hours)
        elif self.car_config.frequency == ONE_DAY_MIN:
            # this is daily, if start_time is given then use it, otherwise use whatever default in cronjob default (@daily)
            if self.car_config.time:
                hours, minutes = self.car_config.time.split(':')
            else:
                minutes = random.randrange(59)
                hours = random.randrange(23)
            cron_schedule = '{} {} * * *'.format(minutes, hours)
        else:
            raise ValueError('Unpermitted value of frequency: {}'.format(self.car_config.frequency))
        return cron_schedule

    def schedule_to_frequency(self, schedule):
        # parse the schedule to grab the frequency and the start_time
        frequency = None
        start_min = None
        start_h = None
        if schedule:
            schedule_array = schedule.split(' ')
            minutes = schedule_array[0].split(',')
            hours = schedule_array[1].split(',')
            days = schedule_array[2].split(',')
            if len(hours) > 1:
                # It is hour frequency
                frequency = (int(hours[1]) - int(hours[0])) * 60
            elif len(minutes) > 1:
                # It is minute frequency
                frequency = int(minutes[1]) - int(minutes[0])
            else:
                # It is daily frequency
                frequency = 1440
                start_h = int(hours[0])
                start_min = int(minutes[0])
        return frequency, start_min, start_h
            
            
            
        