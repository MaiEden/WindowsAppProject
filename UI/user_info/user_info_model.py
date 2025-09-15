# user_info_model.py
from typing import List, Dict, Optional
from server.gateway.DBgateway import DbGateway

class UserInfoModel:
    def __init__(self):
        self.db = DbGateway()

    def get_user(self, username: str) -> Optional[Dict]:
        rows = self.db.query("SELECT UserId, Username, Phone, Region FROM dbo.Users WHERE Username = ?;", (username,))
        return rows[0] if rows else None

    def get_decor_used(self, user_id: int) -> List[Dict]:
        sql = """
        SELECT d.DecorId AS id,
               d.DecorName AS title,
               CONCAT(d.Category, COALESCE(' · ' + d.Theme, '')) AS subtitle,
               d.Region AS region,
               d.PhotoUrl AS photo
        FROM dbo.UserDecor ud
        INNER JOIN dbo.DecorOption d ON d.DecorId = ud.DecorId
        WHERE ud.UserId = ? AND ud.RelationType = 'USER'
        ORDER BY d.DecorName;
        """
        return self.db.query(sql, (user_id,))

    def get_services_used(self, user_id: int) -> List[Dict]:
        sql = """
        SELECT s.ServiceId AS id,
               s.ServiceName AS title,
               COALESCE(s.ShortDescription, s.Subcategory) AS subtitle,
               s.Region AS region,
               s.PhotoUrl AS photo
        FROM dbo.UserServiceLink us
        INNER JOIN dbo.ServiceOption s ON s.ServiceId = us.ServiceId
        WHERE us.UserId = ? AND us.RelationType = 'USER'
        ORDER BY s.ServiceName;
        """
        return self.db.query(sql, (user_id,))

    def get_halls_used(self, user_id: int) -> List[Dict]:
        sql = """
        SELECT h.HallId AS id,
               h.HallName AS title,
               h.HallType AS subtitle,
               h.Region AS region,
               h.PhotoUrl AS photo
        FROM dbo.UserHall uh
        INNER JOIN dbo.Hall h ON h.HallId = uh.HallId
        WHERE uh.UserId = ? AND uh.RelationType = 'USER'
        ORDER BY h.HallName;
        """
        return self.db.query(sql, (user_id,))
