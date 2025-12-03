# TEB vs MPPI 파라미터 기준점 설정

## 📐 수식적 근거 및 동등성 분석

### 1. 속도 제약 (Velocity Constraints)

#### 선속도 (Linear Velocity)
```
로봇 최대 속도: v_max = 0.4 m/s
로봇 최소 속도: v_min = 0.0 m/s (정지 가능)
```

**TEB 설정:**
```yaml
max_vel_x: 0.4        # m/s
max_vel_x_backwards: 0.0  # 후진 불가 (묵시적)
```

**MPPI 설정:**
```yaml
vx_max: 0.4           # m/s
vx_min: -0.2          # m/s (후진 허용)
```

**동등 조건:**
```
TEB.max_vel_x = MPPI.vx_max = 0.4 m/s  ✅
```

#### 각속도 (Angular Velocity)
```
로봇 최대 각속도: ω_max = 1.0 rad/s = 57.3°/s
```

**TEB 설정:**
```yaml
max_vel_theta: 1.0    # rad/s
```

**MPPI 설정:**
```yaml
wz_max: 1.0           # rad/s
```

**동등 조건:**
```
TEB.max_vel_theta = MPPI.wz_max = 1.0 rad/s  ✅
```

---

### 2. 가속도 제약 (Acceleration Constraints)

#### 선가속도 (Linear Acceleration)
```
로봇 최대 가속도: a_max = 0.8 m/s²
감속도: a_min = -0.8 m/s²
```

**TEB 설정:**
```yaml
acc_lim_x: 0.8        # m/s²
```

**MPPI 설정:**
```yaml
ax_max: 0.8           # m/s²
ax_min: -0.8          # m/s²
```

**동등 조건:**
```
TEB.acc_lim_x = MPPI.ax_max = 0.8 m/s²  ✅
```

#### 각가속도 (Angular Acceleration)
```
로봇 최대 각가속도: α_max = 3.2 rad/s²
```

**TEB 설정:**
```yaml
acc_lim_theta: 3.2    # rad/s²
```

**MPPI 설정:**
```yaml
az_max: 3.2           # rad/s²
```

**동등 조건:**
```
TEB.acc_lim_theta = MPPI.az_max = 3.2 rad/s²  ✅
```

---

### 3. 시간 지평 (Time Horizon)

#### 예측 시간 계산

**TEB:**
```
예측 시간은 동적으로 조정되지만, 기본 시간 간격:
Δt = dt_ref = 0.3 s

TEB는 목표까지의 거리에 따라 자동으로 시간 지평 조정
실제 예측 시간: T_teb ≈ 3~5초 (일반적)
```

**MPPI:**
```
예측 시간 = time_steps × model_dt
T_mppi = N × Δt

기존: T_mppi = 56 × 0.05 = 2.8초  ← 너무 짧음!
```

**동등 조건:**
```
T_mppi ≈ T_teb ≈ 4.0초

∴ N = T / Δt = 4.0 / 0.05 = 80 steps

MPPI.time_steps = 80  ✅
MPPI.model_dt = 0.05
```

**근거:**
- 4초 예측 시간은 v_max = 0.4 m/s에서 1.6m 앞을 예측
- 로컬 플래너의 일반적인 예측 거리
- TEB의 평균 예측 거리와 유사

---

### 4. 장애물 안전 거리 (Obstacle Safety Distance)

#### TEB 장애물 회피
```yaml
min_obstacle_dist: 0.27     # 최소 장애물 거리
inflation_dist: 0.6         # 인플레이션 거리
```

**의미:**
```
d_safe = min_obstacle_dist = 0.27 m
d_inflation = 0.6 m

비용 함수:
C_obs(d) = {
  ∞           if d < d_safe
  k/(d-d_safe) if d_safe ≤ d < d_inflation
  0           if d ≥ d_inflation
}
```

#### MPPI 장애물 회피
```yaml
CostCritic:
  inflation_radius: 0.55    # 기존 값
  critical_cost: 300.0
```

**동등 조건:**
```
MPPI의 inflation_radius를 TEB의 inflation_dist와 동일하게:

MPPI.inflation_radius = TEB.inflation_dist = 0.6 m  ✅
```

---

### 5. 로봇 기하 (Robot Geometry)

#### 풋프린트 (Footprint)
```
로봇 크기:
  길이(x): 0.7 m (±0.35)
  폭(y): 0.5 m (±0.25)

풋프린트 좌표:
  [[ 0.35,  0.25],
   [ 0.35, -0.25],
   [-0.35, -0.25],
   [-0.35,  0.25]]
```

**TEB:**
```yaml
footprint_model:
  type: "polygon"
  vertices: "[[0.35, 0.25], [0.35, -0.25], [-0.35, -0.25], [-0.35, 0.25]]"
```

**MPPI:**
```
MPPI는 Costmap을 사용하므로 local_costmap의 footprint 사용
footprint: "[[0.35, 0.25], [0.35, -0.25], [-0.35, -0.25], [-0.35, 0.25]]"
```

**동등 조건:**
```
두 플래너 모두 동일한 풋프린트 사용  ✅
```

---

### 6. 목표 허용 오차 (Goal Tolerance)

```
위치 오차: xy_goal_tolerance = 0.25 m
방향 오차: yaw_goal_tolerance = 0.25 rad ≈ 14.3°
```

