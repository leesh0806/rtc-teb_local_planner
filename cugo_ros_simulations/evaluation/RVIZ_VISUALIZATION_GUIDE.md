# RViz2 시각화 가이드 - TEB vs MPPI

## 🎨 로컬 플래너 경로 시각화 설정

### 문제 상황
- **TEB**: 파란색 밴드 형태로 로컬 경로가 보임 ✅
- **MPPI**: 글로벌 경로만 보이고 로컬 경로가 안 보임 ❌

### 해결 방법

---

## 1️⃣ 설정 파일 수정 (완료 ✅)

### MPPI 시각화 활성화
```yaml
# cugo_v3_mppi.yaml
visualize: false → true  # ✅ 수정 완료
```

### TEB 시각화 강화
```yaml
# cugo_v3_teb.yaml
publish_feedback: false → true        # ✅ 수정 완료
visualize_hc_graph: false → true      # ✅ 수정 완료
```

---

## 2️⃣ RViz2에서 토픽 추가하기

### 📋 로컬 플래너 토픽 목록

| 플래너 | 토픽 이름 | 타입 | 설명 | 색상 추천 |
|--------|----------|------|------|----------|
| **공통** | `/local_plan` | Path | 로컬 플래너의 최종 경로 | 🔵 파란색 |
| **공통** | `/global_plan` | Path | 글로벌 플래너 경로 | 🟢 초록색 |
| **TEB** | `/teb_poses` | PoseArray | TEB 궤적 포즈들 | 🟣 보라색 |
| **TEB** | `/teb_markers` | MarkerArray | TEB 밴드 마커 | 🔵 파란색 |
| **TEB** | `/teb_feedback` | FeedbackMsg | TEB 피드백 정보 | - |
| **MPPI** | `/mppi/trajectories` | MarkerArray | MPPI 샘플링 궤적들 | 🌈 다양한 색 |
| **MPPI** | `/mppi/optimal_trajectory` | Path | 선택된 최적 궤적 | 🔴 빨간색 |

---

## 3️⃣ RViz2 설정 단계별 가이드

### Step 1: RViz2 실행 확인
```bash
# Nav2 실행 시 RViz2가 자동 실행됨
ros2 launch cugo_ros2_control simulation_nav2.launch.py
```

### Step 2: 로컬 경로 추가

#### 기본 로컬 경로 (필수)
1. RViz2 좌측 하단 **"Add"** 버튼 클릭
2. **"By topic"** 탭 선택
3. `/local_plan` 찾아서 **Path** 선택
4. **"OK"** 클릭
5. 좌측 패널에서 `/local_plan` 펼치기
6. **Color** 변경:
   - TEB: Blue (0, 0, 255)
   - MPPI: Red (255, 0, 0)
7. **Line Width**: 0.05로 설정

#### MPPI 샘플링 궤적 (선택)
1. **"Add"** → **"By topic"**
2. `/mppi/trajectories` (MarkerArray) 선택
3. 이것이 2000개의 샘플 궤적을 보여줍니다

#### TEB 밴드 마커 (선택)
1. **"Add"** → **"By topic"**
2. `/teb_markers` (MarkerArray) 선택
3. TEB의 탄성 밴드가 시각화됩니다

### Step 3: 시각화 확인
```bash
# 토픽이 발행되는지 확인
ros2 topic list | grep local_plan
ros2 topic list | grep mppi
ros2 topic list | grep teb

# 토픽 내용 확인
ros2 topic echo /local_plan --once
```

---

## 4️⃣ 토픽별 시각화 예시

### TEB 시각화 (파란색 밴드)
```
/local_plan          [Path]          - 최종 로컬 경로 (파란색 선)
/teb_poses           [PoseArray]     - 궤적 포즈들
/teb_markers         [MarkerArray]   - 밴드 마커
/teb_feedback        [FeedbackMsg]   - 피드백 정보
```

**RViz2에서 보이는 모습:**
- 파란색 곡선 경로 (부드러운 선)
- 포즈 화살표들 (선택적)
- 호모토피 그래프 (여러 경로 후보)

### MPPI 시각화 (샘플링 구름)
```
/local_plan               [Path]         - 최종 선택된 경로
/mppi/trajectories        [MarkerArray]  - 2000개 샘플 궤적
/mppi/optimal_trajectory  [Path]         - 최적 궤적
```

**RViz2에서 보이는 모습:**
- 빨간색 최적 경로
- 무지개색 샘플링 궤적 구름 (확률 분포)
- 시간에 따라 변하는 궤적들

---

## 5️⃣ RViz2 설정 저장

### 설정을 파일로 저장하기
1. RViz2 메뉴: **File** → **Save Config As...**
2. 파일명: `nav2_visualization_comparison.rviz`
3. 저장 위치: `cugo_ros_simulations/rviz/`

### 저장된 설정 사용하기
```bash
rviz2 -d ~/dev_ws/cugo_ws/src/rtc-teb_local_planner/cugo_ros_simulations/rviz/nav2_visualization_comparison.rviz
```

---

## 6️⃣ 시각화 트러블슈팅

### 문제 1: `/local_plan` 토픽이 보이지 않음

