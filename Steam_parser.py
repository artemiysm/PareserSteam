from abc import ABC, abstractmethod
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


# Абстрактный класс
class BaseEntity(ABC):
    @abstractmethod
    def __str__(self):
        pass

class Badges(BaseEntity):
    def __init__(self, id: int, title: str, achievements: str):
        self.id = id
        self.title = title
        self.achievements = achievements

    def __eq__(self, other):
        return self.id == other.id

    def __add__(self, other):
        return Badges(self.id, f"{self.title} & {other.title}", f"{self.achievements} & {other.achievements}")

    def __gt__(self, other):
        return self.id > other.id

    def __str__(self):
        return f"Badge(ID={self.id}, Title={self.title}, Achievements={self.achievements})"

class User(BaseEntity):
    def __init__(self, steam_id: int, username: str, level: int, badges: List[Badges]):
        self.steam_id = steam_id
        self.username = username
        self.level = level
        self.badges = badges

    def format_username(self):
        return f"User: {self.username.upper()}"

    def increase_level(self, amount: int):
        self.level += amount

    def __str__(self):
        return f"User(SteamID={self.steam_id}, Username={self.username}, Level={self.level}, Badges={len(self.badges)})"


class Friend(BaseEntity):
    def __init__(self, friend_id: int, username: str):
        self.friend_id = friend_id
        self.username = username

    def __str__(self):
        return f"Friend(ID={self.friend_id}, Username={self.username})"



class SteamParser:
    API_KEY = "24D998CDEA5F8F3350092BA126426D7A"

    @staticmethod
    def get_api_key():
        return SteamParser.API_KEY

    def __init__(self):
        self.badges_dict: Dict[int, Badges] = {}  # Словарь для значков
        self.users_dict: Dict[int, User] = {}     # Словарь для пользователей
        self.friends_dict: Dict[int, Friend] = {} # Словарь для друзей

    def parse_badges(self, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе: {e}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        badges = soup.find_all('div', class_='badge_row is_link')

        for badge in badges:
            try:
                title_element = badge.find('div', class_='badge_info_title')
                title = title_element.text.strip() if title_element else "Unknown"

                achievements_element = badge.find('div', class_='badge_info_unlocked')
                achievements = str(achievements_element.text.strip() if achievements_element else "0")

                new_badge = Badges(
                    id=len(self.badges_dict) + 1,
                    title=title,
                    achievements=achievements,
                )

                self.badges_dict[new_badge.id] = new_badge
            except Exception as e:
                print(f"Ошибка при парсинге значка: {e}")

    def parse_user(self, steam_id: int, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе: {e}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # Парс пользователя
        username_element = soup.find('span', class_='actual_persona_name')
        username = username_element.text.strip() if username_element else "Unknown"

        # Парс уровня
        level_element = soup.find('span', class_='friendPlayerLevelNum')
        level = int(level_element.text.strip()) if level_element else 0

        # Парс значков
        badges = []
        badge_items = soup.find_all('div', class_='badge_card')

        for item in badge_items:
            title_element = item.find('div', class_='badge_info')
            title = title_element.text if title_element else "Unknown"

            achievements_element = item.find('div', class_='badge_info_unlocked')
            achievements = achievements_element.text.strip() if achievements_element else "0"

            badge = Badges(
                id=len(self.badges_dict) + 1,
                title=title,
                achievements=achievements,
            )
            badges.append(badge)

        new_user = User(
            steam_id=steam_id,
            username=username,
            level=level,
            badges=badges,
        )
        self.users_dict[new_user.steam_id] = new_user

    def parse_friends(self, steam_id: int, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе: {e}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        friends = soup.find_all('div', class_='selectable')

        for friend in friends:
            try:
                friend_id = friend.get('data-steamid')

                username_element = friend.find('div', class_='friend_block_content')
                username = username_element.text.strip() if username_element else "Unknown"

                new_friend = Friend(
                    friend_id=int(friend_id),
                    username=username,
                )
                self.friends_dict[new_friend.friend_id] = new_friend
            except Exception as e:
                print(f"Ошибка при парсинге друга: {e}")


# Класс Report для генерации отчета
class Report:
    def __init__(self, badges_list: list, users_list: list, friends_list: list):
        self.badges_list = badges_list
        self.users_list = users_list
        self.friends_list = friends_list

    def generate(self) -> dict:
        return {
            "total_badges": len(self.badges_list),
            "total_users": len(self.users_list),
            "total_friends": len(self.friends_list),
            "badges": [str(badge) for badge in self.badges_list],
            "users": [str(user) for user in self.users_list],
            "friends": [str(friend) for friend in self.friends_list],
        }


# Основной блок
if __name__ == "__main__":
    parser = SteamParser()

    # Парсинг данных
    parser.parse_badges("https://steamcommunity.com/profiles/76561198807849076/badges/")
    parser.parse_user(76561198807849076, "https://steamcommunity.com/profiles/76561198807849076")
    parser.parse_friends(76561198807849076, "https://steamcommunity.com/profiles/76561198807849076/friends/")

    # Отчёт
    report = Report(list(parser.badges_dict.values()), list(parser.users_dict.values()), list(parser.friends_dict.values()))
    report_dict = report.generate()

    print(report_dict)

    # перегрузка операторов
    badge1 = Badges(1, "First Badge", "10 achievements")
    badge2 = Badges(2, "Second Badge", "5 achievements")
    combined_badge = badge1 + badge2
    print(combined_badge)

    # обработка строк
    user = User(76561198807849076, "JohnDoe", 10, [])
    print(user)

    # обработка исключений
    parser.parse_badges("invalid_url")