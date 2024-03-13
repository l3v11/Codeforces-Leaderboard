import os
import pandas as pd
import dateutil.relativedelta
import requests
from app import handles
from datetime import datetime
from time import time

def benchmark(func):
    # Wrapper to measure execution time of decorated function
    def timer():
        start = time()
        func()
        stop = time()
        print(f"Time taken: {stop - start:.3f}s")
    return timer

class CodeforcesHandler:
    # Provides services for requesting Codeforces API.

    def __init__(self) -> None:
        self.handle = ''
        self.name = ''
        self.location = ''
        self.organization = ''
        self.rating = 0
        self.rank = ''
        self.max_rating = 0
        self.max_rank = ''
        self.contests = 0
        self.accepted = set()
        self.contributions = 0
        self.registration_time = 0

    def __get_user_info(self):
        # Gets data from Codeforces user.info API and sets user's basic profile.
        url = f"https://codeforces.com/api/user.info?handles={self.handle}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            user_info = response.json().get('result')[0]
        except requests.exceptions.RequestException as e:
            raise SystemExit(f"Could not connect to the Codeforces API: {e}")

        first_name = user_info.get('firstName', '')
        last_name = user_info.get('lastName', '')
        self.name = '-' if not first_name and not last_name else f"{first_name} {last_name}"

        country = user_info.get('country', '')
        city = user_info.get('city', '')
        if not country and not city:
            self.location = '-'
        elif not city:
            self.location = country
        else:
            self.location = f"{city}, {country}"

        organization = user_info.get('organization', '')
        self.organization = '-' if not organization else organization

        self.rating = user_info.get('rating', 0)
        self.rank = user_info.get('rank', 'Unrated').title()
        self.max_rating = user_info.get('maxRating', 0)
        self.max_rank = user_info.get('maxRank', 'unrated')
        self.contributions = user_info.get('contribution', 0)
        self.registration_time = user_info.get('registrationTimeSeconds', 0)

    def __get_user_submission(self):
        # Gets data from Codeforces user.status API and saves submission-related details.
        url = f"https://codeforces.com/api/user.status?handle={self.handle}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            user_submission = response.json().get('result')
        except requests.exceptions.RequestException as e:
            raise SystemExit(f"Could not connect to the Codeforces API: {e}")

        for sub in user_submission:
            if sub['verdict'] == 'OK':
                contest_id = sub['problem'].get('contestId', 99999)
                index = sub['problem'].get('index')
                self.accepted.add(str(contest_id) + index)

    def __get_rating_changes(self):
        # Gets all rating changes from user.rating API and sets the total number of contests participated by the user.
        url = f"https://codeforces.com/api/user.rating?handle={self.handle}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.contests = len(response.json().get('result'))
        except requests.exceptions.RequestException as e:
            raise SystemExit(f"Could not connect to the Codeforces API: {e}")

    def __get_color(self, rating):
        # Returns the HEX of appropriate color according to the rating.
        if rating <= 1199:
            col = '#cec8c1'
        elif 1199 < rating <= 1399:
            col = '#43A217'
        elif 1399 < rating <= 1599:
            col = "#22C4AE"
        elif 1599 < rating <= 1899:
            col = "#1427B2"
        elif 1899 < rating <= 2099:
            col = "#700CB0"
        elif 2099 < rating <= 2299:
            col = "#F9A908"
        elif 2299 < rating <= 2399:
            col = "#FBB948"
        else:
            col = "#FF0000"
        return col

    def rating_color(self):
        return self.__get_color(self.rating)

    def max_rating_color(self):
        return self.__get_color(self.max_rating)

    @property
    def member_since(self):
        # Returns the registration duration on Codeforces.
        joined_at = datetime.fromtimestamp(self.registration_time)
        rd = dateutil.relativedelta.relativedelta(datetime.now(), joined_at)

        time_units = [
            (rd.years, 'year'),
            (rd.months, 'month'),
            (rd.days, 'day'),
            (rd.hours, 'hour'),
            (rd.seconds, 'second'),
            (rd.microseconds, 'microsecond'),
        ]

        for value, unit in time_units:
            if value != 0:
                return f"{int(value)} {unit}" + ('' if value <= 1 else 's')

    def make_request(self, cf_handle):
        # Makes all the necessary requests to Codeforces API.
        self.__init__()
        self.handle = cf_handle
        self.__get_user_info()
        self.__get_user_submission()
        self.__get_rating_changes()

        user_info = {
            "Name": self.name,
            "Username": f"{self.handle}",
            "Rank": self.rank,
            "Location": self.location,
            "Organization": self.organization,
            "Rating": self.rating,
            "Contest Rating": f"{self.rating} (max. {self.max_rank}, {self.max_rating})",
            "Contests Joined": self.contests,
            "Problems Solved": len(self.accepted),
            "Member Since": self.member_since
        }

        return user_info

@benchmark
def main():
    print("Generating Leaderboard...")
    print("This may take a while. Please wait...")
    codeforces_handler = CodeforcesHandler()

    user_data = []
    for handle in handles:
        user_info = codeforces_handler.make_request(handle)
        user_data.append(user_info)

    # Convert user data to DataFrame
    df = pd.DataFrame(user_data)

    # Sort DataFrame
    sort_by_column = 'Problems Solved' # 'Rating'
    df_sorted = df.sort_values(by=sort_by_column, ascending=False)

    # Drop columns
    columns_to_drop = ['Location', 'Organization', 'Rating']
    df_sorted = df_sorted.drop(columns_to_drop, axis=1)

    # Reset index to start from 1 and set the index explicitly
    df_sorted.reset_index(drop=True, inplace=True)
    df_sorted.index.name = "Sl. No."
    df_sorted.index += 1
    
    # Save DataFrame to CSV
    csv_file = 'leaderboard.csv'
    df_sorted.to_csv(csv_file)

    print(f"Saved to {os.path.join(os.getcwd(), csv_file)}")

if __name__ == '__main__':
    main()
