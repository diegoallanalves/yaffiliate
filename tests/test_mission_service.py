from pprint import pprint

from app.services.mission_service import MissionService


def main() -> None:
    service = MissionService()

    mission = service.get_daily_mission()

    pprint(mission)


if __name__ == "__main__":
    main()