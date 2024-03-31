from src.core.config import settings

base_url = f"{settings.PREFIX}/"


class BaseTest:
    url: str

    @staticmethod
    def extract_error_message(data):
        return data["error"], data.get("details")

    @staticmethod
    def make_auth_headers(csrf_token):
        return {"Authorization": f"Bearer {csrf_token}"}

    @staticmethod
    def make_auth_cookies(refresh_token, access_token=None):
        base = {"Refresh-Token": refresh_token}
        if access_token:
            base["Access-Token"] = access_token
            return base
        return base

    def headers_cookies(self, refreshed_namedtuple) -> dict[str, dict[str, str]]:
        headers = self.make_auth_headers(refreshed_namedtuple.csrf_token)
        cookies = self.make_auth_cookies(
            refreshed_namedtuple.refresh_token, refreshed_namedtuple.access_token
        )
        return {"headers": headers, "cookies": cookies}

    def headers_cookies_tuple(self, refreshed_namedtuple):
        _ = self.headers_cookies(refreshed_namedtuple)
        return _["headers"], _["cookies"]
