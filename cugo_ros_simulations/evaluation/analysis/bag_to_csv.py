#!/usr/bin/env python3
"""
ROS2 rosbag2 (.db3) → CSV 변환 스크립트

주요 토픽(/odom, /cmd_vel, /imu/data_raw, /local_plan, /global_plan, /amcl_pose)을
각각 별도의 CSV 파일로 저장합니다.

사용 예:
    python3 bag_to_csv.py \
        --bag-path ~/dev_ws/cugo_ws/src/rtc-teb_local_planner/cugo_ros_simulations/evaluation/rosbags/teb/stage123_trial1 \
        --output-dir ~/dev_ws/cugo_ws/src/rtc-teb_local_planner/cugo_ros_simulations/evaluation/rosbags/teb/stage123_trial1/csv

ROS 2 환경(예: `source /opt/ros/humble/setup.bash` 및 workspace setup.bash)을 먼저 설정해야 합니다.
"""

import argparse
import csv
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from rosidl_runtime_py.convert import message_to_ordereddict


DEFAULT_TOPICS = {
    "/odom",
    "/cmd_vel",
    "/imu/data_raw",
    "/local_plan",
    "/global_plan",
    "/amcl_pose",
}


def flatten_dict(
    data: Dict[str, Any],
    parent_key: str = "",
    sep: str = ".",
) -> Dict[str, Any]:
    """중첩 딕셔너리를 'a.b.c' 형태의 flat dict로 변환."""
    items: Dict[str, Any] = {}
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.update(flatten_dict(value, new_key, sep=sep))
        elif isinstance(value, (list, tuple)):
            # 리스트/배열은 인덱스로 풀어서 저장
            for i, v in enumerate(value):
                idx_key = f"{new_key}[{i}]"
                if isinstance(v, dict):
                    items.update(flatten_dict(v, idx_key, sep=sep))
                else:
                    items[idx_key] = v
        else:
            items[new_key] = value
    return items


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def open_bag_reader(bag_path: Path) -> Tuple[rosbag2_py.SequentialReader, Dict[int, Tuple[str, str]]]:
    """rosbag2 SequentialReader를 열고 connection_id → (topic_name, type) 매핑을 반환."""
    if bag_path.is_dir():
        uri = str(bag_path)
    else:
        # *.db3 파일이 주어졌다면 상위 디렉토리를 URI로 사용
        uri = str(bag_path.parent)

    storage_options = rosbag2_py.StorageOptions(uri=uri, storage_id="sqlite3")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topics = reader.get_all_topics_and_types()
    id_to_topic: Dict[int, Tuple[str, str]] = {}
    for info in topics:
        # rosbag2_py.TopicMetadata(id는 없고, reader.read_next()에서 topic_name만 내려오므로
        # 여기서는 name/type만 사용
        # 타입 문자열 예: "nav_msgs/msg/Odometry"
        pass

    return reader, {}  # id 매핑은 사용하지 않음


def convert_bag_to_csv(
    bag_path: Path,
    output_dir: Path,
    topics: Iterable[str] = (),
) -> None:
    topics = set(topics) if topics else set(DEFAULT_TOPICS)

    if bag_path.is_dir():
        uri = str(bag_path)
    else:
        uri = str(bag_path.parent)

    storage_options = rosbag2_py.StorageOptions(uri=uri, storage_id="sqlite3")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types: Dict[str, str] = {
        t.name: t.type for t in reader.get_all_topics_and_types()
    }

    # 선택된 토픽만 필터링
    selected_topic_types = {
        name: msg_type for name, msg_type in topic_types.items() if name in topics
    }

    if not selected_topic_types:
        raise RuntimeError(
            f"지정한 토픽들이 bag에 없습니다. 사용 가능한 토픽: {list(topic_types.keys())}"
        )

    ensure_output_dir(output_dir)

    # topic → (csv_writer, file_handle, header_written)
    writers: Dict[str, Tuple[csv.DictWriter, Any, bool]] = {}

    def get_writer(topic_name: str, fieldnames: Iterable[str]) -> csv.DictWriter:
        if topic_name in writers:
            return writers[topic_name][0]

        # 파일 이름에서 '/' 제거
        safe_name = topic_name.strip("/").replace("/", "_")
        csv_path = output_dir / f"{safe_name}.csv"
        f = csv_path.open("w", newline="")
        # timestamp(ns) 컬럼을 제일 앞으로
        field_list = ["timestamp"] + [fn for fn in fieldnames if fn != "timestamp"]
        writer = csv.DictWriter(f, fieldnames=field_list)
        writer.writeheader()
        writers[topic_name] = (writer, f, True)
        print(f"[INFO] Writing topic '{topic_name}' to {csv_path}")
        return writer

    try:
        # 메시지 타입 캐시
        type_cache: Dict[str, Any] = {}

        while reader.has_next():
            topic_name, data, t = reader.read_next()

            if topic_name not in selected_topic_types:
                continue

            msg_type_str = selected_topic_types[topic_name]

            if msg_type_str not in type_cache:
                # "nav_msgs/msg/Odometry" → 모듈/클래스 로드
                type_cache[msg_type_str] = get_message(msg_type_str)

            msg_type = type_cache[msg_type_str]
            msg = deserialize_message(data, msg_type)

            msg_dict = message_to_ordereddict(msg)
            flat = flatten_dict(msg_dict)

            # timestamp(ns) 추가 (ROS 시간 기준)
            flat["timestamp"] = t

            writer = get_writer(topic_name, flat.keys())
            writer.writerow(flat)

    finally:
        # 파일 핸들 닫기
        for _, (_, f, _) in writers.items():
            f.close()


