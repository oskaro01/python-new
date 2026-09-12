"""
Task 22: Intervals

An interval is a range with a start and an end.

Real examples:
- meeting time: 10 to 12
- booking date: 2026-09-01 to 2026-09-05
- study session: 7 PM to 8 PM
- sale period: day 1 to day 10

Common interval questions:
- Do these two ranges overlap?
- Is there a schedule conflict?
- Can we merge overlapping ranges?
- Where can we insert a new booking?
"""


def intervals_overlap(first, second):
    first_start, first_end = first
    second_start, second_end = second

    return first_start < second_end and second_start < first_end


def has_conflict(intervals):
    intervals = sorted(intervals)

    for index in range(1, len(intervals)):
        previous = intervals[index - 1]
        current = intervals[index]

        if intervals_overlap(previous, current):
            return True

    return False


def find_conflicts(intervals):
    intervals = sorted(intervals)
    conflicts = []

    for index in range(1, len(intervals)):
        previous = intervals[index - 1]
        current = intervals[index]

        if intervals_overlap(previous, current):
            conflicts.append((previous, current))

    return conflicts


def merge_intervals(intervals):
    if len(intervals) == 0:
        return []

    intervals = sorted(intervals)
    merged = [intervals[0]]

    for current_start, current_end in intervals[1:]:
        last_start, last_end = merged[-1]

        if current_start <= last_end:
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            merged.append((current_start, current_end))

    return merged


def can_add_interval(intervals, new_interval):
    for interval in intervals:
        if intervals_overlap(interval, new_interval):
            return False

    return True


def insert_and_merge(intervals, new_interval):
    intervals.append(new_interval)
    return merge_intervals(intervals)


print("=== OVERLAP CHECK ===")

meeting_a = (10, 12)
meeting_b = (11, 13)
meeting_c = (13, 14)

print(f"{meeting_a} overlaps {meeting_b}: {intervals_overlap(meeting_a, meeting_b)}")
print(f"{meeting_a} overlaps {meeting_c}: {intervals_overlap(meeting_a, meeting_c)}")


print("\n=== SCHEDULE CONFLICT ===")

schedule = [
    (9, 10),
    (10, 11),
    (10.5, 12),
    (13, 14),
]

print(f"Schedule has conflict: {has_conflict(schedule)}")
print(f"Conflicts: {find_conflicts(schedule)}")


print("\n=== MERGE INTERVALS ===")

busy_times = [
    (1, 3),
    (2, 6),
    (8, 10),
    (9, 12),
    (15, 18),
]

merged_times = merge_intervals(busy_times)

print(f"Before: {busy_times}")
print(f"After:  {merged_times}")


print("\n=== ADD NEW BOOKING ===")

bookings = [
    (9, 10),
    (11, 12),
    (14, 16),
]

new_booking = (12, 13)
bad_booking = (9.5, 10.5)

print(f"Can add {new_booking}: {can_add_interval(bookings, new_booking)}")
print(f"Can add {bad_booking}: {can_add_interval(bookings, bad_booking)}")


print("\n=== INSERT AND MERGE ===")

sale_periods = [
    (1, 5),
    (10, 15),
]

new_sale = (4, 12)

print(insert_and_merge(sale_periods, new_sale))


print("\n=== PRACTICAL EXAMPLE: NAMED MEETINGS ===")

meetings = [
    {"name": "Study", "start": 9, "end": 10},
    {"name": "Python", "start": 10, "end": 11},
    {"name": "Call", "start": 10.5, "end": 12},
    {"name": "Dinner", "start": 18, "end": 19},
]


def find_meeting_conflicts(meetings):
    sorted_meetings = sorted(meetings, key=lambda meeting: meeting["start"])
    conflicts = []

    for index in range(1, len(sorted_meetings)):
        previous = sorted_meetings[index - 1]
        current = sorted_meetings[index]

        previous_interval = (previous["start"], previous["end"])
        current_interval = (current["start"], current["end"])

        if intervals_overlap(previous_interval, current_interval):
            conflicts.append((previous["name"], current["name"]))

    return conflicts


meeting_conflicts = find_meeting_conflicts(meetings)
print(meeting_conflicts)

"""
It teaches:
- checking if two intervals overlap
- detecting schedule conflicts
- finding conflicting meetings
- merging overlapping ranges
- checking if a new booking can be added
This is extremely practical for calendars, appointments, bookings, study sessions, and date ranges.

"""

print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Make a list of study sessions as intervals.
# 2. Check if the sessions have a conflict.
# 3. Merge overlapping sessions.
# 4. Make a list of named meetings.
# 5. Use find_meeting_conflicts() to find conflicting meeting names.
