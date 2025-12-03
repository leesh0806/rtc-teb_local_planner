#!/usr/bin/env python3
"""
웨이포인트 좌표 정의

실험 시나리오별 웨이포인트 좌표를 정의합니다.
각 웨이포인트는 (x, y, yaw_degrees) 튜플로 표현됩니다.

사용법:
    from waypoint_definitions import SCENARIOS
    waypoints = SCENARIOS['open_space']
"""

# 단일 시나리오: 3-Stage 비교 실험 (사용자 정의)
# 목적: 동일한 선형 구간을 여러 번 왕복하며 TEB/MPPI의 성능 비교
#
# Stage 1:
#   시작점: [0.0,  0.0,   0°]
#   끝점:   [5.6, -2.5,   0°]
#
# Stage 2:
#   시작점: Stage 1의 끝점
#   끝점:   [13.6, -2.5,  0°]
#
# Stage 3:
#   시작점: Stage 2의 끝점
#   끝점:   [5.6, -2.5, 180°]
#
# → 총 네 개의 웨이포인트를 순차적으로 따라감
STAGE123_WAYPOINTS = [
    (0.0,   0.0,   0.0),    # Stage 1 시작점
    (5.6,  -2.47,   0.0),    # Stage 1 끝점 (= Stage 2 시작점)
    (13.4, -2.47,   0.0),    # Stage 2 끝점 (= Stage 3 시작점)
    (5.6,  -2.47,   0.0),    # Stage 3 끝점 (복귀)
]

# 시나리오 딕셔너리
SCENARIOS = {
    'stage123': STAGE123_WAYPOINTS,
}

# 시나리오 설명
SCENARIO_DESCRIPTIONS = {
    'stage123': 'Three-stage straight-line scenario: 0→5.6→13.6→5.6 with final 180° rotation',
}


def get_waypoint_list(scenario_name='stage123'):
    """
    시나리오 이름으로 웨이포인트 리스트 반환
    
    Args:
        scenario_name (str): 시나리오 이름
        
    Returns:
        list: (x, y, yaw) 튜플 리스트
    """
    return SCENARIOS.get(scenario_name, STAGE123_WAYPOINTS)


def get_scenario_description(scenario_name='stage123'):
    """
    시나리오 설명 반환
    
    Args:
        scenario_name (str): 시나리오 이름
        
    Returns:
        str: 시나리오 설명
    """
    return SCENARIO_DESCRIPTIONS.get(
        scenario_name, 
        'Unknown scenario'
    )


def list_scenarios():
    """사용 가능한 시나리오 목록 출력"""
    print("\n📋 Available Scenarios:")
    print("=" * 60)
    for name, waypoints in SCENARIOS.items():
        desc = SCENARIO_DESCRIPTIONS[name]
        print(f"\n{name}:")
        print(f"  Description: {desc}")
        print(f"  Waypoints: {len(waypoints)} points")
    print("\n" + "=" * 60 + "\n")


if __name__ == '__main__':
    # 스크립트 직접 실행 시 시나리오 목록 출력
    list_scenarios()

