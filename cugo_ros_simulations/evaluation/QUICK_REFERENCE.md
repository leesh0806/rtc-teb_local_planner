# TEB vs MPPI 빠른 참조표

## 📋 핵심 파라미터 한눈에 보기

### ✅ 동일한 파라미터 (공정한 비교 보장)

| 제약 조건 | 값 | TEB | MPPI |
|----------|---|-----|------|
| 🚗 **최대 속도** | 0.4 m/s | `max_vel_x` | `vx_max` |
| 🔄 **최대 각속도** | 1.0 rad/s (57°/s) | `max_vel_theta` | `wz_max` |
| ⚡ **최대 가속도** | 0.8 m/s² | `acc_lim_x` | `ax_max` |
| 🔃 **최대 각가속도** | 3.2 rad/s² | `acc_lim_theta` | `az_max` |
| ⏱️ **예측 시간** | ~4.0초 | 동적 조정 | 80 × 0.05s |
| 📏 **예측 거리** | ~1.6m | v × t | 0.4 × 4.0 |
| 🛡️ **안전 거리** | 0.6m | `inflation_dist` | `inflation_radius` |
| 📐 **로봇 크기** | 0.7×0.5m | footprint | costmap |
| 🎯 **위치 정확도** | ±0.25m | `xy_goal_tolerance` | 동일 |
| 🧭 **방향 정확도** | ±14.3° | `yaw_goal_tolerance` | 동일 |
| 🕐 **제어 주기** | 50ms (20Hz) | `controller_frequency` | 동일 |

---

## 🔧 주요 수정 사항 (MPPI)

### 수정 전 → 수정 후

```yaml
# 1. 예측 시간 확장 (TEB와 동등하게)
time_steps: 56 → 80
# 2.8초 → 4.0초 예측

# 2. 안전 거리 통일 (TEB와 동일하게)
inflation_radius: 0.55 → 0.6
# 0.55m → 0.6m

# 3. GPU 샘플링 (유지)
batch_size: 2000  # GPU 사용 시
```

---

## 📊 수식 정리

### 속도/가속도 제약
```
|v(t)| ≤ 0.4 m/s
|ω(t)| ≤ 1.0 rad/s
|a(t)| ≤ 0.8 m/s²
|α(t)| ≤ 3.2 rad/s²
```

### 예측 지평
```
MPPI: T = N × Δt = 80 × 0.05 = 4.0초
TEB:  T ≈ 4.0초 (동적)
→ 예측 거리 d = 0.4 × 4.0 = 1.6m
```

### 안전 조건
```
min(||p_robot - p_obstacle||) ≥ 0.6m
```

---

## 🎯 실험 체크리스트

### 실험 전 확인사항
- [ ] 두 설정 파일의 속도/가속도 제한 동일 확인
- [ ] MPPI time_steps = 80 확인
- [ ] MPPI inflation_radius = 0.6 확인
- [ ] 동일한 초기 위치에서 시작
- [ ] 동일한 웨이포인트 사용

### 실험 중 기록사항
- [ ] rosbag 파일명에 플래너 이름 포함
- [ ] 시작 시간 및 종료 시간 기록
- [ ] 특이사항 메모 (충돌, 타임아웃 등)

### 실험 후 분석
- [ ] 각속도 그래프 비교 (PlotJuggler)
- [ ] 주행 시간 비교
- [ ] CPU/GPU 사용률 확인
- [ ] 성공률 계산

---

## 📈 예상 결과 비교

### TEB의 강점
- ✅ 정밀한 경로 추종
- ✅ 호모토피 경로 (여러 대안)
- ✅ 동적 장애물 대응

### MPPI의 강점
- ✅ 부드러운 제어 (샘플링 평균)
- ✅ GPU 병렬 처리 (빠른 계산)
- ✅ 확률적 안전성

### 측정 메트릭
| 메트릭 | 낮을수록 좋음 | 높을수록 좋음 |
|--------|------------|------------|
| 주행 시간 | ✅ | |
| 각속도 변화량 | ✅ | |
| 급가속 횟수 | ✅ | |
| 제어 주파수 | | ✅ |
| 경로 추종 정확도 | | ✅ |

---

## 🚀 빠른 실험 명령어

### TEB 실험
```bash
# Nav2 실행
ros2 launch cugo_ros2_control simulation_nav2.launch.py

# rosbag 기록
ros2 bag record -o teb_test /odom /cmd_vel /plan /local_plan

# 실험 시작
ros2 run cugo_ros2_control waypoint_navigator.py --scenario open_space
```

### MPPI 실험
```bash
# Nav2 실행 (MPPI 설정)
ros2 launch cugo_ros2_control simulation_nav2.launch.py \
  params_file:=$(ros2 pkg prefix cugo_ros2_control)/share/cugo_ros2_control/evaluation/configs/cugo_v3_mppi.yaml

# rosbag 기록
ros2 bag record -o mppi_test /odom /cmd_vel /plan /local_plan

# 실험 시작 (동일한 스크립트)
ros2 run cugo_ros2_control waypoint_navigator.py --scenario open_space
```

---

## 📚 참고 문서

- `PARAMETER_BASELINE.md`: 상세 수식 및 이론적 근거
- `COMPARISON_TABLE.md`: 전체 파라미터 비교표
- `README.md`: 실험 진행 가이드
- `configs/cugo_v3_teb.yaml`: TEB 설정 파일
- `configs/cugo_v3_mppi.yaml`: MPPI 설정 파일

---

## ⚡ 빠른 문제 해결

### MPPI 플러그인 없음
```bash
sudo apt install ros-humble-nav2-mppi-controller
```

### GPU 사용 확인
```bash
nvidia-smi  # GPU 사용률 확인
```

### rosbag 재생
```bash
ros2 bag play mppi_test
ros2 run plotjuggler plotjuggler  # 시각화
```

---

## ✅ 최종 확인

파라미터가 올바르게 설정되었는지 확인:

```bash
# TEB 설정 확인
grep -A2 "max_vel_x\|acc_lim_x\|inflation_dist" evaluation/configs/cugo_v3_teb.yaml

# MPPI 설정 확인
grep -A2 "vx_max\|ax_max\|inflation_radius\|time_steps" evaluation/configs/cugo_v3_mppi.yaml
```

예상 출력:
```
TEB:  max_vel_x: 0.4, acc_lim_x: 0.8, inflation_dist: 0.6
MPPI: vx_max: 0.4, ax_max: 0.8, inflation_radius: 0.6, time_steps: 80
```

