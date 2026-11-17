"""
역할 (Role) 모델
"""

from typing import Union

from app.utils.constants import Role as RoleEnum


class Role:
    """
    플레이어 역할 클래스
    
    역할은 게임 시작 시 할당되며, 승리 조건을 결정합니다.
    """
    
    def __init__(self, role: Union[RoleEnum, str, "Role"]):
        """
        Args:
            role: 역할 Enum 값
        """
        self.role: RoleEnum
        self.name: str
        # role이 이미 Role 객체인 경우 처리
        if isinstance(role, Role):
            self.role = role.role
            self.name = role.name
        elif isinstance(role, str):
            # 문자열인 경우 RoleEnum으로 변환 시도
            try:
                # RoleEnum에서 해당 문자열을 찾기
                for r in RoleEnum:
                    if r.value == role:
                        self.role = r
                        self.name = r.value
                        return
                # 찾지 못한 경우 기본값 사용
                self.role = RoleEnum.SHERIFF
                self.name = RoleEnum.SHERIFF.value
            except Exception:
                self.role = RoleEnum.SHERIFF
                self.name = RoleEnum.SHERIFF.value
        else:
            # RoleEnum인 경우
            self.role = role
            self.name = role.value
    
    @property
    def is_sheriff(self) -> bool:
        """상단주 여부"""
        return self.role == RoleEnum.SHERIFF
    
    @property
    def is_deputy(self) -> bool:
        """원로원 여부"""
        return self.role == RoleEnum.DEPUTY
    
    @property
    def is_outlaw(self) -> bool:
        """적도 세력 여부"""
        return self.role == RoleEnum.OUTLAW
    
    @property
    def is_renegade(self) -> bool:
        """야망가 여부"""
        return self.role == RoleEnum.RENEGADE
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Role({self.name})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Role):
            return self.role == other.role
        return False

