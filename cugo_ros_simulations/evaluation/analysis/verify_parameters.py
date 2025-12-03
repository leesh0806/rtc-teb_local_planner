#!/usr/bin/env python3
"""
パラメータ等価性検証スクリプト

TEBとMPPI設定ファイルのコアパラメータが正しく同一に設定されているかを検証します。

使用方法:
    python3 verify_parameters.py
"""

import yaml
from pathlib import Path
from typing import Dict, Any


class ParameterVerifier:
    """パラメータ等価性検証"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.teb_config = self.base_dir / 'configs' / 'cugo_v3_teb.yaml'
        self.mppi_config = self.base_dir / 'configs' / 'cugo_v3_mppi.yaml'
        
        self.errors = []
        self.warnings = []
        self.passed = []
    
    def load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """YAMLファイル読み込み"""
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    
    def check_velocity_constraints(self, teb_data: Dict, mppi_data: Dict):
        """速度制約検証"""
        print("\n🚗 速度制約検証中...")
        
        # 最大線速度
        teb_vx = teb_data['controller_server']['ros__parameters']['FollowPath']['max_vel_x']
        mppi_vx = mppi_data['controller_server']['ros__parameters']['FollowPath']['vx_max']
        
        if teb_vx == mppi_vx:
            self.passed.append(f"✅ 最大線速度: {teb_vx} m/s (同一)")
        else:
            self.errors.append(f"❌ 最大線速度不一致: TEB={teb_vx}, MPPI={mppi_vx}")
        
        # 最大角速度
        teb_w = teb_data['controller_server']['ros__parameters']['FollowPath']['max_vel_theta']
        mppi_w = mppi_data['controller_server']['ros__parameters']['FollowPath']['wz_max']
        
        if teb_w == mppi_w:
            self.passed.append(f"✅ 最大角速度: {teb_w} rad/s (同一)")
        else:
            self.errors.append(f"❌ 最大角速度不一致: TEB={teb_w}, MPPI={mppi_w}")
    
    def check_acceleration_constraints(self, teb_data: Dict, mppi_data: Dict):
        """加速度制約検証"""
        print("\n⚡ 加速度制約検証中...")
        
        # 最大線加速度
        teb_ax = teb_data['controller_server']['ros__parameters']['FollowPath']['acc_lim_x']
        mppi_ax = mppi_data['controller_server']['ros__parameters']['FollowPath']['ax_max']
        
        if teb_ax == mppi_ax:
            self.passed.append(f"✅ 最大線加速度: {teb_ax} m/s² (同一)")
        else:
            self.errors.append(f"❌ 最大線加速度不一致: TEB={teb_ax}, MPPI={mppi_ax}")
        
        # 最大角加速度
        teb_alpha = teb_data['controller_server']['ros__parameters']['FollowPath']['acc_lim_theta']
        mppi_alpha = mppi_data['controller_server']['ros__parameters']['FollowPath']['az_max']
        
        if teb_alpha == mppi_alpha:
            self.passed.append(f"✅ 最大角加速度: {teb_alpha} rad/s² (同一)")
        else:
            self.errors.append(f"❌ 最大角加速度不一致: TEB={teb_alpha}, MPPI={mppi_alpha}")
    
    def check_time_horizon(self, teb_data: Dict, mppi_data: Dict):
        """時間ホライズン検証"""
        print("\n⏱️  時間ホライズン検証中...")
        
        # MPPI予測時間計算
        time_steps = mppi_data['controller_server']['ros__parameters']['FollowPath']['time_steps']
        model_dt = mppi_data['controller_server']['ros__parameters']['FollowPath']['model_dt']
        mppi_horizon = time_steps * model_dt
        
        target_horizon = 4.0  # 目標予測時間
        
        if abs(mppi_horizon - target_horizon) < 0.1:
            self.passed.append(f"✅ MPPI予測時間: {mppi_horizon:.1f}秒 ({time_steps} × {model_dt})")
        else:
            self.warnings.append(
                f"⚠️  MPPI予測時間: {mppi_horizon:.1f}秒 (目標: {target_horizon}秒)"
            )
        
        # 予測距離計算
        vx_max = mppi_data['controller_server']['ros__parameters']['FollowPath']['vx_max']
        pred_distance = vx_max * mppi_horizon
        
        self.passed.append(f"✅ 予測距離: {pred_distance:.2f}m (= {vx_max} m/s × {mppi_horizon:.1f}s)")
    
    def check_safety_distance(self, teb_data: Dict, mppi_data: Dict):
        """安全距離検証"""
        print("\n🛡️  安全距離検証中...")
        
        # TEB inflation
        teb_inflation = teb_data['controller_server']['ros__parameters']['FollowPath']['inflation_dist']
        
        # MPPI inflation
        mppi_inflation = mppi_data['controller_server']['ros__parameters']['FollowPath']['CostCritic']['inflation_radius']
        
        if abs(teb_inflation - mppi_inflation) < 0.01:
            self.passed.append(f"✅ インフレーション距離: {teb_inflation}m (同一)")
        else:
            self.errors.append(
                f"❌ インフレーション距離不一致: TEB={teb_inflation}m, MPPI={mppi_inflation}m"
            )
    
    def check_control_frequency(self, teb_data: Dict, mppi_data: Dict):
        """制御周波数検証"""
        print("\n🕐 制御周波数検証中...")
        
        teb_freq = teb_data['controller_server']['ros__parameters']['controller_frequency']
        mppi_freq = mppi_data['controller_server']['ros__parameters']['controller_frequency']
        
        if teb_freq == mppi_freq:
            control_period = 1.0 / teb_freq
            self.passed.append(
                f"✅ 制御周波数: {teb_freq} Hz (周期: {control_period*1000:.0f}ms)"
            )
        else:
            self.errors.append(
                f"❌ 制御周波数不一致: TEB={teb_freq}, MPPI={mppi_freq}"
            )
    
    def check_goal_tolerance(self, teb_data: Dict, mppi_data: Dict):
        """目標許容誤差検証"""
        print("\n🎯 目標許容誤差検証中...")
        
        teb_xy = teb_data['controller_server']['ros__parameters']['general_goal_checker']['xy_goal_tolerance']
        mppi_xy = mppi_data['controller_server']['ros__parameters']['general_goal_checker']['xy_goal_tolerance']
        
        teb_yaw = teb_data['controller_server']['ros__parameters']['general_goal_checker']['yaw_goal_tolerance']
        mppi_yaw = mppi_data['controller_server']['ros__parameters']['general_goal_checker']['yaw_goal_tolerance']
        
        if teb_xy == mppi_xy:
            self.passed.append(f"✅ 位置許容誤差: {teb_xy}m (同一)")
        else:
            self.errors.append(f"❌ 位置許容誤差不一致: TEB={teb_xy}, MPPI={mppi_xy}")
        
        if teb_yaw == mppi_yaw:
            yaw_deg = teb_yaw * 57.3
            self.passed.append(f"✅ 方向許容誤差: {teb_yaw}rad ({yaw_deg:.1f}°) (同一)")
        else:
            self.errors.append(f"❌ 方向許容誤差不一致: TEB={teb_yaw}, MPPI={mppi_yaw}")
    
    def verify(self):
        """全体検証実行"""
        print("=" * 70)
        print("TEB vs MPPI パラメータ等価性検証")
        print("=" * 70)
        
        print(f"\n📂 設定ファイル:")
        print(f"  TEB:  {self.teb_config}")
        print(f"  MPPI: {self.mppi_config}")
        
        # YAML読み込み
        try:
            teb_data = self.load_yaml(self.teb_config)
            mppi_data = self.load_yaml(self.mppi_config)
        except Exception as e:
            print(f"\n❌ 設定ファイル読み込み失敗: {e}")
            return False
        
        # 各項目検証
        self.check_velocity_constraints(teb_data, mppi_data)
        self.check_acceleration_constraints(teb_data, mppi_data)
        self.check_time_horizon(teb_data, mppi_data)
        self.check_safety_distance(teb_data, mppi_data)
        self.check_control_frequency(teb_data, mppi_data)
        self.check_goal_tolerance(teb_data, mppi_data)
        
        # 結果出力
        print("\n" + "=" * 70)
        print("検証結果")
        print("=" * 70)
        
        if self.passed:
            print(f"\n✅ 合格 ({len(self.passed)}個):")
            for msg in self.passed:
                print(f"  {msg}")
        
        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}個):")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print(f"\n❌ エラー ({len(self.errors)}個):")
            for msg in self.errors:
                print(f"  {msg}")
        
        print("\n" + "=" * 70)
        
        if self.errors:
            print("❌ 検証失敗: パラメータを修正してください！")
            return False
        elif self.warnings:
            print("⚠️  検証完了: 警告事項を確認してください。")
            return True
        else:
            print("✅ 検証成功: すべてのパラメータが正しく設定されています！")
            return True
    
    def print_summary(self):
        """サマリー出力"""
        print("\n" + "=" * 70)
        print("📊 パラメータサマリー")
        print("=" * 70)
        
        teb_data = self.load_yaml(self.teb_config)
        mppi_data = self.load_yaml(self.mppi_config)
        
        teb_params = teb_data['controller_server']['ros__parameters']['FollowPath']
        mppi_params = mppi_data['controller_server']['ros__parameters']['FollowPath']
        
        print("\n速度/加速度制約:")
        print(f"  v_max = {mppi_params['vx_max']} m/s")
        print(f"  ω_max = {mppi_params['wz_max']} rad/s")
        print(f"  a_max = {mppi_params['ax_max']} m/s²")
        print(f"  α_max = {mppi_params['az_max']} rad/s²")
        
        print("\n予測ホライズン:")
        T = mppi_params['time_steps'] * mppi_params['model_dt']
        d = mppi_params['vx_max'] * T
        print(f"  T_pred = {T:.1f}s ({mppi_params['time_steps']} × {mppi_params['model_dt']}s)")
        print(f"  d_pred = {d:.2f}m")
        
        print("\n安全距離:")
        print(f"  d_infl = {mppi_params['CostCritic']['inflation_radius']}m")
        
        print("\n制御周波数:")
        freq = mppi_data['controller_server']['ros__parameters']['controller_frequency']
        print(f"  f = {freq} Hz ({1000/freq:.0f}ms)")
        
        print("\n" + "=" * 70)


def main():
    verifier = ParameterVerifier()
    success = verifier.verify()
    verifier.print_summary()
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())

