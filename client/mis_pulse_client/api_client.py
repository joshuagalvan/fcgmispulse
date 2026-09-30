import requests


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    def __init__(self, base_url: str, token: str | None = None, timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        try:
            resp = requests.request(
                method, url, headers=self._headers(), timeout=self.timeout, **kwargs
            )
        except requests.RequestException as e:
            raise ApiError(f"Could not reach the server at {self.base_url}: {e}") from e

        if resp.status_code >= 400:
            detail = None
            try:
                detail = resp.json().get("detail")
            except Exception:
                pass
            raise ApiError(
                detail or f"Server error ({resp.status_code})", status_code=resp.status_code
            )
        return resp

    # ---- auth ----

    def login(self, username: str, password: str) -> dict:
        data = self._request(
            "POST", "/auth/login", json={"username": username, "password": password}
        ).json()
        self.token = data["token"]
        return data

    def me(self) -> dict:
        return self._request("GET", "/auth/me").json()

    def logout(self) -> None:
        self._request("POST", "/auth/logout")

    # ---- entries ----

    def list_entries(self, **params) -> dict:
        clean = {k: v for k, v in params.items() if v not in (None, "")}
        return self._request("GET", "/entries", params=clean).json()

    def create_entry(self, payload: dict) -> dict:
        return self._request("POST", "/entries", json=payload).json()

    def update_entry(self, entry_id: int, payload: dict) -> dict:
        return self._request("PUT", f"/entries/{entry_id}", json=payload).json()

    def delete_entry(self, entry_id: int) -> None:
        self._request("DELETE", f"/entries/{entry_id}")

    # ---- lookups ----

    def brands(self) -> list[str]:
        return self._request("GET", "/lookups/brands").json()

    def locations(self, location_type: str, brand: str | None = None) -> list[str]:
        params = {"location_type": location_type}
        if brand:
            params["brand"] = brand
        return self._request("GET", "/lookups/locations", params=params).json()

    def area_managers(self) -> list[str]:
        return self._request("GET", "/lookups/area-managers").json()

    def reported_by(self, q: str = "") -> list[str]:
        return self._request("GET", "/lookups/reported-by", params={"q": q}).json()

    # ---- lookup management (admin) ----

    def manage_list(self, kind: str) -> list[dict]:
        return self._request("GET", "/lookups/manage", params={"kind": kind}).json()

    def add_lookup(
        self, kind: str, value: str, location_type: str | None = None, brand: str | None = None
    ) -> dict:
        return self._request(
            "POST",
            "/lookups",
            json={"kind": kind, "location_type": location_type, "brand": brand, "value": value},
        ).json()

    def update_lookup(self, lookup_id: int, **fields) -> dict:
        return self._request("PUT", f"/lookups/{lookup_id}", json=fields).json()

    def remove_lookup(self, lookup_id: int) -> None:
        self._request("DELETE", f"/lookups/{lookup_id}")

    # ---- export ----

    def export(self, month: str, dest_path: str) -> str:
        resp = self._request("GET", "/export", params={"month": month}, stream=True)
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        return dest_path

    def server_version(self) -> dict:
        return self._request("GET", "/version").json()
