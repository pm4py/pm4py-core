import datetime


class BusinessHours:

    def __init__(self, datetime1, datetime2, worktiming=[7, 17],
                 weekends=[6, 7]):
        self.weekends = weekends
        self.worktiming = worktiming
        self.datetime1 = datetime1
        self.datetime2 = datetime2
        self.day_hours = (self.worktiming[1] - self.worktiming[0])
        self.day_minutes = self.day_hours * 60  # minutes in a work day

    def getdays(self):
        return int(self.getminutes() / self.day_minutes)

    def gethours(self):
        return int(self.getminutes() / 60)

    def getseconds(self):
        return self.getminutes() * 60

    def getminutes(self):
        """
        Return the difference in minutes.
        """
        # Set initial default variables
        dt_start = self.datetime1  # datetime of start
        dt_end = self.datetime2  # datetime of end
        worktime_in_seconds = 0

        if dt_start.date() == dt_end.date():
            # starts and ends on same workday
            full_days = 0
            if self.is_weekend(dt_start):
                return 0
            else:
                if dt_start.hour < self.worktiming[0]:
                    # set start time to opening hour
                    dt_start = datetime.datetime(
                        year=dt_start.year,
                        month=dt_start.month,
                        day=dt_start.day,
                        hour=self.worktiming[0],
                        minute=0)
                if dt_start.hour >= self.worktiming[1] or \
                        dt_end.hour < self.worktiming[0]:
                    return 0
                if dt_end.hour >= self.worktiming[1]:
                    dt_end = datetime.datetime(
                        year=dt_end.year,
                        month=dt_end.month,
                        day=dt_end.day,
                        hour=self.worktiming[1],
                        minute=0)
                worktime_in_seconds = (dt_end - dt_start).total_seconds()
        elif (dt_end - dt_start).days < 0:
            # ends before start
            return 0
        else:
            # start and ends on different days
            current_day = dt_start  # marker for counting workdays
            while not current_day.date() == dt_end.date():
                if not self.is_weekend(current_day):
                    if current_day == dt_start:
                        # increment hours of first day
                        if current_day.hour < self.worktiming[0]:
                            # starts before the work day
                            worktime_in_seconds += self.day_minutes * 60  # add 1 full work day
                        elif current_day.hour >= self.worktiming[1]:
                            pass  # no time on first day
                        else:
                            # starts during the working day
                            dt_currentday_close = datetime.datetime(
                                year=dt_start.year,
                                month=dt_start.month,
                                day=dt_start.day,
                                hour=self.worktiming[1],
                                minute=0)
                            worktime_in_seconds += (dt_currentday_close
                                                    - dt_start).total_seconds()
                    else:
                        # increment one full day
                        worktime_in_seconds += self.day_minutes * 60
                current_day += datetime.timedelta(days=1)  # next day
            # Time on the last day
            if not self.is_weekend(dt_end):
                if dt_end.hour >= self.worktiming[1]:  # finish after close
                    # Add a full day
                    worktime_in_seconds += self.day_minutes * 60
                elif dt_end.hour < self.worktiming[0]:  # close before opening
                    pass  # no time added
                else:
                    # Add time since opening
                    dt_end_open = datetime.datetime(
                        year=dt_end.year,
                        month=dt_end.month,
                        day=dt_end.day,
                        hour=self.worktiming[0],
                        minute=0)
                    worktime_in_seconds += (dt_end - dt_end_open).total_seconds()
        return int(worktime_in_seconds / 60)

    def is_weekend(self, datetime):
        """
        Returns True if datetime lands on a weekend.
        """
        for weekend in self.weekends:
            if datetime.isoweekday() == weekend:
                return True
        return False