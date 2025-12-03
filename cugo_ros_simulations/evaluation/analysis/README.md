# Analysis - 데이터 분석

이 폴더는 TEB vs MPPI 비교 실험의 데이터 분석을 위한 Jupyter Notebook과 유틸리티를 포함합니다.

## 📂 파일 구조

```
analysis/
├── teb_vs_mppi_analysis.ipynb    # 메인 분석 노트북 (ALL-IN-ONE)
├── verify_parameters.py           # 파라미터 검증 스크립트
└── README.md                      # 이 파일
```

## 📊 `teb_vs_mppi_analysis.ipynb` - 메인 분석 노트북

모든 데이터 분석을 하나의 Jupyter Notebook에서 수행합니다.

### 노트북 구성

1. **실험 개요**
   - 실험 조건 및 목적
   - 데이터 수집 정보

2. **데이터 로드 및 전처리**
   - Rosbag → DataFrame 변환
   - IMU, Odom, Cmd_vel 데이터 추출
   - 시간 동기화 및 보간
   - 파생 변수 계산 (저크, 각가속도, 주행 거리)

3. **탐색적 데이터 분석 (EDA)**
   - 기술 통계량
   - 분포 확인 (히스토그램, Box plot)
   - 시계열 분석

4. **메트릭 계산**
   - 안정성 메트릭 (각속도 표준편차, 저크 등)
   - 효율성 메트릭 (주행 시간, 거리)
   - 정밀도 메트릭 (경로 추종 오차)

5. **통계 검정**
   - T-test (평균 차이 검정)
   - Cohen's d (효과 크기)
   - 신뢰구간

6. **시각화**
   - 시계열 그래프 (각속도, 속도, 가속도, 저크)
   - 비교 그래프 (Box plot, Radar chart, Bar chart)
   - 2D 궤적 시각화
   - 상관관계 히트맵

7. **결론 및 권장사항**
   - 정량적/정성적 결과 요약
   - 향후 연구 방향

## 🚀 사용 방법

### 1. Jupyter Notebook 실행

```bash
# Jupyter Lab 실행
cd ~/dev_ws/cugo_ws/src/rtc-teb_local_planner/cugo_ros_simulations/evaluation/analysis
jupyter lab teb_vs_mppi_analysis.ipynb

# 또는 Jupyter Notebook
jupyter notebook teb_vs_mppi_analysis.ipynb
```

### 2. 파라미터 검증

실험 전에 TEB와 MPPI 설정이 올바른지 확인:

```bash
cd ~/dev_ws/cugo_ws/src/rtc-teb_local_planner/cugo_ros_simulations/evaluation/analysis
python3 verify_parameters.py
```

## 📋 필요한 Python 패키지

```bash
pip install jupyter jupyterlab numpy pandas matplotlib seaborn scipy
```

## 💡 분석 팁

### 데이터 소스

- **IMU 데이터 우선**: 가속도/각속도는 `/imu/data_raw`에서 추출 (정확도 높음)
- **Odom 보조**: 위치/속도는 `/odom`에서 추출
- **시간 동기화**: IMU를 기준으로 다른 토픽 데이터 보간

### 주요 메트릭

- **안정성**: `angular_vel_std` (낮을수록 부드러움)
- **효율성**: `total_time`, `total_distance`
- **정밀도**: `goal_error`, `path_deviation`

### 그래프 우선순위

교수님께 보여드릴 핵심 그래프:
1. 각속도 시계열 비교 (가장 중요!)
2. Box plot 비교
3. 2D 궤적 시각화
4. Radar chart (종합 성능)
5. 메트릭 비교 표

## 🔄 데이터 흐름

```
1. Rosbag 수집
   ↓
   ../rosbags/teb/stage123_trial1/
   ../rosbags/mppi/stage123_trial1/
   
2. Jupyter Notebook에서 분석
   ↓
   teb_vs_mppi_analysis.ipynb
   
3. 모든 결과가 노트북 안에 저장
   - 그래프
   - 통계 결과
   - 결론
```

## 📝 노트북 실행 순서

1. **셀 순차 실행**: 위에서 아래로 모든 셀 실행
2. **데이터 확인**: 각 단계마다 데이터프레임 출력 확인
3. **그래프 저장**: 필요한 그래프는 `plt.savefig()` 사용
4. **결과 문서화**: 마크다운 셀에 인사이트 기록

## 🐛 문제 해결

### Rosbag 읽기 오류
```python
# sqlite3로 직접 읽기
import sqlite3
conn = sqlite3.connect('rosbag.db3')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
```

### IMU 토픽이 없을 때
```bash
# 토픽 확인
ros2 bag info ../rosbags/teb/stage123_trial1

# 대체: /odom에서 속도 미분하여 가속도 계산
```

### 메모리 부족
```python
# 데이터 다운샘플링
df_downsampled = df.iloc[::10]  # 10개 중 1개만 사용
```

## 📚 참고 자료

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Scipy Stats](https://docs.scipy.org/doc/scipy/reference/stats.html)