**원인:** Controller가 실행되지 않았거나 토픽이 발행되지 않음

**해결:**
```bash
# Controller 상태 확인
ros2 node list | grep controller

# 토픽 확인
ros2 topic list | grep plan

# Controller 재시작
ros2 lifecycle set /controller_server configure
ros2 lifecycle set /controller_server activate
```

### 문제 2: MPPI 샘플링 궤적이 너무 많아서 느림

**원인:** 2000개 궤적을 모두 시각화하면 RViz2가 느려질 수 있음

**해결:**
```yaml
# cugo_v3_mppi.yaml
visualize: true → false  # 시각화 끄기

# 또는 batch_size 줄이기 (GPU 사용 시)
batch_size: 2000 → 1000
```

### 문제 3: TEB 경로는 보이는데 색이 흐릿함

**원인:** Line Width가 너무 작음

**해결:**
1. RViz2 좌측 패널에서 `/local_plan` 펼치기
2. **Line Width**: 0.05 → 0.1로 증가
3. **Alpha**: 1.0 (완전 불투명)

### 문제 4: 경로가 끊겨서 보임

**원인:** 제어 주파수가 낮거나 경로 업데이트가 느림

**확인:**
```bash
# 토픽 발행 주파수 확인
ros2 topic hz /local_plan

# 예상: ~20 Hz (controller_frequency와 동일)
```

---

## 7️⃣ 비교 실험을 위한 권장 설정

### TEB 실험 시
```yaml
RViz2 Display:
- Global Plan: Green (0, 255, 0), Width: 0.03
- Local Plan:  Blue (0, 0, 255), Width: 0.08
- TEB Markers: Purple (128, 0, 128)
- Robot Model: Enabled
- Costmap:     Local + Global
```

### MPPI 실험 시
```yaml
RViz2 Display:
- Global Plan:           Green (0, 255, 0), Width: 0.03
- Local Plan:            Red (255, 0, 0), Width: 0.08
- MPPI Trajectories:     Rainbow (자동), Alpha: 0.3
- MPPI Optimal:          Cyan (0, 255, 255), Width: 0.1
- Robot Model:           Enabled
- Costmap:               Local + Global
```

### 동시 비교 시 (권장하지 않음)
- 한 번에 하나의 플래너만 실행
- 각각 따로 rosbag 기록하여 나중에 비교

---

## 8️⃣ 스크린샷 캡처 팁

### TEB vs MPPI 비교 영상 만들기

**Step 1: 화면 녹화**
```bash
# SimpleScreenRecorder 설치 (없으면)
sudo apt install simplescreenrecorder

# 또는 ROS2 기본 도구
ros2 run image_view video_recorder image:=/camera/image_raw
```

**Step 2: RViz2 스크린샷**
- RViz2 창 활성화
- `Ctrl + Shift + S` 또는
- **File** → **Save Screenshot**

**Step 3: 비교 이미지 생성**
```bash
# ImageMagick으로 나란히 배치
convert teb_screenshot.png mppi_screenshot.png +append comparison.png
```

---

## 9️⃣ 추천 RViz2 플러그인

### PlotJuggler와 통합
```bash
# PlotJuggler 실행
ros2 run plotjuggler plotjuggler

# 동시에 실시간 그래프 + RViz2 시각화
```

### RViz2 Video Recording
```bash
# rqt_bag으로 replay하면서 녹화
ros2 bag play teb_experiment.db3
# RViz2에서 재생되는 모습 녹화
```

---

## 🎯 최종 확인 체크리스트

### 설정 파일 확인
- [ ] `cugo_v3_teb.yaml`: `publish_feedback: true`
- [ ] `cugo_v3_teb.yaml`: `visualize_hc_graph: true`
- [ ] `cugo_v3_mppi.yaml`: `visualize: true`

### RViz2 확인
- [ ] `/local_plan` 토픽이 Display에 추가됨
- [ ] 색상이 구분되게 설정 (TEB: Blue, MPPI: Red)
- [ ] Line Width가 잘 보이도록 설정 (0.05~0.1)

### 실행 확인
- [ ] Nav2 controller가 활성화됨
- [ ] 로봇이 움직일 때 경로가 업데이트됨
- [ ] 토픽 발행 주파수가 정상 (~20 Hz)

---

## 🚀 빠른 명령어

```bash
# 토픽 확인
ros2 topic list | grep -E "(local_plan|global_plan|teb|mppi)"

# 토픽 시각화 확인
ros2 topic echo /local_plan --once

# Controller 상태 확인
ros2 lifecycle get /controller_server

# RViz2 재시작
killall rviz2
# (simulation_nav2.launch.py가 자동으로 재시작)
```

---

## 📚 추가 자료

- [Nav2 Visualization](https://navigation.ros.org/tutorials/docs/navigation2_with_rviz.html)
- [MPPI Controller](https://navigation.ros.org/configuration/packages/configuring-mppic.html)
- [TEB Local Planner](http://wiki.ros.org/teb_local_planner/Tutorials/Visualization)

---

**이제 TEB의 파란색 밴드처럼 MPPI의 빨간색 경로와 샘플링 구름을 볼 수 있습니다!** 🎨

