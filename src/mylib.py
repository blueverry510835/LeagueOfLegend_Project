from urllib.parse import quote

import requests


def get_Key(path, name=None):
    """key.properties 파일에서 API 키를 읽어온다.

    지원 형식:
      - 키만 한 줄로 적은 경우:   RGAPI-xxxx
      - 이름=값 형식:             api_key=RGAPI-xxxx
    name을 주면 그 이름의 값을, 안 주면 첫 번째 값을 반환한다.
    """
    with open(path, encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]

    if not lines:
        raise ValueError(f"{path} 파일에 키가 없습니다")

    for line in lines:
        if "=" in line:
            k, v = line.split("=", 1)
            if name is None or k.strip() == name:
                return v.strip()
        elif name is None:
            return line

    raise KeyError(f"{path} 파일에서 '{name}'을(를) 찾을 수 없습니다")


# ---- Riot API ----
# host: 계정/매치 API는 대륙(asia), 소환사/리그 API는 서버(kr)를 쓴다.

def riot_get(key, host, path, params=None):
    """https://{host}.api.riotgames.com{path} 로 요청. 키는 X-Riot-Token 헤더로 보낸다."""
    url = f"https://{host}.api.riotgames.com{path}"
    r = requests.get(url, headers={"X-Riot-Token": key}, params=params, timeout=15)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code} 에러: {r.text}  ({url})")
    return r.json()


def get_account(key, game_name, tag_line):
    """Riot ID(이름#태그)로 계정 정보(puuid 포함) 조회. Account-V1"""
    path = f"/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    return riot_get(key, "asia", path)


def get_summoner(key, puuid):
    """puuid로 소환사 정보(레벨, 아이콘 등) 조회. Summoner-V4"""
    return riot_get(key, "kr", f"/lol/summoner/v4/summoners/by-puuid/{puuid}")


def get_match_ids(key, puuid, count=20, start=0, queue=None):
    """puuid로 최근 경기 ID 목록 조회. queue=420이면 솔로랭크만. Match-V5"""
    params = {"start": start, "count": count}
    if queue is not None:
        params["queue"] = queue
    return riot_get(key, "asia", f"/lol/match/v5/matches/by-puuid/{puuid}/ids", params)


def get_match(key, match_id):
    """경기 ID로 경기 상세 정보 조회. Match-V5"""
    return riot_get(key, "asia", f"/lol/match/v5/matches/{match_id}")