def convert_bag_to_csv_combined(
    bag_path: Path,
    output_dir: Path,
    topics: Iterable[str] = (),
    filename: str = "combined.csv",
) -> None:
    """여러 토픽을 하나의 CSV 파일로 결합해서 저장."""
    topics = set(topics) if topics else set(DEFAULT_TOPICS)

    if bag_path.is_dir():
        uri = str(bag_path)
    else:
        uri = str(bag_path.parent)

    storage_options = rosbag2_py.StorageOptions(uri=uri, storage_id="sqlite3")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )

    # 1st pass: 필드 이름 수집
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types: Dict[str, str] = {
        t.name: t.type for t in reader.get_all_topics_and_types()
    }

    selected_topic_types = {
        name: msg_type for name, msg_type in topic_types.items() if name in topics
    }

    if not selected_topic_types:
        raise RuntimeError(
            f"지정한 토픽들이 bag에 없습니다. 사용 가능한 토픽: {list(topic_types.keys())}"
        )

    ensure_output_dir(output_dir)

    type_cache: Dict[str, Any] = {}
    all_fields: Dict[str, None] = {}

    while reader.has_next():
        topic_name, data, t = reader.read_next()
        if topic_name not in selected_topic_types:
            continue

        msg_type_str = selected_topic_types[topic_name]
        if msg_type_str not in type_cache:
            type_cache[msg_type_str] = get_message(msg_type_str)
        msg_type = type_cache[msg_type_str]

        msg = deserialize_message(data, msg_type)
        msg_dict = message_to_ordereddict(msg)
        flat = flatten_dict(msg_dict)

        for k in flat.keys():
            all_fields.setdefault(k, None)

    # 필드 리스트 구성
    fieldnames = ["timestamp", "topic"] + sorted(all_fields.keys())

    # 2nd pass: 실제 CSV 쓰기
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    csv_path = output_dir / filename
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        type_cache = {}

        while reader.has_next():
            topic_name, data, t = reader.read_next()
            if topic_name not in selected_topic_types:
                continue

            msg_type_str = selected_topic_types[topic_name]
            if msg_type_str not in type_cache:
                type_cache[msg_type_str] = get_message(msg_type_str)
            msg_type = type_cache[msg_type_str]

            msg = deserialize_message(data, msg_type)
            msg_dict = message_to_ordereddict(msg)
            flat = flatten_dict(msg_dict)

            row = {fn: "" for fn in fieldnames}
            row["timestamp"] = t
            row["topic"] = topic_name
            for k, v in flat.items():
                if k in row:
                    row[k] = v

            writer.writerow(row)

    print(f"[INFO] Combined CSV written to {csv_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ROS2 rosbag2 (.db3) → CSV 변환 도구",
    )
    parser.add_argument(
        "--bag-path",
        required=True,
        type=str,
        help="rosbag2 디렉토리 또는 .db3 파일 경로",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=str,
        help="CSV를 저장할 디렉토리",
    )
    parser.add_argument(
        "--topics",
        nargs="*",
        default=[],
        help=(
            "CSV로 변환할 토픽 리스트 (미지정 시 기본 세트 사용: "
            f"{', '.join(sorted(DEFAULT_TOPICS))})"
        ),
    )
    parser.add_argument(
        "--combined",
        action="store_true",
        help="여러 토픽을 하나의 combined CSV로 저장 (기본: 토픽별 개별 CSV)",
    )
    parser.add_argument(
        "--output-filename",
        type=str,
        default="combined.csv",
        help="출력 CSV 파일 이름 (--combined 옵션 사용 시, 기본: combined.csv)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bag_path = Path(os.path.expanduser(args.bag_path)).resolve()
    output_dir = Path(os.path.expanduser(args.output_dir)).resolve()

    if not bag_path.exists():
        raise FileNotFoundError(f"bag 경로가 존재하지 않습니다: {bag_path}")

    print(f"[INFO] Bag: {bag_path}")
    print(f"[INFO] Output dir: {output_dir}")
    topics = args.topics if args.topics else list(DEFAULT_TOPICS)
    print(f"[INFO] Topics: {topics}")

    if args.combined:
        convert_bag_to_csv_combined(bag_path, output_dir, topics, filename=args.output_filename)
    else:
        convert_bag_to_csv(bag_path, output_dir, topics)

    print("[INFO] 완료: CSV 변환이 끝났습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