**TEB & MPPI (공통):**
```yaml
general_goal_checker:
  xy_goal_tolerance: 0.25
  yaw_goal_tolerance: 0.25
```

**동등 조건:**
```
동일한 goal_checker 사용  ✅
```

---

### 7. 제어 주파수 (Control Frequency)

```
제어 주파수: f = 20 Hz
제어 주기: T = 1/f = 0.05 s = 50 ms
```

**TEB & MPPI (공통):**
```yaml
controller_frequency: 20.0  # Hz
```

**동등 조건:**
```
동일한 제어 주파수  ✅
```

**근거:**
- 50ms는 Nav2의 표준 제어 주기
- TEB의 최적화와 MPPI의 샘플링 모두 처리 가능

---

### 8. 샘플링/반복 횟수 (Sampling & Iterations)

#### TEB 최적화
```yaml
no_inner_iterations: 5
no_outer_iterations: 4
```

**계산 부하:**
```
총 반복 횟수 = inner × outer = 5 × 4 = 20 iterations
각 반복마다 Jacobian 계산 및 QP 해결
```

#### MPPI 샘플링 (GPU 사용)
```yaml
batch_size: 2000          # 샘플 궤적 개수
iteration_count: 1        # MPPI는 보통 1회 반복
```

**계산 부하:**
```
GPU 병렬 처리로 2000개 궤적 동시 평가
각 궤적 = 80 time steps
총 평가 수 = 2000 × 80 = 160,000 poses/control cycle
```

**동등 조건:**
```
GPU 사용 시 batch_size는 높게 유지 (성능 활용)
MPPI.batch_size = 2000  ✅ (GPU 사용 시)
```

---

## 📊 최종 파라미터 비교 표

| 파라미터 | 물리적 의미 | TEB 설정 | MPPI 설정 | 동등성 |
|---------|------------|----------|-----------|-------|
| **속도 제약** |
| 최대 선속도 | v_max | `max_vel_x: 0.4` | `vx_max: 0.4` | ✅ |
| 최대 각속도 | ω_max | `max_vel_theta: 1.0` | `wz_max: 1.0` | ✅ |
| **가속도 제약** |
| 최대 선가속도 | a_max | `acc_lim_x: 0.8` | `ax_max: 0.8` | ✅ |
| 최대 각가속도 | α_max | `acc_lim_theta: 3.2` | `az_max: 3.2` | ✅ |
| **시간 지평** |
| 예측 시간 | T_pred | ~4.0초 (동적) | `80 × 0.05 = 4.0초` | ✅ |
| 시간 간격 | Δt | `dt_ref: 0.3` | `model_dt: 0.05` | ⚠️ 다름 (알고리즘 특성) |
| **안전 거리** |
| 장애물 인플레이션 | d_infl | `inflation_dist: 0.6` | `inflation_radius: 0.6` | ✅ |
| 최소 거리 | d_min | `min_obstacle_dist: 0.27` | (costmap 기반) | ⚠️ 다름 (구현 방식) |
| **로봇 기하** |
| 풋프린트 | - | polygon: 0.7×0.5m | 동일 | ✅ |
| **목표 정확도** |
| 위치 허용오차 | xy_tol | 0.25 m | 0.25 m | ✅ |
| 방향 허용오차 | θ_tol | 0.25 rad | 0.25 rad | ✅ |
| **제어 주파수** |
| 주파수 | f | 20 Hz | 20 Hz | ✅ |
| **계산 복잡도** |
| 최적화/샘플링 | - | 20 iterations | 2000 samples | - (알고리즘 다름) |

---

## 🎯 수정 요약

### MPPI 파라미터 수정 사항

```yaml
# 수정 전 → 수정 후

1. 시간 지평 확장
   time_steps: 56 → 80
   (2.8초 → 4.0초 예측)

2. 장애물 인플레이션 통일
   inflation_radius: 0.55 → 0.6
   (TEB와 동일하게)

3. GPU 활용 최적화
   batch_size: 2000 (유지)
   (GPU 병렬 처리 활용)
```

---

## 📐 핵심 동등성 수식

### 1. 속도 제약 동등성
```
∀ t: |v(t)| ≤ v_max = 0.4 m/s
∀ t: |ω(t)| ≤ ω_max = 1.0 rad/s
```

### 2. 가속도 제약 동등성
```
∀ t: |a(t)| ≤ a_max = 0.8 m/s²
∀ t: |α(t)| ≤ α_max = 3.2 rad/s²
```

### 3. 예측 거리 동등성
```
d_pred = v_max × T_pred = 0.4 × 4.0 = 1.6 m
```

### 4. 안전 거리 동등성
```
C_safety(d) > 0  when  d < d_infl = 0.6 m
```

---

## ✅ 결론

### 동일하게 설정된 제약 조건
1. ✅ 속도/가속도 제한 (로봇 물리 제약)
2. ✅ 예측 시간 지평 (~4초)
3. ✅ 장애물 안전 거리 (0.6m)
4. ✅ 로봇 기하학적 형상
5. ✅ 목표 도달 정확도
6. ✅ 제어 주파수 (20Hz)

### 알고리즘 고유 특성 (다를 수 있음)
- TEB: 시간 탄성 밴드 최적화
- MPPI: 샘플링 기반 MPC

### 공정한 비교 보장
이 설정으로 두 플래너는 동일한 물리적 제약 하에서 작동하며,
성능 차이는 순수하게 알고리즘의 특성에서 기인합니다.

